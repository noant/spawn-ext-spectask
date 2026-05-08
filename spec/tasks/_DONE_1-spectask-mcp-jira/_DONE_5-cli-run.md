# Step 5: `run` subcommand output

## Goal
Reuse Jira backends to print fetched issue/list to stdout exactly once (`spectask-mcp run [--issue KEY]`).

## Approach
Implement `spectask_mcp/run_cmd.py` with `run_once(*, issue_key: str | None) -> int` mirroring MCP tool semantics for consistency (shared helper `_execute_query(key: str | None) -> Result` extracted to `spectask_mcp/jira_actions.py` if duplication otherwise). Stdout formatting: newline-delimited key/summary pairs for listings; fenced plain text block matching MCP output optional; exit code non-zero only on missing config (`2`), connection errors (`3`), usage errors (`1`).

## Affected files
- `spectask_mcp/run_cmd.py` (new)
- `spectask_mcp/jira_actions.py` (new, optional refactor target)

## Code changes (before / after)

### `spectask_mcp/run_cmd.py` — CLI one-shot (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""One-shot CLI fetch."""

from __future__ import annotations


def run_once(issue_key: str | None) -> int:
    """Load config from spec/.config; print issue or listing; exit code conventions."""
```

Behavior prints human-readable summaries; aligns with MCP tool content.

### Shared helper (preferred if MCP duplicates logic)

### `spectask_mcp/jira_actions.py` — `query_jira(...)`

**Before**
```python
(file absent)
```

**After**
```python
def query_jira(cfg, issue_key: str | None) -> str:
    """Return plaintext body suitable for MCP and CLI reuse."""
```
Behavior: encapsulates branching for found issue vs fallback list vs unreachable.

## Additional actions
- Decide exit codes in implementation README comment inside module docstring — not standalone doc file.

