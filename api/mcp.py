import json

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Key

from . import operations  # noqa: F401  registers the handlers
from .auth import key_user
from .registry import READ, REGISTRY, OpError, call

PROTOCOL_VERSION = "2025-06-18"

INSTRUCTIONS = """Vergissmeinnicht is a to-do app. A board holds lists; every board has one untitled default list \
(is_default, always first, cannot be renamed, moved or deleted). Tasks belong to a list and have a state: \
open, done or archived. State changes go one step at a time: open <-> done <-> archived. Archived tasks are \
hidden from the board and shown on its archive. Task positions are 0-based within the list, all states included. \
Roles: the owner may do everything; an editor may change lists and tasks but not rename, share or delete the \
board; an observer may only read. Use boards_list to start, then board_get for lists and tasks."""


def tool_list():
    return [
        {
            "name": op.name,
            "description": op.description,
            "inputSchema": op.input_schema(),
            "annotations": {"readOnlyHint": op.access == READ, "destructiveHint": op.destructive},
        }
        for op in REGISTRY.values()
    ]


def _call_tool(user, params):
    name = params.get("name")
    if name not in REGISTRY:
        return {"content": [{"type": "text", "text": f"Unknown tool {name}"}], "isError": True}
    try:
        result = call(name, user, params.get("arguments") or {})
    except OpError as e:
        return {"content": [{"type": "text", "text": e.message}], "isError": True}
    # structuredContent has to be an object, so list results arrive as {"items": [...]}.
    structured = result if isinstance(result, dict) else {"items": result}
    return {"content": [{"type": "text", "text": json.dumps(result)}], "structuredContent": structured}


def _handle(user, message):
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or "method" not in message:
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
    method = message["method"]
    params = message.get("params") or {}
    if "id" not in message:
        return None
    if method == "initialize":
        result = {
            "protocolVersion": params.get("protocolVersion") or PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "vergissmeinnicht", "version": settings.APP_VERSION},
            "instructions": INSTRUCTIONS,
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": tool_list()}
    elif method == "tools/call" and isinstance(params, dict):
        result = _call_tool(user, params)
    else:
        return {"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": message["id"], "result": result}


@csrf_exempt
def endpoint(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    user = key_user(request, Key.MCP)
    if user is None:
        response = JsonResponse({"error": "Authentication required"}, status=401)
        response["WWW-Authenticate"] = "Bearer"
        return response
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
    if isinstance(payload, list):
        replies = [r for r in (_handle(user, m) for m in payload) if r is not None]
        return JsonResponse(replies, safe=False) if replies else HttpResponse(status=202)
    reply = _handle(user, payload)
    return JsonResponse(reply) if reply is not None else HttpResponse(status=202)
