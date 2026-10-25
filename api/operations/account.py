from accounts import services as acc
from boards import services as s
from boards.serializers import board_data, list_data, task_data

from ..registry import READ, WRITE, operation


@operation("search", access=READ, method="GET", path="search/",
           description="Find boards by name and tasks by title or note (at least 2 characters), boards first, up to 50.",
           params={"q": {"type": "string"}}, required=["q"])
def search(user, q):
    boards, tasks = s.search(user, q)
    return {
        "boards": [board_data(b) for b in boards],
        "tasks": [{**task_data(t), "board": board_data(t.list.board), "list": list_data(t.list)} for t in tasks],
    }


@operation("profile_get", access=READ, method="GET", path="profile/",
           description="Get the caller's display name, email address and reminder setting.")
def profile_get(user):
    return acc.profile_data(user)


@operation("profile_update", access=WRITE, method="PATCH", path="profile/",
           description="Change display name, email address or reminder setting.",
           params={"display_name": {"type": "string"}, "email": {"type": "string"},
                   "reminders_enabled": {"type": "boolean"}})
def profile_update(user, **args):
    return acc.profile_data(acc.update_profile(user, **args))
