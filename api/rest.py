import json
from collections import defaultdict

from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Key

from . import operations  # noqa: F401  registers the handlers
from .auth import bearer_token, key_user
from .registry import REGISTRY, OpError, call

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def error(message, status):
    return JsonResponse({"error": message}, status=status)


def _csrf_ok(request):
    return CsrfViewMiddleware(lambda r: None).process_view(request, None, (), {}) is None


def authenticate(request):
    if bearer_token(request) is not None:
        return key_user(request, Key.API)
    if request.user.is_authenticated and (request.method in SAFE_METHODS or _csrf_ok(request)):
        return request.user
    return None


def _arguments(request, path_args):
    if request.method in ("GET", "DELETE"):
        args = {k: v for k, v in request.GET.items()}
    elif request.body:
        try:
            args = json.loads(request.body)
        except (ValueError, UnicodeDecodeError):
            raise OpError("Body is not valid JSON")
        if not isinstance(args, dict):
            raise OpError("Body must be a JSON object")
    else:
        args = {}
    return {**args, **path_args}


@csrf_exempt
def endpoint(request, ops, **path_args):
    op = ops.get(request.method)
    if op is None:
        return error("Method not allowed", 405)
    user = authenticate(request)
    if user is None:
        return error("Authentication required", 401)
    try:
        result = call(op.name, user, _arguments(request, path_args))
    except OpError as e:
        return error(e.message, e.status)
    return JsonResponse(result, safe=False)


def index(request):
    return JsonResponse({
        "operations": [
            {
                "name": op.name,
                "method": op.method,
                "path": "/api/v1/" + op.path,
                "description": op.description,
                "access": op.access,
                "parameters": op.input_schema(),
            }
            for op in REGISTRY.values()
        ]
    })


def _django_path(op_path):
    return "/".join(f"<int:{part[1:-1]}>" if part.startswith("{") else part for part in op_path.split("/"))


def urlpatterns_for_registry():
    grouped = defaultdict(dict)
    for op in REGISTRY.values():
        grouped[op.path][op.method] = op
    patterns = [path("", index)]
    for op_path, ops in grouped.items():
        patterns.append(path(_django_path(op_path), endpoint, {"ops": ops}))
    return patterns


def handler404(request, exception=None):
    return error("Not found", 404)


def api_routes():
    """Method and path per operation for the frontend's api client."""
    return {op.name: [op.method, "/api/v1/" + op.path] for op in REGISTRY.values()}
