from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Case, IntegerField, Prefetch, Q, When
from django.db.models.functions import Lower

from accounts.models import unique_slug

from .models import Board, List, Share, Task

OWNER = "owner"
EDITOR = Share.EDITOR
OBSERVER = Share.OBSERVER

READ = "read"
WRITE = "write"
OWNER_ONLY = "owner"

TRANSITIONS = {
    (Task.OPEN, Task.DONE),
    (Task.DONE, Task.OPEN),
    (Task.DONE, Task.ARCHIVED),
    (Task.ARCHIVED, Task.DONE),
}

UNSET = object()


class ServiceError(Exception):
    status = 400

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Invalid(ServiceError):
    status = 400


class Forbidden(ServiceError):
    status = 403


class NotFound(ServiceError):
    status = 404


class Conflict(ServiceError):
    status = 409


# Validation

def clean_text(value, label, max_len, required=True):
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise Invalid(f"{label} must be text")
    value = value.strip()
    if required and not value:
        raise Invalid(f"{label} is required")
    if len(value) > max_len:
        raise Invalid(f"{label} is longer than {max_len} characters")
    return value


def clean_emoji(value):
    value = clean_text(value, "Emoji", 32, required=False)
    if any((ch.isascii() and ch.isalpha()) or ch in "<>&\"'" for ch in value):
        raise Invalid("Emoji is not an emoji")
    return value


def clean_colour(value):
    if value not in Task.COLOURS:
        raise Invalid(f"Colour must be one of {', '.join(Task.COLOURS)}")
    return value


def clean_state(value):
    if value not in Task.STATES:
        raise Invalid(f"State must be one of {', '.join(Task.STATES)}")
    return value


def clean_role(value):
    if value not in (OBSERVER, EDITOR):
        raise Invalid("Role must be observer or editor")
    return value


def due_status(due_date, state, today):
    """Return "now", "soon" or None for the card warning and reminder stage."""
    if state != Task.OPEN or due_date is None:
        return None
    days = (due_date - today).days
    if days <= 0:
        return "now"
    if days <= 3:
        return "soon"
    return None


# Access

def role_for(user, board):
    if board.owner_id == user.id:
        return OWNER
    share = Share.objects.filter(board=board, user=user).only("role").first()
    return share.role if share else None


def _check(user, board, need, missing):
    role = role_for(user, board)
    if role is None:
        raise NotFound(missing)
    if need == WRITE and role == OBSERVER:
        raise Forbidden("Observers cannot change this board")
    if need == OWNER_ONLY and role != OWNER:
        raise Forbidden("Only the owner can do this")
    board.role = role
    return role


def get_board_by_slug(user, username, slug):
    board = Board.objects.select_related("owner").filter(owner__username=username, slug=slug).first()
    if board is None:
        raise NotFound("Board not found")
    _check(user, board, READ, "Board not found")
    return board


def get_board(user, board_id, need=READ):
    board = Board.objects.select_related("owner").filter(pk=board_id).first()
    if board is None:
        raise NotFound("Board not found")
    _check(user, board, need, "Board not found")
    return board


def get_list(user, list_id, need=READ):
    lst = List.objects.select_related("board__owner").filter(pk=list_id).first()
    if lst is None:
        raise NotFound("List not found")
    _check(user, lst.board, need, "List not found")
    return lst


def get_task(user, task_id, need=READ):
    task = Task.objects.select_related("list__board__owner").filter(pk=task_id).first()
    if task is None:
        raise NotFound("Task not found")
    _check(user, task.list.board, need, "Task not found")
    return task


def member_board_ids(user):
    return Board.objects.filter(Q(owner=user) | Q(shares__user=user)).values("id")


# Positions

def _renumber(items):
    changed = []
    for index, item in enumerate(items):
        if item.position != index:
            item.position = index
            changed.append(item)
    if changed:
        type(changed[0]).objects.bulk_update(changed, ["position"])


def _place(items, obj, position, minimum=0):
    """Insert a saved obj into the ordered siblings at position (clamped) and renumber."""
    if position is None:
        position = len(items)
    position = max(minimum, min(int(position), len(items)))
    items.insert(position, obj)
    _renumber(items)


def ordered_tasks(queryset):
    rank = Case(
        When(state=Task.OPEN, then=0), When(state=Task.DONE, then=1), default=2, output_field=IntegerField()
    )
    return queryset.annotate(rank=rank).order_by("rank", "position", "id")


def _list_sequence(lst):
    return list(Task.objects.filter(list=lst).order_by("position", "id"))


# Boards

def boards_for(user):
    own = list(Board.objects.filter(owner=user).select_related("owner").order_by("position", "id"))
    for board in own:
        board.role = OWNER
    shared = []
    for share in Share.objects.filter(user=user).select_related("board__owner"):
        share.board.role = share.role
        shared.append(share.board)
    shared.sort(key=lambda b: (b.title.lower(), b.id))
    return own, shared


def board_content(board, states=None):
    """Attach board.lists_data: lists in order, each with .task_items ordered by state and position."""
    tasks = Task.objects.all()
    if states is not None:
        tasks = tasks.filter(state__in=states)
    board.list_items = list(
        board.lists.order_by("position", "id").prefetch_related(
            Prefetch("tasks", queryset=ordered_tasks(tasks), to_attr="task_items")
        )
    )
    return board


STARTER_BOARDS = [("My Todos", "🧹"), ("Shopping List", "🛒")]


def board_slug(owner, title, board=None):
    taken = Board.objects.filter(owner=owner)
    if board is not None:
        taken = taken.exclude(pk=board.pk)
    return unique_slug(title, set(taken.values_list("slug", flat=True)), "board")


def create_starter_boards(user):
    for title, emoji in STARTER_BOARDS:
        create_board(user, title, emoji)


@transaction.atomic
def create_board(user, title, emoji="", position=None):
    title = clean_text(title, "Board title", 100)
    emoji = clean_emoji(emoji)
    siblings = list(Board.objects.select_for_update().filter(owner=user).order_by("position", "id"))
    board = Board.objects.create(owner=user, title=title, emoji=emoji, slug=board_slug(user, title))
    List.objects.create(board=board, is_default=True, position=0)
    _place(siblings, board, position)
    board.role = OWNER
    return board


def update_board(user, board_id, title=UNSET, emoji=UNSET):
    board = get_board(user, board_id, OWNER_ONLY)
    if title is not UNSET:
        board.title = clean_text(title, "Board title", 100)
        board.slug = board_slug(board.owner, board.title, board)
    if emoji is not UNSET:
        board.emoji = clean_emoji(emoji)
    board.save()
    return board


@transaction.atomic
def delete_board(user, board_id):
    board = get_board(user, board_id, OWNER_ONLY)
    board.delete()
    _renumber(list(Board.objects.filter(owner=user).order_by("position", "id")))


@transaction.atomic
def move_board(user, board_id, position):
    board = get_board(user, board_id, OWNER_ONLY)
    siblings = list(Board.objects.filter(owner=user).exclude(pk=board.pk).order_by("position", "id"))
    _place(siblings, board, position)
    return board


def leave_board(user, board_id):
    board = get_board(user, board_id, READ)
    if board.role == OWNER:
        raise Invalid("The owner cannot leave the board")
    Share.objects.filter(board=board, user=user).delete()


# Shares

def list_shares(user, board_id):
    board = get_board(user, board_id, OWNER_ONLY)
    return list(board.shares.select_related("user").order_by(Lower("user__display_name"), "id"))


def search_users(user, board_id, query):
    board = get_board(user, board_id, OWNER_ONLY)
    query = clean_text(query, "Search text", 254, required=False)
    if len(query) < 3:
        return []
    return list(
        get_user_model()
        .objects.filter(Q(display_name__icontains=query) | Q(email__icontains=query), is_active=True)
        .exclude(pk=board.owner_id)
        .exclude(shares__board=board)
        .order_by(Lower("display_name"), "id")[:10]
    )


def add_share(user, board_id, user_id, role=OBSERVER):
    board = get_board(user, board_id, OWNER_ONLY)
    role = clean_role(role)
    target = get_user_model().objects.filter(pk=user_id, is_active=True).first()
    if target is None:
        raise NotFound("User not found")
    if target.pk == board.owner_id:
        raise Invalid("The owner cannot be added")
    if Share.objects.filter(board=board, user=target).exists():
        raise Conflict("User already has access")
    return Share.objects.create(board=board, user=target, role=role)


def _get_share(user, share_id):
    share = Share.objects.select_related("board", "user").filter(pk=share_id).first()
    if share is None:
        raise NotFound("Share not found")
    _check(user, share.board, OWNER_ONLY, "Share not found")
    return share


def update_share(user, share_id, role):
    share = _get_share(user, share_id)
    share.role = clean_role(role)
    share.save(update_fields=["role"])
    return share


def remove_share(user, share_id):
    _get_share(user, share_id).delete()


# Lists

@transaction.atomic
def create_list(user, board_id, title, position=None):
    board = get_board(user, board_id, WRITE)
    title = clean_text(title, "List title", 100)
    siblings = list(board.lists.select_for_update().order_by("position", "id"))
    lst = List.objects.create(board=board, title=title, position=len(siblings))
    _place(siblings, lst, position, minimum=1)
    return lst


def _custom_list(user, list_id):
    lst = get_list(user, list_id, WRITE)
    if lst.is_default:
        raise Invalid("The default list cannot be changed")
    return lst


def rename_list(user, list_id, title):
    lst = _custom_list(user, list_id)
    lst.title = clean_text(title, "List title", 100)
    lst.save(update_fields=["title"])
    return lst


@transaction.atomic
def move_list(user, list_id, position):
    lst = _custom_list(user, list_id)
    siblings = list(lst.board.lists.exclude(pk=lst.pk).order_by("position", "id"))
    _place(siblings, lst, position, minimum=1)
    return lst


@transaction.atomic
def delete_list(user, list_id):
    """Move every task to the end of the default list and delete the list. Returns the moved tasks."""
    lst = _custom_list(user, list_id)
    default = lst.board.lists.get(is_default=True)
    start = Task.objects.filter(list=default).count()
    moved = _list_sequence(lst)
    for offset, task in enumerate(moved):
        task.list = default
        task.position = start + offset
    Task.objects.bulk_update(moved, ["list", "position"])
    board = lst.board
    lst.delete()
    _renumber(list(board.lists.order_by("position", "id")))
    return moved


# Tasks

def _clean_due(value):
    if value is None or value == "":
        return None
    if hasattr(value, "isoformat"):
        return value
    raise Invalid("Due date must be a date")


@transaction.atomic
def create_task(user, list_id, title, position=None, state=Task.OPEN, due_date=None, colour="none", note=""):
    lst = get_list(user, list_id, WRITE)
    siblings = list(Task.objects.select_for_update().filter(list=lst).order_by("position", "id"))
    task = Task.objects.create(
        list=lst,
        title=clean_text(title, "Task title", 200),
        state=clean_state(state),
        due_date=_clean_due(due_date),
        colour=clean_colour(colour or "none"),
        note=clean_text(note, "Note", 5000, required=False),
        position=len(siblings),
    )
    _place(siblings, task, position)
    return task


def update_task(user, task_id, title=UNSET, due_date=UNSET, colour=UNSET, note=UNSET):
    task = get_task(user, task_id, WRITE)
    if title is not UNSET:
        task.title = clean_text(title, "Task title", 200)
    if due_date is not UNSET:
        due_date = _clean_due(due_date)
        if due_date != task.due_date:
            task.reminded_soon = task.reminded_due = False
        task.due_date = due_date
    if colour is not UNSET:
        task.colour = clean_colour(colour)
    if note is not UNSET:
        task.note = clean_text(note, "Note", 5000, required=False)
    task.save()
    return task


def transition(task, state):
    """The only place that changes a task's state."""
    if (task.state, state) not in TRANSITIONS:
        raise Conflict(f"A {task.state} task cannot become {state}")
    task.state = state
    task.save(update_fields=["state"])
    return task


def transition_task(user, task_id, state):
    state = clean_state(state)
    return transition(get_task(user, task_id, WRITE), state)


@transaction.atomic
def transition_tasks(user, task_ids, state):
    state = clean_state(state)
    tasks = [get_task(user, task_id, WRITE) for task_id in task_ids]
    return [transition(task, state) for task in tasks]


@transaction.atomic
def archive_done(user, board_id):
    board = get_board(user, board_id, WRITE)
    done = list(Task.objects.filter(list__board=board, state=Task.DONE).order_by("id"))
    return [transition(task, Task.ARCHIVED) for task in done]


@transaction.atomic
def move_task(user, task_id, list_id, position):
    task = get_task(user, task_id, WRITE)
    target = get_list(user, list_id, WRITE)
    if target.board_id != task.list.board_id:
        raise Invalid("Tasks move only within their board")
    source = task.list
    remaining = [t for t in _list_sequence(source) if t.pk != task.pk]
    if source.pk != target.pk:
        _renumber(remaining)
        remaining = _list_sequence(target)
        task.list = target
        task.save(update_fields=["list"])
    _place(remaining, task, position)
    return task


@transaction.atomic
def move_tasks(user, moves):
    return [move_task(user, m["task_id"], m["list_id"], m["position"]) for m in moves]


@transaction.atomic
def delete_task(user, task_id):
    task = get_task(user, task_id, WRITE)
    lst = task.list
    task.delete()
    _renumber(_list_sequence(lst))


def archive_of(user, board_id):
    board = get_board(user, board_id, READ)
    return board_content(board, states=[Task.ARCHIVED])


# Search

def search(user, query, limit=50):
    query = clean_text(query, "Search text", 200, required=False)
    if len(query) < 2:
        return [], []
    board_ids = member_board_ids(user)
    boards = list(
        Board.objects.filter(id__in=board_ids, title__icontains=query).select_related("owner").order_by(Lower("title"), "id")[:limit]
    )
    tasks = list(
        ordered_tasks(
            Task.objects.filter(Q(title__icontains=query) | Q(note__icontains=query), list__board_id__in=board_ids)
        ).select_related("list__board__owner")[: limit - len(boards)]
    )
    return boards, tasks
