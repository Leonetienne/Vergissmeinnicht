from boards import services as s
from boards.models import Task
from boards.serializers import list_data, task_data

from ..registry import ID, POSITION, READ, WRITE, operation

TITLE = {"type": "string", "description": "1 to 100 characters"}


@operation("list_get", access=READ, method="GET", path="lists/{list_id}/",
           description="Get a list with all its tasks of every state. Same JSON as the list export.",
           params={"list_id": ID}, required=["list_id"])
def list_get(user, list_id):
    lst = s.get_list(user, list_id)
    return list_data(lst, s.ordered_tasks(Task.objects.filter(list=lst)))


@operation("list_create", access=WRITE, method="POST", path="boards/{board_id}/lists/",
           description="Create a list at the end of the board, or at position (1 or more; 0 is the default list).",
           params={"board_id": ID, "title": TITLE, "position": POSITION}, required=["board_id", "title"])
def list_create(user, board_id, title, position=None):
    return list_data(s.create_list(user, board_id, title, position), [])


@operation("list_update", access=WRITE, method="PATCH", path="lists/{list_id}/",
           description="Rename a list. The default list cannot be renamed.",
           params={"list_id": ID, "title": TITLE}, required=["list_id", "title"])
def list_update(user, list_id, title):
    return list_data(s.rename_list(user, list_id, title))


@operation("list_move", access=WRITE, method="POST", path="lists/{list_id}/move/",
           description="Move a list to a position (1 or more); the default list stays first.",
           params={"list_id": ID, "position": POSITION}, required=["list_id", "position"])
def list_move(user, list_id, position):
    return list_data(s.move_list(user, list_id, position))


@operation("list_delete", access=WRITE, method="DELETE", path="lists/{list_id}/",
           description="Delete a list. Its tasks of every state move to the end of the default list.",
           params={"list_id": ID}, required=["list_id"], destructive=True)
def list_delete(user, list_id):
    return {"deleted": list_id, "moved": [task_data(t) for t in s.delete_list(user, list_id)]}
