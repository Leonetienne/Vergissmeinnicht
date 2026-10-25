from boards import services as s
from boards.models import Board, List, Share, Task

from .conftest import make_user, refused


def test_create_board_with_default_list(call, people):
    owner = people[0]
    result = call("board_create", owner, name="Garden", emoji="🌼")
    assert result.ok and result.data["name"] == "Garden" and result.data["role"] == "owner"
    board = Board.objects.get(pk=result.data["id"])
    assert list(board.lists.values_list("is_default", "title")) == [(True, "")]


def test_create_board_validation(call, people):
    refused(call("board_create", people[0], name="  "), 400)
    refused(call("board_create", people[0], name="x" * 101), 400)
    refused(call("board_create", people[0]), 400)


def test_boards_list_sections(call, people, board):
    owner, editor, observer, _ = people
    s.create_board(editor, "Zeta")
    data = call("boards_list", editor).data
    assert [b["name"] for b in data["own"]] == ["Zeta"]
    assert data["shared"][0]["name"] == "Household"
    assert data["shared"][0]["role"] == "editor"
    assert data["shared"][0]["owner"]["display_name"] == "Leon"


def test_shared_sorted_alphabetically(call, people):
    owner, editor = people[0], people[1]
    for name in ["beta", "Alpha", "gamma"]:
        b = s.create_board(owner, name)
        s.add_share(owner, b.id, editor.id)
    assert [b["name"] for b in call("boards_list", editor).data["shared"]] == ["Alpha", "beta", "gamma"]


def test_board_get_includes_every_state(call, people, board, default_list):
    owner = people[0]
    t = s.create_task(owner, default_list.id, "A")
    s.transition_task(owner, t.id, "done")
    s.transition_task(owner, t.id, "archived")
    s.create_task(owner, default_list.id, "B")
    data = call("board_get", people[2], board_id=board.id).data
    assert [(t["title"], t["state"]) for t in data["lists"][0]["tasks"]] == [("B", "open"), ("A", "archived")]


def test_board_get_hidden_from_strangers(call, people, board):
    refused(call("board_get", people[3], board_id=board.id), 404)
    refused(call("board_get", people[0], board_id=99999), 404)


def test_update_board_owner_only(call, people, board):
    owner, editor, observer, stranger = people
    assert call("board_update", owner, board_id=board.id, name="Home", emoji="🏡").data["url"] == f"/{board.id}-home/"
    refused(call("board_update", editor, board_id=board.id, name="X"), 403)
    refused(call("board_update", observer, board_id=board.id, emoji="🌼"), 403)
    refused(call("board_update", stranger, board_id=board.id, name="X"), 404)
    refused(call("board_update", owner, board_id=board.id, emoji="abc"), 400)
    assert Board.objects.get(pk=board.id).name == "Home"


def test_move_board_keeps_positions_gapless(call, people):
    owner = people[0]
    ids = [s.create_board(owner, n).id for n in "ABCD"]
    assert call("board_move", owner, board_id=ids[3], position=0).ok
    assert list(Board.objects.filter(owner=owner).values_list("id", "position")) == [
        (ids[3], 0), (ids[0], 1), (ids[1], 2), (ids[2], 3)]


def test_move_board_of_others_refused(call, people, board):
    refused(call("board_move", people[1], board_id=board.id, position=0), 403)


def test_delete_board_cascades(call, people, board, default_list):
    owner, editor = people[0], people[1]
    s.create_task(owner, default_list.id, "A")
    refused(call("board_delete", editor, board_id=board.id), 403)
    assert call("board_delete", owner, board_id=board.id).ok
    assert not Board.objects.exists() and not List.objects.exists()
    assert not Task.objects.exists() and not Share.objects.exists()


def test_create_board_appends_after_delete(call, people):
    owner = people[0]
    a, b, c = (s.create_board(owner, n) for n in "ABC")
    call("board_delete", owner, board_id=b.id)
    assert list(Board.objects.filter(owner=owner).values_list("position", flat=True)) == [0, 1]


def test_leave_board(call, people, board):
    owner, editor, observer, stranger = people
    assert call("board_leave", observer, board_id=board.id).ok
    assert not Share.objects.filter(user=observer).exists()
    refused(call("board_leave", owner, board_id=board.id), 400)
    refused(call("board_leave", stranger, board_id=board.id), 404)


def test_archive_done_and_archive(call, people, board, default_list):
    owner, editor, observer, _ = people
    a = s.create_task(owner, default_list.id, "A")
    b = s.create_task(owner, default_list.id, "B")
    s.transition_task(owner, a.id, "done")
    refused(call("board_archive_done", observer, board_id=board.id), 403)
    result = call("board_archive_done", editor, board_id=board.id)
    assert result.data == {"task_ids": [a.id]}
    archive = call("board_archive", observer, board_id=board.id).data
    assert [t["id"] for t in archive["lists"][0]["tasks"]] == [a.id]
    assert Task.objects.get(pk=b.id).state == "open"
    refused(call("board_archive", people[3], board_id=board.id), 404)


def test_ownership_of_content(call, people, board, default_list):
    editor = people[1]
    task = call("task_create", editor, list_id=default_list.id, title="By editor").data
    assert Task.objects.get(pk=task["id"]).list.board.owner == people[0]
    make_user("x@example.org")
