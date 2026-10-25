from datetime import date

from boards import services as s
from boards.models import Task

from .conftest import refused


def seq(lst):
    return list(Task.objects.filter(list=lst).order_by("position").values_list("title", flat=True))


def test_create_task(call, people, default_list):
    owner, editor, observer, stranger = people
    result = call("task_create", editor, list_id=default_list.id, title="Seeds")
    assert result.data["state"] == "open" and result.data["colour"] == "none" and result.data["position"] == 0
    refused(call("task_create", observer, list_id=default_list.id, title="X"), 403)
    refused(call("task_create", stranger, list_id=default_list.id, title="X"), 404)
    refused(call("task_create", owner, list_id=default_list.id, title=""), 400)
    refused(call("task_create", owner, list_id=default_list.id, title="x" * 201), 400)
    refused(call("task_create", owner, list_id=default_list.id, title="X", colour="pink"), 400)
    refused(call("task_create", owner, list_id=default_list.id, title="X", note="x" * 5001), 400)


def test_create_task_restores_full_state(call, people, default_list):
    owner = people[0]
    s.create_task(owner, default_list.id, "A")
    s.create_task(owner, default_list.id, "B")
    data = call("task_create", owner, list_id=default_list.id, title="R", position=1, state="archived",
                due_date="2026-03-14", colour="blue", note="n").data
    assert data["position"] == 1 and data["state"] == "archived" and data["due_date"] == "2026-03-14"
    assert seq(default_list) == ["A", "R", "B"]


def test_update_task(call, people, default_list):
    owner, editor, observer, _ = people
    task = s.create_task(owner, default_list.id, "A")
    data = call("task_update", editor, task_id=task.id, title="B", due_date="2026-03-14", colour="green", note="x").data
    assert (data["title"], data["due_date"], data["colour"], data["note"]) == ("B", "2026-03-14", "green", "x")
    assert call("task_update", owner, task_id=task.id, due_date=None).data["due_date"] is None
    refused(call("task_update", observer, task_id=task.id, title="C"), 403)
    refused(call("task_update", owner, task_id=task.id, due_date="14.03.2026"), 400)
    refused(call("task_update", owner, task_id=task.id, title=" "), 400)


def test_due_change_resets_reminders(people, default_list):
    owner = people[0]
    task = s.create_task(owner, default_list.id, "A", due_date=date(2026, 3, 14))
    Task.objects.filter(pk=task.id).update(reminded_soon=True, reminded_due=True)
    s.update_task(owner, task.id, due_date=date(2026, 3, 20))
    task.refresh_from_db()
    assert not task.reminded_soon and not task.reminded_due


def test_transition(call, people, default_list):
    owner, editor, observer, _ = people
    task = s.create_task(owner, default_list.id, "A")
    refused(call("task_transition", owner, task_id=task.id, state="archived"), 409)
    assert call("task_transition", editor, task_id=task.id, state="done").data["state"] == "done"
    assert call("task_transition", editor, task_id=task.id, state="archived").data["state"] == "archived"
    refused(call("task_transition", owner, task_id=task.id, state="open"), 409)
    refused(call("task_transition", observer, task_id=task.id, state="done"), 403)
    refused(call("task_transition", owner, task_id=task.id, state="gone"), 400)


def test_bulk_transition_is_atomic(call, people, default_list):
    owner = people[0]
    a = s.create_task(owner, default_list.id, "A")
    b = s.create_task(owner, default_list.id, "B")
    s.transition_task(owner, a.id, "done")
    refused(call("tasks_transition", owner, task_ids=[a.id, b.id], state="archived"), 409)
    assert Task.objects.get(pk=a.id).state == "done"
    assert [t["state"] for t in call("tasks_transition", owner, task_ids=[a.id], state="archived").data] == ["archived"]
    refused(call("tasks_transition", people[2], task_ids=[a.id], state="done"), 403)


def test_move_within_list(call, people, default_list):
    owner = people[0]
    a, b, c = (s.create_task(owner, default_list.id, n) for n in "ABC")
    assert call("task_move", owner, task_id=a.id, list_id=default_list.id, position=2).ok
    assert seq(default_list) == ["B", "C", "A"]
    assert call("task_move", owner, task_id=a.id, list_id=default_list.id, position=0).ok
    assert seq(default_list) == ["A", "B", "C"]


def test_move_between_lists_gapless(call, people, board, default_list):
    owner, editor = people[0], people[1]
    other = s.create_list(owner, board.id, "Other")
    a, b, c = (s.create_task(owner, default_list.id, n) for n in "ABC")
    x = s.create_task(owner, other.id, "X")
    assert call("task_move", editor, task_id=b.id, list_id=other.id, position=0).data["list_id"] == other.id
    assert list(Task.objects.filter(list=default_list).order_by("position").values_list("title", "position")) == [("A", 0), ("C", 1)]
    assert list(Task.objects.filter(list=other).order_by("position").values_list("title", "position")) == [("B", 0), ("X", 1)]


def test_move_to_other_board_refused(call, people, default_list):
    owner = people[0]
    task = s.create_task(owner, default_list.id, "A")
    other = s.create_board(owner, "Other").lists.get()
    refused(call("task_move", owner, task_id=task.id, list_id=other.id, position=0), 400)


def test_move_refused_for_observer(call, people, default_list):
    task = s.create_task(people[0], default_list.id, "A")
    refused(call("task_move", people[2], task_id=task.id, list_id=default_list.id, position=0), 403)


def test_bulk_move(call, people, board, default_list):
    owner = people[0]
    other = s.create_list(owner, board.id, "Other")
    a, b = (s.create_task(owner, default_list.id, n) for n in "AB")
    moves = [{"task_id": a.id, "list_id": other.id, "position": 0}, {"task_id": b.id, "list_id": other.id, "position": 1}]
    assert len(call("tasks_move", owner, moves=moves).data) == 2
    assert seq(other) == ["A", "B"]
    refused(call("tasks_move", owner, moves=[{"task_id": a.id}]), 400)


def test_bulk_move_atomic(call, people, board, default_list):
    owner = people[0]
    a = s.create_task(owner, default_list.id, "A")
    foreign = s.create_board(people[3], "Foreign").lists.get()
    moves = [{"task_id": a.id, "list_id": default_list.id, "position": 0},
             {"task_id": a.id, "list_id": foreign.id, "position": 0}]
    refused(call("tasks_move", owner, moves=moves), 404)


def test_delete_task_renumbers(call, people, default_list):
    owner, editor, observer, _ = people
    a, b, c = (s.create_task(owner, default_list.id, n) for n in "ABC")
    refused(call("task_delete", observer, task_id=b.id), 403)
    assert call("task_delete", editor, task_id=b.id).ok
    assert list(Task.objects.filter(list=default_list).order_by("position").values_list("position", flat=True)) == [0, 1]
    refused(call("task_get", owner, task_id=b.id), 404)


def test_task_get(call, people, default_list):
    task = s.create_task(people[0], default_list.id, "A")
    assert call("task_get", people[2], task_id=task.id).data["title"] == "A"
    refused(call("task_get", people[3], task_id=task.id), 404)
