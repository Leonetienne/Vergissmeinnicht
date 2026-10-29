from boards import services as s
from boards.models import List, Task

from .conftest import refused


def positions(board):
    return list(List.objects.filter(board=board).order_by("position").values_list("title", "position"))


def test_create_list_at_end(call, people, board):
    owner, editor, observer, stranger = people
    assert call("list_create", editor, board_id=board.id, title="Groceries").data["position"] == 1
    assert call("list_create", owner, board_id=board.id, title="Later").data["position"] == 2
    refused(call("list_create", observer, board_id=board.id, title="X"), 403)
    refused(call("list_create", stranger, board_id=board.id, title="X"), 404)
    refused(call("list_create", owner, board_id=board.id, title=""), 400)
    refused(call("list_create", owner, board_id=board.id, title="x" * 101), 400)


def test_create_list_never_before_default(call, people, board):
    data = call("list_create", people[0], board_id=board.id, title="A", position=0).data
    assert data["position"] == 1
    assert positions(board)[0] == ("", 0)


def test_rename_list(call, people, board, default_list):
    owner, editor, observer, _ = people
    lst = s.create_list(owner, board.id, "A")
    assert call("list_update", editor, list_id=lst.id, title="B").data["title"] == "B"
    refused(call("list_update", observer, list_id=lst.id, title="C"), 403)
    refused(call("list_update", owner, list_id=default_list.id, title="C"), 400)


def test_list_colour(call, people, board, default_list):
    owner, editor, observer, _ = people
    lst = s.create_list(owner, board.id, "A")
    assert call("list_get", owner, list_id=lst.id).data["colour"] == "none"
    data = call("list_update", editor, list_id=lst.id, colour="green").data
    assert data["colour"] == "green" and data["title"] == "A"
    assert call("list_update", owner, list_id=lst.id, title="B").data["colour"] == "green"
    refused(call("list_update", owner, list_id=lst.id, colour="pink"), 400)
    refused(call("list_update", observer, list_id=lst.id, colour="red"), 403)
    refused(call("list_update", owner, list_id=default_list.id, colour="red"), 400)
    assert call("list_create", owner, board_id=board.id, title="C", colour="blue").data["colour"] == "blue"


def test_list_titles_unique_per_board(call, people, board):
    owner = people[0]
    a = s.create_list(owner, board.id, "Groceries")
    b = s.create_list(owner, board.id, "Later")
    refused(call("list_create", owner, board_id=board.id, title="Groceries"), 409)
    refused(call("list_create", owner, board_id=board.id, title=" groceries "), 409)
    refused(call("list_update", owner, list_id=b.id, title="GROCERIES"), 409)
    assert call("list_update", owner, list_id=a.id, title="groceries").data["title"] == "groceries"
    other = s.create_board(owner, "Other")
    assert call("list_create", owner, board_id=other.id, title="Groceries").ok


def test_move_list(call, people, board, default_list):
    owner = people[0]
    a, b, c = (s.create_list(owner, board.id, n) for n in "ABC")
    assert call("list_move", owner, list_id=c.id, position=1).ok
    assert positions(board) == [("", 0), ("C", 1), ("A", 2), ("B", 3)]
    assert call("list_move", owner, list_id=c.id, position=0).ok
    assert positions(board)[0] == ("", 0)
    refused(call("list_move", owner, list_id=default_list.id, position=2), 400)
    refused(call("list_move", people[2], list_id=a.id, position=2), 403)


def test_delete_list_moves_tasks_to_default_end(call, people, board, default_list):
    owner, editor, observer, _ = people
    s.create_task(owner, default_list.id, "D1")
    lst = s.create_list(owner, board.id, "Groceries")
    a = s.create_task(owner, lst.id, "A")
    b = s.create_task(owner, lst.id, "B")
    c = s.create_task(owner, lst.id, "C")
    s.transition_task(owner, b.id, "done")
    s.transition_task(owner, b.id, "archived")
    refused(call("list_delete", observer, list_id=lst.id), 403)
    result = call("list_delete", editor, list_id=lst.id)
    assert [t["title"] for t in result.data["moved"]] == ["A", "B", "C"]
    assert list(Task.objects.filter(list=default_list).order_by("position").values_list("title", "position")) == [
        ("D1", 0), ("A", 1), ("B", 2), ("C", 3)]
    assert not List.objects.filter(pk=lst.id).exists()
    refused(call("list_delete", owner, list_id=default_list.id), 400)


def test_list_get_orders_by_state_then_position(call, people, board, default_list):
    owner = people[0]
    a = s.create_task(owner, default_list.id, "A")
    s.create_task(owner, default_list.id, "B")
    s.transition_task(owner, a.id, "done")
    data = call("list_get", people[2], list_id=default_list.id).data
    assert [t["title"] for t in data["tasks"]] == ["B", "A"]
    refused(call("list_get", people[3], list_id=default_list.id), 404)
