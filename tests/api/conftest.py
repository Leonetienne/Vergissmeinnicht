import json
from urllib.parse import urlencode
from dataclasses import dataclass

import pytest

from accounts.models import Key, User
from api.registry import REGISTRY
from boards import services as s


@dataclass
class Result:
    ok: bool
    status: int | None
    data: object
    error: str | None


def make_user(email, name=None):
    return User.objects.create_user(email, "Forget-me-not-1", display_name=name or email.split("@")[0])


class Transport:
    """Calls an operation as a user through REST (API key) or MCP (MCP key)."""

    def __init__(self, kind, client):
        self.kind = kind
        self.client = client
        self.keys = {}

    def key(self, user):
        if user.pk not in self.keys:
            self.keys[user.pk] = Key.generate(user, Key.API if self.kind == "rest" else Key.MCP)
        return self.keys[user.pk]

    def __call__(self, op_name, user, /, **args):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {self.key(user)}"} if user else {}
        return self.rest(op_name, headers, args) if self.kind == "rest" else self.mcp(op_name, headers, args)

    def rest(self, name, headers, args):
        op = REGISTRY[name]
        path = "/api/v1/" + op.path
        for key in op.path_params():
            path = path.replace("{" + key + "}", str(args.pop(key)))
        if op.method in ("GET", "DELETE"):
            response = self.client.generic(op.method, path + ("?" + urlencode(args) if args else ""), **headers)
        else:
            response = self.client.generic(op.method, path, json.dumps(args), content_type="application/json", **headers)
        data = response.json()
        ok = response.status_code == 200
        return Result(ok, response.status_code, data if ok else None, None if ok else data["error"])

    def mcp(self, name, headers, args):
        body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}}
        response = self.client.post("/mcp", json.dumps(body), content_type="application/json", **headers)
        if response.status_code == 401:
            return Result(False, 401, None, response.json()["error"])
        result = response.json()["result"]
        text = result["content"][0]["text"]
        if result.get("isError"):
            return Result(False, None, None, text)
        return Result(True, None, json.loads(text), None)


@pytest.fixture(params=["rest", "mcp"])
def call(request, client):
    return Transport(request.param, client)


@pytest.fixture
def people(db):
    owner = make_user("owner@example.org", "Leon")
    editor = make_user("editor@example.org", "Mara Lind")
    observer = make_user("observer@example.org", "Jonas Weber")
    stranger = make_user("stranger@example.org", "Stranger")
    return owner, editor, observer, stranger


@pytest.fixture
def board(people):
    owner, editor, observer, _ = people
    board = s.create_board(owner, "Household")
    s.add_share(owner, board.id, editor.id, "editor")
    s.add_share(owner, board.id, observer.id, "observer")
    return board


@pytest.fixture
def default_list(board):
    return board.lists.get(is_default=True)


def refused(result, status):
    """Assert an operation failed; MCP carries no status code, only the error flag."""
    assert not result.ok
    if result.status is not None:
        assert result.status == status, result.error
    return result
