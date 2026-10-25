# MCP Server

### Endpoint
`req~mcp.endpoint~1`

The system shall serve a stateless MCP server over HTTP (JSON-RPC) at `/mcp`.

Covers:
- `feat~mcp~1`

### Authentication
`req~mcp.auth~1`

The MCP server shall accept only a Bearer MCP key and answer 401 otherwise.

Covers:
- `feat~mcp~1`

Tags: Security

### Tools from operations
`req~mcp.tools~1`

The MCP server shall expose every REST API operation as a tool, generated from the central operation layer with its name, description and parameter schema, and mark write operations that delete data as destructive.

Covers:
- `feat~mcp~1`

### Same coverage as REST
`req~mcp.coverage~1`

The MCP server shall offer exactly the actions of the REST API, with the same exclusions.

Covers:
- `feat~mcp~1`

### Instructions
`req~mcp.instructions~1`

The MCP server shall send short instructions describing boards, lists, task states and roles to the connecting agent.

Covers:
- `feat~mcp~1`

### Structured results
`req~mcp.structured~1`

The MCP server shall return every successful tool result both as JSON text and as `structuredContent`; a result that is a list shall be wrapped as `{"items": [...]}`.

Covers:
- `feat~mcp~1`

### Tool errors
`req~mcp.errors~1`

If an operation fails, then the MCP server shall return a tool error carrying the operation's error message.

Covers:
- `feat~mcp~1`
