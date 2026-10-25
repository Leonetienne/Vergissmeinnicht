"""Every action is one Operation; REST (/api/v1/), MCP (/mcp) and the frontend all call through here."""
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable

from boards.services import ServiceError

READ = "read"
WRITE = "write"


class OpError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


@dataclass(frozen=True)
class Operation:
    name: str
    access: str
    method: str
    path: str
    description: str
    handler: Callable[..., Any]
    params: dict = field(default_factory=dict)
    required: tuple = ()
    destructive: bool = False

    def input_schema(self):
        schema = {"type": "object", "properties": self.params, "additionalProperties": False}
        if self.required:
            schema["required"] = list(self.required)
        return schema

    def path_params(self):
        return [part[1:-1] for part in self.path.split("/") if part.startswith("{")]


REGISTRY: dict[str, Operation] = {}


def operation(name, *, access, method, path, description, params=None, required=(), destructive=False):
    def register(handler):
        assert name not in REGISTRY and access in (READ, WRITE)
        REGISTRY[name] = Operation(
            name, access, method, path, description, handler, params or {}, tuple(required), destructive
        )
        return handler

    return register


# Shared parameter schemas
ID = {"type": "integer", "minimum": 1}
POSITION = {"type": "integer", "minimum": 0, "description": "0-based position among the siblings"}
DATE = {"type": ["string", "null"], "format": "date", "description": "YYYY-MM-DD or null"}


def _coerce(schema, value, name):
    types = schema.get("type")
    types = types if isinstance(types, list) else [types]
    if value is None:
        if "null" in types:
            return None
        raise OpError(f"{name} is required")
    if "integer" in types:
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            value = int(value)
        if not isinstance(value, int) or isinstance(value, bool):
            raise OpError(f"{name} must be an integer")
        if value < schema.get("minimum", value) or value > 2**31:
            raise OpError(f"{name} is out of range")
        return value
    if "boolean" in types:
        if isinstance(value, str) and value.lower() in ("true", "false"):
            return value.lower() == "true"
        if not isinstance(value, bool):
            raise OpError(f"{name} must be true or false")
        return value
    if "string" in types:
        if not isinstance(value, str):
            raise OpError(f"{name} must be text")
        if schema.get("format") == "date":
            if value == "" and "null" in types:
                return None
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise OpError(f"{name} must be a date (YYYY-MM-DD)")
        if "enum" in schema and value not in schema["enum"]:
            raise OpError(f"{name} must be one of {', '.join(schema['enum'])}")
        return value
    if "array" in types:
        if not isinstance(value, list):
            raise OpError(f"{name} must be a list")
        if len(value) > 1000:
            raise OpError(f"{name} has too many entries")
        return [_coerce(schema["items"], item, name) for item in value]
    if "object" in types:
        if not isinstance(value, dict):
            raise OpError(f"{name} must be an object")
        return _coerce_args(schema["properties"], schema.get("required", ()), value)
    raise OpError(f"{name} has an unsupported type")


def _coerce_args(properties, required, raw):
    unknown = set(raw) - set(properties)
    if unknown:
        raise OpError(f"Unknown parameter {sorted(unknown)[0]}")
    for name in required:
        if name not in raw:
            raise OpError(f"{name} is required")
    return {name: _coerce(properties[name], value, name) for name, value in raw.items()}


def call(name, user, raw):
    """Validate raw args and run the operation as user. Raises OpError."""
    op = REGISTRY.get(name)
    if op is None:
        raise OpError(f"Unknown operation {name}", 404)
    if not isinstance(raw, dict):
        raise OpError("Arguments must be an object")
    args = _coerce_args(op.params, op.required, raw)
    try:
        return op.handler(user, **args)
    except ServiceError as e:
        raise OpError(e.message, e.status)
