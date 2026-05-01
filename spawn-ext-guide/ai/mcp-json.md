---
document: spawn-extension-mcp-json
audience: machine
encoding: utf-8
prerequisite: spawn-ext-guide/ai/core.md (global uniqueness of server names)
---

# extsrc/mcp.json — machine schema

path: `extsrc/mcp.json` (only under **extension source** `extsrc/`; not merged into arbitrary IDE JSON by hand — Spawn adapters emit IDE-specific config).

constraint: valid JSON.

format_note:

- extension uses top-level `servers` array (NOT IDE root `mcpServers` object); Spawn normalizes; adapters rewrite per IDE.

## top_level

| field | type | semantics |
|-------|------|-----------|
| servers | array | each element one MCP server; missing or `[]` → no MCP from extension |

## server_object

| field | type | required | semantics |
|-------|------|----------|-----------|
| name | string | yes | stable id; MUST be unique across ALL extensions in same target |
| transport | object | implicit default | connection; omit → parser defaults (`type` default `stdio`) |
| env | object | no | env vars; see env_semantics |
| capabilities | object | no | see capabilities_defaults |

## transport_fields

| field | default | semantics |
|-------|---------|-----------|
| type | `"stdio"` | `stdio`, `sse`, `streamable-http`, etc. per adapter mapping |
| command | — | executable for stdio |
| args | `[]` | string list |
| cwd | `"."` | working directory |
| url | — | for HTTP/SSE when type not plain stdio |

## env_value_semantics

- **A** non-object scalar, or JSON value not a mapping → user secret → IDE placeholder (never literals in repo).
- **B** mapping → optional fields:

| field | type | default | semantics |
|-------|------|---------|-----------|
| source | string | `"user"` | provenance |
| required | bool | `true` | var must be set |
| secret | bool | `false` | mask/placeholder in generated config |
| value | string \| null | null | non-secret default when secret false |

## capabilities_defaults

| field | default |
|-------|---------|
| tools | true |
| resources | false |
| prompts | false |

## validation

- `spawn extension check`: JSON parses; semantic issues (e.g. missing `name`) MAY surface when MCP is loaded for rendering.

## examples.reference_only

example_stdio_secret_object:

```json
{
  "servers": [
    {
      "name": "acme-docs-mcp",
      "transport": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@acme/mcp-server", "--stdio"],
        "cwd": "."
      },
      "env": {
        "ACME_API_TOKEN": {
          "source": "user",
          "required": true,
          "secret": true
        }
      },
      "capabilities": { "tools": true, "resources": false, "prompts": false }
    }
  ]
}
```

example_streamable_http:

```json
{
  "servers": [
    {
      "name": "acme-remote-mcp",
      "transport": { "type": "streamable-http", "url": "https://mcp.example.com/v1" },
      "capabilities": { "tools": true, "resources": false, "prompts": false }
    }
  ]
}
```

example_sse:

```json
{
  "servers": [
    {
      "name": "acme-sse-gateway",
      "transport": { "type": "sse", "url": "https://mcp.example.com/sse" }
    }
  ]
}
```

example_python_stdio:

```json
{
  "servers": [
    {
      "name": "acme-python-mcp",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["-m", "acme_mcp", "--stdio"],
        "cwd": "."
      }
    }
  ]
}
```

uv_wrapper_fragment (replace command/args as needed):

```json
"command": "uv",
"args": ["tool", "run", "acme-mcp-cli", "--stdio"]
```

example_minimal_stdio:

```json
{
  "servers": [
    {
      "name": "pack-minimal-stdio",
      "transport": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@some-scope/some-mcp-package"]
      }
    }
  ]
}
```

example_two_servers:

```json
{
  "servers": [
    {
      "name": "methodology-docs-mcp",
      "transport": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@org/mcp-docs", "--stdio"]
      }
    },
    {
      "name": "methodology-lint-mcp",
      "transport": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@org/mcp-lint", "--stdio"]
      }
    }
  ]
}
```

example_env_plain_placeholder:

```json
{
  "servers": [
    {
      "name": "pack-with-inline-env-hint",
      "transport": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@org/mcp-server"]
      },
      "env": { "ORG_API_KEY": "" }
    }
  ]
}
```

note: empty string still marks placeholder in many adapters; prefer explicit object form in example_stdio_secret_object for `required` / `secret`.
