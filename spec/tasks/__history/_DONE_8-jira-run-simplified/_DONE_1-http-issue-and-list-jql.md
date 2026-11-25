# Step 1: HTTP helpers -- list JQL, issue without comments

## Goal
Point open-issue search at five newest-created unresolved issues and stop all comment retrieval in `fetch_issue_bundle_via_jira`, deleting comment-only helpers that become dead code.

## Approach
Replace `OPEN_ISSUES_JQL` with the clarified JQL (`resolution = Unresolved ORDER BY created DESC`). Callers in Step 2 use `backend.list_open_issues(limit=5)`, which passes `limit` through to `fetch_open_issues_via_jira`. Strip `fetch_issue_bundle_via_jira` down to issue GET + `IssueBundle(..., comments=[])` without calling `_paginated_issue_comments_via_session`. Remove `_paginated_issue_comments_via_session`, `_comment_body_text`, `_adf_to_plain`, `_strip_html`, `COMMENT_PAGE_SIZE`, and `COMMENT_MAX_FETCH`.

## Affected files
- `spectask_mcp/jira/http_common.py`

## Code changes (before / after)

### `spectask_mcp/jira/http_common.py` -- `OPEN_ISSUES_JQL`

**Before**

```python
OPEN_ISSUES_JQL = "resolution = Unresolved ORDER BY updated DESC"
```

Behavior: listing ordered by last update time.

**After**

```python
OPEN_ISSUES_JQL = "resolution = Unresolved ORDER BY created DESC"
```

Behavior: listing ordered by created time descending (newest created first).

### `spectask_mcp/jira/http_common.py` -- comment helpers and constants

**Before**

```python
COMMENT_PAGE_SIZE = 100
COMMENT_MAX_FETCH = 150


def _strip_html(s: str) -> str:
    t = re.sub(r"(?is)<script[^>]*>.*?</script>", "", s)
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t).strip()


def _adf_to_plain(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if node.get("type") == "text":
            return str(node.get("text", ""))
        chunks: list[str] = []
        for child in node.get("content") or []:
            chunks.append(_adf_to_plain(child))
        if node.get("type") in ("paragraph", "heading"):
            inner = "".join(chunks).strip()
            return (inner + "\n") if inner else ""
        return "".join(chunks)
    if isinstance(node, list):
        return "".join(_adf_to_plain(x) for x in node)
    return ""


def _comment_body_text(comment: dict[str, Any]) -> str:
    rb = comment.get("renderedBody")
    if isinstance(rb, str) and rb.strip():
        return _strip_html(rb)
    body = comment.get("body")
    if isinstance(body, str):
        return body.strip()
    if isinstance(body, dict):
        return _adf_to_plain(body).strip()
    return ""
```

Behavior: these helpers support comment HTML/ADF parsing; `_paginated_issue_comments_via_session` (entire function below them in the module) performs paginated `/comment` fetch.

**After**

```python
# COMMENT_PAGE_SIZE, COMMENT_MAX_FETCH, _strip_html, _adf_to_plain,
# _comment_body_text, _paginated_issue_comments_via_session removed.
```

Behavior: module no longer contains comment-parsing or comment REST pagination.

### `spectask_mcp/jira/http_common.py` -- top-level imports

**Before**

```python
import html
import re
from collections.abc import Callable
```

Behavior: `html` and `re` are only referenced by comment stripping / ADF helpers.

**After**

```python
from collections.abc import Callable
```

Behavior: drop `html` and `re` if no remaining references after helper removal.

### `spectask_mcp/jira/http_common.py` -- `fetch_issue_bundle_via_jira` tail

**Before**

```python
    comments_ordered = _paginated_issue_comments_via_session(jira, safe_key)

    return IssueBundle(key=key, summary=summary, fields=dict(fields), comments=comments_ordered)
```

Behavior: bundles include up to 150 comments from `/comment`.

**After**

```python
    return IssueBundle(key=key, summary=summary, fields=dict(fields), comments=[])
```

Behavior: bundles never query comment endpoints; comments list always empty.

## Additional actions
- Grep `spectask_mcp` for removed symbol names to ensure zero stale imports or calls.
