# Step 4: Stdio MCP server with conditional tools

## Goal
Expose MCP stdio transport; register **zero** tools when config absent/invalid; when valid register one tool executing Jira lookup rules.

## Approach
Implement `spectask_mcp/mcp_app.py`:
- `def run_stdio() -> int`: instantiate `FastMCP` or `Server` pattern from official `mcp` package; attach stdio streams.
- `_config_or_none()`, `_describe_no_tools_startup()` logged at INFO on stderr acceptable (no secrets).
- `@mcp.tool()` name e.g. `jira_fetch` accepting optional `issue_key: str | None`. Handler: loads config fresh each call optional (or caches read-only singleton); builds backend via factory; executes same branching as CLI `run_once` semantics.
Use structured `TextContent` / JSON payloads per SDK conventions; failures return user-facing plain text in MCP result (not traceback).

When no config: omit tool registration handlers entirely (still run server loop answering `initialize`/`list_tools` empty set).

## Affected files
- `spectask_mcp/mcp_app.py` (new)
- Optionally `spectask_mcp/cli.py` already imports — no change unless signature drift

## Code changes (before / after)

### `spectask_mcp/mcp_app.py` — stdio MCP (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""Stdio MCP: optional Jira tools when spec/.config/config.yaml is valid."""

from __future__ import annotations


def run_stdio() -> int:
    ...
```

Behavior:
- Validates config via `load_optional_config(config_path());` builds tool list dynamically.
- If `issue_key` present and backend returns bundle: stringify full payload + concatenated comments.
- If absent or lookup returns None: `list_open_issues` output enumerated.
- On `JiraConnectionError`: MCP tool returns error text "`Jira server unreachable:` ...".

## Additional actions
- Read current `mcp` Python SDK README via Context7 or package docs during implementation — tool decorator names differ by version.
