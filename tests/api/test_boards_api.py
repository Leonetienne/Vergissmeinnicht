from accounts.models import User
from boards import services as s
from boards.models import Board, List, Share, Task

from .conftest import make_user, refused


def test_create_board_with_default_list(call, people):
    owner = people[0]
    result = call("board_create", owner, title="Garden", emoji="🌼")
    assert result.ok and result.data["title"] == "Garden" and result.data["role"] == "owner"
    board = Board.objects.get(pk=result.data["id"])
    assert list(board.lists.values_list("is_default", "title")) == [(True, "")]


def test_create_board_validation(call, people):
    refused(call("board_create", people[0], title="  "), 400)
    refused(call("board_create", people[0], title="x" * 101), 400)
    refused(call("board_create", people[0]), 400)


def test_boards_list_sections(call, people, board):
    owner, editor, observer, _ = people
    s.create_board(editor, "Zeta")
    data = call("boards_list", editor).data
    assert [b["title"] for b in data["own"]] == ["Zeta"]
    assert data["shared"][0]["title"] == "Household"
    assert data["shared"][0]["role"] == "editor"
    assert data["shared"][0]["owner"]["display_name"] == "Leon"


def test_shared_sorted_alphabetically(call, people):
    owner, editor = people[0], people[1]
    for name in ["beta", "Alpha", "gamma"]:
        b = s.create_board(owner, name)
        s.add_share(owner, b.id, editor.id)
    assert [b["title"] for b in call("boards_list", editor).data["shared"]] == ["Alpha", "beta", "gamma"]


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
    assert call("board_update", owner, board_id=board.id, title="Home", emoji="🏡").data["url"] == "/leon/home/"
    refused(call("board_update", editor, board_id=board.id, title="X"), 403)
    refused(call("board_update", observer, board_id=board.id, emoji="🌼"), 403)
    refused(call("board_update", stranger, board_id=board.id, title="X"), 404)
    refused(call("board_update", owner, board_id=board.id, emoji="abc"), 400)
    assert Board.objects.get(pk=board.id).title == "Home"


def test_starter_boards(db):
    user = User.objects.create_user("new@example.org", "pw1", display_name="New")
    assert list(Board.objects.filter(owner=user).values_list("title", "emoji", "slug")) == [
        ("My Todos", "🧹", "my-todos"), ("Shopping List", "🛒", "shopping-list")]
    assert all(b.lists.filter(is_default=True).count() == 1 for b in Board.objects.filter(owner=user))


def test_board_slugs_unique_per_owner(call, people):
    owner, editor = people[0], people[1]
    first = call("board_create", owner, title="My tasks").data
    second = call("board_create", owner, title="My tasks?").data
    third = call("board_create", owner, title="My Tasks!").data
    assert (first["url"], second["url"], third["url"]) == ("/leon/my-tasks/", "/leon/my-tasks-1/", "/leon/my-tasks-2/")
    assert call("board_create", editor, title="My tasks").data["url"] == "/mara-lind/my-tasks/"
    assert call("board_update", owner, board_id=first["id"], title="My tasks").data["url"] == "/leon/my-tasks/"
    assert call("board_update", owner, board_id=second["id"], title="Groceries").data["url"] == "/leon/groceries/"
    assert call("board_create", owner, title="🌼").data["url"] == "/leon/board/"


def test_board_titles_unique_per_owner(call, people, board):
    owner, editor = people[0], people[1]
    other = s.create_board(owner, "Garden")
    refused(call("board_create", owner, title="Household"), 409)
    refused(call("board_create", owner, title=" household "), 409)
    refused(call("board_update", owner, board_id=other.id, title="HOUSEHOLD"), 409)
    assert call("board_update", owner, board_id=board.id, title="household").data["title"] == "household"
    assert call("board_create", editor, title="Household").ok


def test_usernames_unique_and_not_reserved(db):
    assert make_user("a@example.org", "Leon").username == "leon"
    assert make_user("b@example.org", "Léon").username == "leon-1"
    assert make_user("c@example.org", "Settings").username == "settings-1"
    assert make_user("d@example.org", "🌼").username == "user"


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
