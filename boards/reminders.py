from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMessage, get_connection

from .models import Share, Task
from .services import due_status

SOON = "soon"
DUE = "due"


def reminder_stage(task, today):
    """The reminder to send now, or None. "due" wins when both stages are pending."""
    status = due_status(task.due_date, task.state, today)
    if status == "now" and not task.reminded_due:
        return DUE
    if status == "soon" and not task.reminded_soon:
        return SOON
    return None


def recipients(board):
    users = [board.owner] + [s.user for s in board.shares.all() if s.role == Share.EDITOR]
    return [u for u in users if u.is_active and u.reminders_enabled]


def collect(today):
    """Return ({recipient: [(task, stage)]}, tasks to mark)."""
    tasks = (
        Task.objects.filter(state=Task.OPEN, due_date__lte=today + timedelta(days=3))
        .select_related("list__board__owner")
        .prefetch_related("list__board__shares__user")
        .order_by("due_date", "id")
    )
    digest = defaultdict(list)
    marked = []
    for task in tasks:
        stage = reminder_stage(task, today)
        if stage is None:
            continue
        for user in recipients(task.list.board):
            digest[user].append((task, stage))
        task.reminded_soon = True
        task.reminded_due = task.reminded_due or stage == DUE
        marked.append(task)
    return digest, marked


def message_for(user, items):
    lines = []
    for task, stage in items:
        board = task.list.board
        when = "due" if stage == DUE else "due soon"
        link = f"{settings.SITE_URL}{board.get_absolute_url()}#task-{task.id}"
        lines.append(f"- {task.title} ({board.name}, {when} {task.due_date:%b %-d, %Y})\n  {link}")
    count = len(items)
    subject = f"{count} task{'s' if count != 1 else ''} due"
    body = f"Hello {user.display_name},\n\nthese tasks are due:\n\n" + "\n".join(lines) + "\n"
    return EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_due_reminders(today):
    """Send one digest per recipient. Returns the number of emails sent."""
    digest, marked = collect(today)
    if digest:
        get_connection().send_messages([message_for(user, items) for user, items in digest.items()])
    Task.objects.bulk_update(marked, ["reminded_soon", "reminded_due"])
    return len(digest)
