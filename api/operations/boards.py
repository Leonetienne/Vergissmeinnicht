from boards import services as s
from boards.serializers import board_data, board_with_lists

from ..registry import ID, POSITION, READ, WRITE, operation

TITLE = {"type": "string", "description": "1 to 100 characters"}
EMOJI = {"type": "string", "description": "One emoji, or empty to remove it"}
DESCRIPTION = {"type": "string", "description": "Up to 1000 characters, or empty to remove it"}


@operation("boards_list", access=READ, method="GET", path="boards/",
           description="List own boards in their order and boards shared with the user.")
def boards_list(user):
    own, shared = s.boards_for(user)
    return {"own": [board_data(b) for b in own], "shared": [board_data(b) for b in shared]}


@operation("board_get", access=READ, method="GET", path="boards/{board_id}/",
           description="Get a board with all lists and tasks of every state. Same JSON as the board export.",
           params={"board_id": ID}, required=["board_id"])
def board_get(user, board_id):
    return board_with_lists(s.board_content(s.get_board(user, board_id)))


@operation("board_create", access=WRITE, method="POST", path="boards/",
           description="Create a board with its default list. Owner is the caller.",
           params={"title": TITLE, "emoji": EMOJI, "position": POSITION}, required=["title"])
def board_create(user, **args):
    return board_data(s.create_board(user, **args))


@operation("board_update", access=WRITE, method="PATCH", path="boards/{board_id}/",
           description="Rename a board or change its emoji or description. Owner only.",
           params={"board_id": ID, "title": TITLE, "emoji": EMOJI, "description": DESCRIPTION}, required=["board_id"])
def board_update(user, board_id, **args):
    return board_data(s.update_board(user, board_id, **args))


@operation("board_move", access=WRITE, method="POST", path="boards/{board_id}/move/",
           description="Move one of the caller's own boards to a position in their board list.",
           params={"board_id": ID, "position": POSITION}, required=["board_id", "position"])
def board_move(user, board_id, position):
    return board_data(s.move_board(user, board_id, position))


@operation("board_delete", access=WRITE, method="DELETE", path="boards/{board_id}/",
           description="Delete a board with all lists, tasks and shares. Owner only.",
           params={"board_id": ID}, required=["board_id"], destructive=True)
def board_delete(user, board_id):
    s.delete_board(user, board_id)
    return {"deleted": board_id}


@operation("board_leave", access=WRITE, method="POST", path="boards/{board_id}/leave/",
           description="Remove the caller's own share of a board shared with them.",
           params={"board_id": ID}, required=["board_id"], destructive=True)
def board_leave(user, board_id):
    s.leave_board(user, board_id)
    return {"left": board_id}


@operation("board_archive_done", access=WRITE, method="POST", path="boards/{board_id}/archive-done/",
           description="Archive every done task of a board. Returns the archived task ids.",
           params={"board_id": ID}, required=["board_id"])
def board_archive_done(user, board_id):
    return {"task_ids": [t.id for t in s.archive_done(user, board_id)]}


@operation("board_archive", access=READ, method="GET", path="boards/{board_id}/archive/",
           description="Get a board with its lists and only the archived tasks.",
           params={"board_id": ID}, required=["board_id"])
def board_archive(user, board_id):
    return board_with_lists(s.archive_of(user, board_id))
