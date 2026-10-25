import json

import pytest
from django.test import Client

from accounts.models import Key
from api.registry import REGISTRY
from boards import services as s

EXCLUDED_WORDS = ("password", "key", "totp", "factor", "backdrop", "register", "account")


def test_every_operation_has_a_route_and_tool(client, people):
    index = client.get("/api/v1/").json()["operations"]
    assert {op["name"] for op in index} == set(REGISTRY)
    for op in index:
        assert op["method"] and op["path"].startswith("/api/v1/") and op["description"] and "properties" in op["parameters"]


def test_no_account_takeover_operations():
    for name in REGISTRY:
        assert not any(word in name for word in EXCLUDED_WORDS), name


@pytest.mark.parametrize("header", [None, "Bearer wrong", "Basic abc"])
def test_rest_requires_auth(client, people, header):
    extra = {"HTTP_AUTHORIZATION": header} if header else {}
    response = client.get("/api/v1/boards/", **extra)
    assert response.status_code == 401 and response.json() == {"error": "Authentication required"}


def test_keys_are_separate(client, people):
    owner = people[0]
    api_key = Key.generate(owner, Key.API)
    mcp_key = Key.generate(owner, Key.MCP)
    assert client.get("/api/v1/boards/", HTTP_AUTHORIZATION=f"Bearer {mcp_key}").status_code == 401
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert client.post("/mcp", body, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {api_key}").status_code == 401
    assert client.post("/mcp", body, content_type="application/json").status_code == 401


def test_revoked_key_fails(client, people):
    key = Key.generate(people[0], Key.API)
    Key.objects.all().delete()
    assert client.get("/api/v1/boards/", HTTP_AUTHORIZATION=f"Bearer {key}").status_code == 401


def test_key_last_use_recorded(client, people):
    key = Key.generate(people[0], Key.API)
    client.get("/api/v1/boards/", HTTP_AUTHORIZATION=f"Bearer {key}")
    assert Key.objects.get().last_used_at is not None


def test_new_key_replaces_old(people):
    first = Key.generate(people[0], Key.API)
    Key.generate(people[0], Key.API)
    assert Key.objects.count() == 1
    assert Key.authenticate(first, Key.API) is None


def test_session_reads_and_csrf_writes(people):
    browser = Client(enforce_csrf_checks=True)
    browser.force_login(people[0])
    assert browser.get("/api/v1/boards/").status_code == 200
    assert browser.post("/api/v1/boards/", json.dumps({"name": "A"}), content_type="application/json").status_code == 401
    browser.get("/")
    token = browser.cookies["csrftoken"].value
    response = browser.post("/api/v1/boards/", json.dumps({"name": "A"}), content_type="application/json", HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 200


@pytest.mark.parametrize("body", ["not json", "[1]", '{"name": 5}', '{"name": "A", "bogus": 1}'])
def test_malformed_bodies_are_400(client, people, body):
    key = Key.generate(people[0], Key.API)
    response = client.post("/api/v1/boards/", body, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {key}")
    assert response.status_code == 400 and "error" in response.json()


def test_unknown_route_and_method(client, people):
    key = Key.generate(people[0], Key.API)
    auth = {"HTTP_AUTHORIZATION": f"Bearer {key}"}
    assert client.get("/api/v1/nothing/", **auth).status_code == 404
    assert client.put("/api/v1/boards/", **auth).status_code == 405


class TestMcp:
    def rpc(self, client, key, method, params=None, msg_id=1):
        body = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if msg_id is not None:
            body["id"] = msg_id
        return client.post("/mcp", json.dumps(body), content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {key}")

    def test_initialize_has_instructions(self, client, people):
        key = Key.generate(people[0], Key.MCP)
        result = self.rpc(client, key, "initialize", {"protocolVersion": "2025-06-18"}).json()["result"]
        assert result["capabilities"]["tools"] is not None
        assert "default list" in result["instructions"] and "observer" in result["instructions"]

    def test_notification_is_accepted(self, client, people):
        key = Key.generate(people[0], Key.MCP)
        assert self.rpc(client, key, "notifications/initialized", msg_id=None).status_code == 202

    def test_tools_match_registry(self, client, people):
        key = Key.generate(people[0], Key.MCP)
        tools = {t["name"]: t for t in self.rpc(client, key, "tools/list").json()["result"]["tools"]}
        assert set(tools) == set(REGISTRY)
        assert tools["task_delete"]["annotations"]["destructiveHint"] is True
        assert tools["board_get"]["annotations"]["readOnlyHint"] is True
        assert tools["task_create"]["annotations"]["destructiveHint"] is False
        assert tools["task_create"]["inputSchema"]["required"] == ["list_id", "title"]

    def test_unknown_method_and_tool(self, client, people):
        key = Key.generate(people[0], Key.MCP)
        assert self.rpc(client, key, "resources/list").json()["error"]["code"] == -32601
        result = self.rpc(client, key, "tools/call", {"name": "drop_tables", "arguments": {}}).json()["result"]
        assert result["isError"] is True

    def test_every_result_is_structured(self, client, people, board, default_list):
        key = Key.generate(people[0], Key.MCP)
        task = s.create_task(people[0], default_list.id, "A")
        calls = [("shares_list", {"board_id": board.id}),
                 ("tasks_move", {"moves": [{"task_id": task.id, "list_id": default_list.id, "position": 0}]}),
                 ("profile_get", {})]
        for name, args in calls:
            result = self.rpc(client, key, "tools/call", {"name": name, "arguments": args}).json()["result"]
            structured = result["structuredContent"]
            assert isinstance(structured, dict)
            assert structured == json.loads(result["content"][0]["text"]) or structured["items"] == json.loads(result["content"][0]["text"])

    def test_parse_error(self, client, people):
        key = Key.generate(people[0], Key.MCP)
        response = client.post("/mcp", "{", content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {key}")
        assert response.json()["error"]["code"] == -32700


def test_board_page_query_count_is_constant(client, people, board, default_list, django_assert_max_num_queries):
    owner = people[0]
    client.force_login(owner)
    for i in range(3):
        lst = s.create_list(owner, board.id, f"L{i}")
        for j in range(5):
            s.create_task(owner, lst.id, f"T{i}{j}")
    with django_assert_max_num_queries(12):
        assert client.get(board.get_absolute_url()).status_code == 200
