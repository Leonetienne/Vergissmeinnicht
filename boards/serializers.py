"""The one JSON shape per entity, shared by pages, REST, MCP, JSON export and undo."""


def user_data(user):
    return {"id": user.id, "display_name": user.display_name}


def task_data(task):
    return {
        "id": task.id,
        "list_id": task.list_id,
        "title": task.title,
        "state": task.state,
        "position": task.position,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "colour": task.colour,
        "note": task.note,
    }


def list_data(lst, tasks=None):
    data = {
        "id": lst.id,
        "board_id": lst.board_id,
        "title": lst.title,
        "colour": lst.colour,
        "is_default": lst.is_default,
        "position": lst.position,
    }
    if tasks is not None:
        data["tasks"] = [task_data(t) for t in tasks]
    return data


def board_data(board, lists=None):
    """Lists are included when given as (list, tasks) pairs."""
    data = {
        "id": board.id,
        "title": board.title,
        "emoji": board.emoji,
        "description": board.description,
        "url": board.get_absolute_url(),
        "owner": user_data(board.owner),
        "role": getattr(board, "role", None),
    }
    if lists is not None:
        data["lists"] = [list_data(lst, tasks) for lst, tasks in lists]
    return data


def board_with_lists(board):
    """Serialize a board prepared by services.board_content."""
    return board_data(board, [(lst, lst.task_items) for lst in board.list_items])


def share_data(share):
    return {
        "id": share.id,
        "board_id": share.board_id,
        "user": {**user_data(share.user), "email": share.user.email},
        "role": share.role,
    }
