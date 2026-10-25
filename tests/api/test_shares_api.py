from boards import services as s
from boards.models import Share

from .conftest import make_user, refused


def test_shares_list_owner_only(call, people, board):
    owner, editor, observer, _ = people
    data = call("shares_list", owner, board_id=board.id).data
    assert {(sh["user"]["email"], sh["role"]) for sh in data} == {
        ("editor@example.org", "editor"), ("observer@example.org", "observer")}
    refused(call("shares_list", editor, board_id=board.id), 403)


def test_candidates(call, people, board):
    owner, editor, observer, stranger = people
    for i in range(12):
        make_user(f"cand{i}@example.org", f"Candidate {i}")
    assert call("share_candidates", owner, board_id=board.id, q="ca").data == []
    names = [u["display_name"] for u in call("share_candidates", owner, board_id=board.id, q="CANDI").data]
    assert len(names) == 10
    emails = [u["email"] for u in call("share_candidates", owner, board_id=board.id, q="example.org").data]
    assert "owner@example.org" not in emails and "editor@example.org" not in emails
    refused(call("share_candidates", editor, board_id=board.id, q="cand"), 403)


def test_add_share(call, people, board):
    owner, editor, observer, stranger = people
    data = call("share_add", owner, board_id=board.id, user_id=stranger.id).data
    assert data["role"] == "observer" and data["user"]["id"] == stranger.id
    refused(call("share_add", owner, board_id=board.id, user_id=stranger.id), 409)
    refused(call("share_add", owner, board_id=board.id, user_id=owner.id), 400)
    refused(call("share_add", owner, board_id=board.id, user_id=99999), 404)
    refused(call("share_add", owner, board_id=board.id, user_id=stranger.id, role="admin"), 400)
    refused(call("share_add", editor, board_id=board.id, user_id=stranger.id), 403)


def test_role_change_applies_next_request(call, people, board, default_list):
    owner, _, observer, _ = people
    share = Share.objects.get(user=observer)
    refused(call("task_create", observer, list_id=default_list.id, title="A"), 403)
    assert call("share_update", owner, share_id=share.id, role="editor").data["role"] == "editor"
    assert call("task_create", observer, list_id=default_list.id, title="A").ok
    refused(call("share_update", observer, share_id=share.id, role="observer"), 403)


def test_remove_share(call, people, board):
    owner, editor = people[0], people[1]
    share = Share.objects.get(user=editor)
    refused(call("share_remove", editor, share_id=share.id), 403)
    assert call("share_remove", owner, share_id=share.id).ok
    refused(call("board_get", editor, board_id=board.id), 404)
    refused(call("share_remove", owner, share_id=share.id), 404)
