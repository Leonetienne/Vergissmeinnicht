from boards import services as s
from boards.models import Task
from boards.serializers import task_data

from ..registry import DATE, ID, POSITION, READ, WRITE, operation

TITLE = {"type": "string", "description": "1 to 200 characters"}
STATE = {"type": "string", "enum": Task.STATES}
COLOUR = {"type": "string", "enum": Task.COLOURS}
NOTE = {"type": "string", "description": "Plain text, up to 5000 characters"}
TASK_POSITION = {**POSITION, "description": "0-based position in the list's task sequence, all states included"}


@operation("task_get", access=READ, method="GET", path="tasks/{task_id}/",
           description="Get a task. Same JSON as the task export.",
           params={"task_id": ID}, required=["task_id"])
def task_get(user, task_id):
    return task_data(s.get_task(user, task_id))


@operation("task_create", access=WRITE, method="POST", path="lists/{list_id}/tasks/",
           description="Create a task, by default open and at the end of the list.",
           params={"list_id": ID, "title": TITLE, "position": TASK_POSITION, "state": STATE,
                   "due_date": DATE, "colour": COLOUR, "note": NOTE},
           required=["list_id", "title"])
def task_create(user, list_id, **args):
    return task_data(s.create_task(user, list_id, **args))


@operation("task_update", access=WRITE, method="PATCH", path="tasks/{task_id}/",
           description="Change title, due date, colour or note of a task.",
           params={"task_id": ID, "title": TITLE, "due_date": DATE, "colour": COLOUR, "note": NOTE},
           required=["task_id"])
def task_update(user, task_id, **args):
    return task_data(s.update_task(user, task_id, **args))


@operation("task_transition", access=WRITE, method="POST", path="tasks/{task_id}/transition/",
           description="Change a task's state: open <-> done <-> archived, one step at a time (409 otherwise).",
           params={"task_id": ID, "state": STATE}, required=["task_id", "state"])
def task_transition(user, task_id, state):
    return task_data(s.transition_task(user, task_id, state))


@operation("tasks_transition", access=WRITE, method="POST", path="tasks/transition/",
           description="Change the state of several tasks at once, atomically.",
           params={"task_ids": {"type": "array", "items": ID}, "state": STATE},
           required=["task_ids", "state"])
def tasks_transition(user, task_ids, state):
    return [task_data(t) for t in s.transition_tasks(user, task_ids, state)]


@operation("task_move", access=WRITE, method="POST", path="tasks/{task_id}/move/",
           description="Move a task to a list of the same board and a position in that list.",
           params={"task_id": ID, "list_id": ID, "position": TASK_POSITION},
           required=["task_id", "list_id", "position"])
def task_move(user, task_id, list_id, position):
    return task_data(s.move_task(user, task_id, list_id, position))


MOVE = {"type": "object", "properties": {"task_id": ID, "list_id": ID, "position": TASK_POSITION},
        "required": ["task_id", "list_id", "position"]}


@operation("tasks_move", access=WRITE, method="POST", path="tasks/move/",
           description="Apply several task moves in order, atomically.",
           params={"moves": {"type": "array", "items": MOVE}}, required=["moves"])
def tasks_move(user, moves):
    return [task_data(t) for t in s.move_tasks(user, moves)]


@operation("task_delete", access=WRITE, method="DELETE", path="tasks/{task_id}/",
           description="Delete a task.",
           params={"task_id": ID}, required=["task_id"], destructive=True)
def task_delete(user, task_id):
    s.delete_task(user, task_id)
    return {"deleted": task_id}
