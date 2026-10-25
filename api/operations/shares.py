from boards import services as s
from boards.serializers import share_data

from ..registry import ID, READ, WRITE, operation

ROLE = {"type": "string", "enum": ["observer", "editor"]}


@operation("shares_list", access=READ, method="GET", path="boards/{board_id}/shares/",
           description="List the shares of a board. Owner only.",
           params={"board_id": ID}, required=["board_id"])
def shares_list(user, board_id):
    return [share_data(sh) for sh in s.list_shares(user, board_id)]


@operation("share_candidates", access=READ, method="GET", path="boards/{board_id}/share-candidates/",
           description="Find up to 10 users by name or email (at least 3 characters) to share a board with. Owner only.",
           params={"board_id": ID, "q": {"type": "string"}}, required=["board_id", "q"])
def share_candidates(user, board_id, q):
    return [{"id": u.id, "display_name": u.display_name, "email": u.email}
            for u in s.search_users(user, board_id, q)]


@operation("share_add", access=WRITE, method="POST", path="boards/{board_id}/shares/",
           description="Share a board with a user as observer (default) or editor. Owner only.",
           params={"board_id": ID, "user_id": ID, "role": ROLE}, required=["board_id", "user_id"])
def share_add(user, board_id, user_id, role="observer"):
    return share_data(s.add_share(user, board_id, user_id, role))


@operation("share_update", access=WRITE, method="PATCH", path="shares/{share_id}/",
           description="Change the role of a share. Owner only.",
           params={"share_id": ID, "role": ROLE}, required=["share_id", "role"])
def share_update(user, share_id, role):
    return share_data(s.update_share(user, share_id, role))


@operation("share_remove", access=WRITE, method="DELETE", path="shares/{share_id}/",
           description="Remove a share, revoking the member's access. Owner only.",
           params={"share_id": ID}, required=["share_id"], destructive=True)
def share_remove(user, share_id):
    s.remove_share(user, share_id)
    return {"deleted": share_id}
