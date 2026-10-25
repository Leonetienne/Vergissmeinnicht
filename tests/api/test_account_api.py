from boards import services as s

from .conftest import refused


def test_search_scope_and_order(call, people, board, default_list):
    owner, editor, observer, stranger = people
    s.create_task(owner, default_list.id, "Buy garden seeds")
    archived = s.create_task(owner, default_list.id, "Garden hose", note="")
    s.transition_task(owner, archived.id, "done")
    s.transition_task(owner, archived.id, "archived")
    s.create_task(owner, default_list.id, "Other", note="for the GARDEN")
    s.create_board(owner, "Garden")
    s.create_board(stranger, "Garden secrets")
    data = call("search", observer, q="garden").data
    assert data["boards"] == []
    assert sorted(t["title"] for t in data["tasks"]) == ["Buy garden seeds", "Garden hose", "Other"]
    data = call("search", owner, q="garden").data
    assert [b["name"] for b in data["boards"]] == ["Garden"]
    assert {t["state"] for t in data["tasks"]} == {"open", "archived"}
    assert data["tasks"][0]["board"]["name"] == "Household"
    assert data["tasks"][0]["list"]["is_default"] is True
    assert call("search", owner, q="g").data == {"boards": [], "tasks": []}


def test_search_limit(call, people, default_list):
    owner = people[0]
    for i in range(60):
        s.create_task(owner, default_list.id, f"Item {i}")
    data = call("search", owner, q="item").data
    assert len(data["tasks"]) == 50


def test_profile(call, people):
    owner, editor = people[0], people[1]
    assert call("profile_get", owner).data["email"] == "owner@example.org"
    data = call("profile_update", owner, display_name="Leo", email="Leo@Example.org", reminders_enabled=False).data
    assert data == {"id": owner.id, "display_name": "Leo", "email": "leo@example.org", "reminders_enabled": False}
    refused(call("profile_update", owner, email="EDITOR@example.org"), 409)
    refused(call("profile_update", owner, email="not-an-email"), 400)
    refused(call("profile_update", owner, display_name=""), 400)
