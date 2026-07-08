# Step 2: MCP plain formatter and mcp_app wiring

Status: Done | model: composer-2.5-fast

## Goal
Add MCP-only plain-text formatting and route `jira_fetch` through it; leave CLI `query_jira` / `_format_issue` unchanged.

## Approach
1. Add `_format_issue_mcp(bundle: IssueBundle) -> str` with sections from overview Details template.
2. Add `query_jira_for_mcp(cfg, issue_key, trace=None) -> str` mirroring `query_jira` control flow but calling `_format_issue_mcp` on success.
3. Update `_jira_fetch_impl` and tool description in `mcp_app.py`.
4. Do not change `run_cmd.py` or `_format_issue` (CLI keeps Fields JSON and numbered comments).

## Affected files
- `spectask_mcp/jira_actions.py` — `_format_issue_mcp`, `query_jira_for_mcp`
- `spectask_mcp/mcp_app.py` — `_jira_fetch_impl`, `jira_fetch` description

## Code changes (before / after)

### `spectask_mcp/jira_actions.py` — `_format_issue_mcp` (new)

**Before**
```python
def _format_issue(bundle: IssueBundle) -> str:
    fields_json = json.dumps(bundle.fields, indent=2, sort_keys=True, default=str)
    lines = [
        bundle.key,
        f"Summary: {bundle.summary}",
        "",
        "Fields:",
        fields_json,
        "",
        "Comments:",
    ]
    ...
    return "\n".join(lines)
```
Only `_format_issue` exists in this module; MCP routing still uses it via `mcp_app._jira_fetch_impl`.

**After**
```python
def _format_issue_mcp(bundle: IssueBundle) -> str:
    lines = [
        bundle.key,
        f"Summary: {bundle.summary}",
        "",
        "Description:",
        bundle.description.strip() if bundle.description.strip() else "(none)",
        "",
    ]
    if bundle.labels:
        lines.append(f"Labels: {', '.join(bundle.labels)}")
    else:
        lines.append("Labels: (none)")
    lines.extend(["", "Comments:"])
    if not bundle.comments:
        lines.append("(none)")
    else:
        for comment in bundle.comments:
            body = comment.body.strip() if comment.body else ""
            author = comment.author.strip() if comment.author else "unknown"
            lines.append(f"{author}: {body}" if body else f"{author}:")
    return "\n".join(lines)
```
MCP plain sections only; comments without numeric prefix.

### `spectask_mcp/jira_actions.py` — `query_jira_for_mcp` (new)

**Before**
```python
def query_jira(
    cfg: SpectaskLocalConfig,
    issue_key: str | None,
    trace: JiraHttpTraceFn | None = None,
) -> str:
    backend = backend_from_config(cfg, trace=trace)
    try:
        key = issue_key.strip() if isinstance(issue_key, str) else None
        if not key:
            key = None

        pairs = backend.list_open_issues(limit=5)
        if key is not None:
            bundle = backend.get_issue_bundle(key)
            if bundle is not None:
                return _format_issue(bundle)
        return _format_list(pairs)
    finally:
        close = getattr(backend, "close", None)
        if callable(close):
            close()
```
No MCP-specific query entry point; `mcp_app._jira_fetch_impl` imports this function.

**After**
```python
def query_jira_for_mcp(
    cfg: SpectaskLocalConfig,
    issue_key: str | None,
    trace: JiraHttpTraceFn | None = None,
) -> str:
    backend = backend_from_config(cfg, trace=trace)
    try:
        key = issue_key.strip() if isinstance(issue_key, str) else None
        if not key:
            key = None

        pairs = backend.list_open_issues(limit=5)
        if key is not None:
            bundle = backend.get_issue_bundle(key)
            if bundle is not None:
                return _format_issue_mcp(bundle)
        return _format_list(pairs)
    finally:
        close = getattr(backend, "close", None)
        if callable(close):
            close()
```
Same branching as `query_jira`; listing unchanged; issue detail uses MCP formatter.

### `spectask_mcp/mcp_app.py` — `_jira_fetch_impl` import and call

**Before**
```python
from spectask_mcp.jira_actions import query_jira
...
        return query_jira(cfg, issue_key)
```
MCP uses CLI formatter path.

**After**
```python
from spectask_mcp.jira_actions import query_jira_for_mcp
...
        return query_jira_for_mcp(cfg, issue_key)
```
MCP tool returns plain-text issue shape.

### `spectask_mcp/mcp_app.py` — `jira_fetch` description

**Before**
```python
            description=(
                "When issue_key is omitted or not found: return the five most recently "
                "created unresolved issues as key<TAB>summary lines. "
                "When issue_key resolves to an issue: return key, summary, fields JSON, "
                "and up to 70 comments as numbered lines (author: body)."
            ),
```
Promises fields JSON and numbered comments.

**After**
```python
            description=(
                "When issue_key is omitted or not found: return the five most recently "
                "created unresolved issues as key<TAB>summary lines. "
                "When issue_key resolves to an issue: return plain text with key, summary, "
                "description, labels, and up to 70 comments (author: body per line)."
            ),
```
Documents MCP plain output (no Fields JSON).

## Additional actions
- Step 7: update HLA paragraph to split MCP plain output vs CLI fields JSON.
- Optional: one line in `jira_actions` module docstring noting MCP vs CLI formatters.
