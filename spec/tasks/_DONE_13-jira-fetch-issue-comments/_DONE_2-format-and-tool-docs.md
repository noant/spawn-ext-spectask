# Step 2: Format comments and update tool docs

Status: Done | model: composer-2.5-fast

## Goal
Serialize `IssueComment` entries in shared plaintext output and update MCP/CLI descriptions to document comment fetch.

## Approach
1. Extend `_format_issue` with a `Comments:` section using `{n}. {author}: {body}` lines.
2. Update module docstrings in `jira_actions.py` and `run_cmd.py`.
3. Update MCP `jira_fetch` tool description in `mcp_app.py` (70-comment cap and author in output).

## Affected files
- `spectask_mcp/jira_actions.py` — module docstring, `_format_issue` (called by `query_jira` for MCP and CLI)
- `spectask_mcp/mcp_app.py` — `app.add_tool` description for `jira_fetch`
- `spectask_mcp/run_cmd.py` — module docstring

## Code changes (before / after)

### `spectask_mcp/jira_actions.py` — `_format_issue`

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
    ]
    return "\n".join(lines)
```
Issue output ends after fields JSON; no comments block.

**After**
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
    if not bundle.comments:
        lines.append("(none)")
    else:
        for i, comment in enumerate(bundle.comments, start=1):
            body = comment.body.strip() if comment.body else ""
            author = comment.author.strip() if comment.author else "unknown"
            if body:
                lines.append(f"{i}. {author}: {body}")
            else:
                lines.append(f"{i}. {author}:")
    return "\n".join(lines)
```
MCP and CLI issue detail include numbered comments with author prefix.

### `spectask_mcp/jira_actions.py` — module docstring

**Before**
```python
Plaintext formatting matches MCP jira_fetch intent: issue detail with JSON fields only
(no comments). Listing is up to five issues assigned to the current user, unresolved,
```
Documents no comment fetch.

**After**
```python
Plaintext formatting matches MCP jira_fetch intent: issue detail with JSON fields plus
up to 70 comments (author and body per line). Listing is up to five issues assigned to
the current user, unresolved,
```
Docstring matches runtime behavior.

### `spectask_mcp/mcp_app.py` — `jira_fetch` description

**Before**
```python
            description=(
                "When issue_key is omitted or not found: return the five most recently "
                "created unresolved issues as key<TAB>summary lines. "
                "When issue_key resolves to an issue: return key, summary, "
                "and fields JSON (no comments)."
            ),
```
Tool description omits comments.

**After**
```python
            description=(
                "When issue_key is omitted or not found: return the five most recently "
                "created unresolved issues as key<TAB>summary lines. "
                "When issue_key resolves to an issue: return key, summary, fields JSON, "
                "and up to 70 comments as numbered lines (author: body)."
            ),
```
MCP callers know comments and author are included.

### `spectask_mcp/run_cmd.py` — module docstring

**Before**
```python
    0 - Success; issue fields (no comments) or five-issue listing on stdout.
```
CLI help text says no comments.

**After**
```python
    0 - Success; issue fields and comments (up to 70) or five-issue listing on stdout.
```
CLI docstring aligned with MCP output.

## Additional actions
- Export `IssueComment` from `spectask_mcp/jira/__init__.py` if other modules re-export `IssueBundle` (optional parity with existing exports).
- Step 7 (after code review): update HLA paragraph that states bundles always have empty `comments`.
