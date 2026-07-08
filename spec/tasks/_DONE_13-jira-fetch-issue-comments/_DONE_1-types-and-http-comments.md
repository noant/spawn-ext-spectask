# Step 1: Types and HTTP comment fetch

Status: Done | model: composer-2.5-fast

## Goal
Restore paginated Jira comment loading (max 70, author plus body) in shared HTTP helpers and populate `IssueBundle.comments`.

## Approach
1. Add `IssueComment(author, body)` in `types.py`; change `IssueBundle.comments` type.
2. Restore comment parsing helpers and `_paginated_issue_comments_via_session` in `http_common.py` from commit `9385221`, with `COMMENT_MAX_FETCH = 70`, `_comment_author_name`, and `IssueComment` mapping.
3. Call pagination from `fetch_issue_bundle_via_jira` after issue load; map each REST comment dict to `IssueComment`.
4. Keep 404 on missing issue as `None`; 404 on comment endpoint returns empty list (issue with no comment resource).

## Affected files
- `spectask_mcp/jira/types.py` — `IssueComment`, `IssueBundle`
- `spectask_mcp/jira/http_common.py` — imports, comment helpers, `_paginated_issue_comments_via_session`, `fetch_issue_bundle_via_jira`

## Code changes (before / after)

### `spectask_mcp/jira/types.py` — `IssueComment`, `IssueBundle.comments`

**Before**
```python
@dataclass
class IssueBundle:
    """One issue with all comments, for MCP/CLI serialization."""

    key: str
    summary: str
    fields: dict[str, Any]
    comments: list[str]
```
Holds comment bodies as plain strings; today always empty at runtime.

**After**
```python
@dataclass
class IssueComment:
    """One Jira issue comment for MCP/CLI serialization."""

    author: str
    body: str


@dataclass
class IssueBundle:
    """One issue with comments, for MCP/CLI serialization."""

    key: str
    summary: str
    fields: dict[str, Any]
    comments: list[IssueComment]
```
Each comment carries author display name and plain-text body.

### `spectask_mcp/jira/http_common.py` — imports and `IssueComment` type import

**Before**
```python
from collections.abc import Callable
from typing import Any
from urllib.parse import quote
```
```python
from spectask_mcp.jira.types import IssueBundle
```
No `html`/`re` imports; only `IssueBundle` imported from types.

**After**
```python
import html
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import quote
```
```python
from spectask_mcp.jira.types import IssueBundle, IssueComment
```
Imports needed for HTML/ADF comment body parsing and typed comment rows.

### `spectask_mcp/jira/http_common.py` — constants and `_comment_author_name` (new)

**Before**
```python
JiraHttpTraceFn = Callable[[str, str, int, str], None]
```
No comment constants or author helper.

**After**
```python
JiraHttpTraceFn = Callable[[str, str, int, str], None]

COMMENT_PAGE_SIZE = 100
COMMENT_MAX_FETCH = 70


def _comment_author_name(comment: dict[str, Any]) -> str:
    author = comment.get("author")
    if isinstance(author, dict):
        for key in ("displayName", "name", "key"):
            val = author.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
    return "unknown"
```
Caps fetch at 70 comments; resolves author from Jira comment JSON.

### `spectask_mcp/jira/http_common.py` — `_strip_html`, `_adf_to_plain`, `_comment_body_text` (restore)

**Before**
```python
def _raise_requests_http(resp: requests.Response) -> None:
```
No comment body parsing helpers before HTTP error mapping.

**After**
```python
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


def _raise_requests_http(resp: requests.Response) -> None:
```
Plain-text comment bodies from rendered HTML, string body, or ADF.

### `spectask_mcp/jira/http_common.py` — `_paginated_issue_comments_via_session` (restore, adapted)

**Before**
```python
    return JiraConnectionError(str(exc))


def fetch_issue_bundle_via_jira(
```
No comment pagination helper between `_map_jira_error` and issue fetch.

**After**
```python
def _paginated_issue_comments_via_session(jira: JIRA, safe_key: str) -> list[IssueComment]:
    """Fetch up to COMMENT_MAX_FETCH comments; when truncated, keep the newest window."""
    session = jira._session
    url = jira._get_latest_url(f"issue/{safe_key}/comment")
    params_base: dict[str, Any] = {
        "expand": "renderedBody",
        "orderBy": "created",
    }

    try:
        r_probe = session.get(
            url,
            params={
                **params_base,
                "startAt": 0,
                "maxResults": 1,
            },
        )
    except requests.RequestException as e:
        raise JiraConnectionError(str(e)) from e
    if r_probe.status_code == 404:
        return []
    _raise_requests_http(r_probe)

    envelope = r_probe.json()
    raw_total = envelope.get("total")
    if isinstance(raw_total, int) and raw_total <= 0:
        return []

    if isinstance(raw_total, int):
        take = min(COMMENT_MAX_FETCH, raw_total)
        start_at = max(0, raw_total - take)
        out: list[IssueComment] = []
        cursor = start_at
        max_pages = (take + COMMENT_PAGE_SIZE - 1) // COMMENT_PAGE_SIZE + 2
        for _ in range(max_pages):
            if len(out) >= take:
                break
            need = take - len(out)
            page_sz = min(COMMENT_PAGE_SIZE, need)
            try:
                r = session.get(
                    url,
                    params={
                        **params_base,
                        "startAt": cursor,
                        "maxResults": page_sz,
                    },
                )
            except requests.RequestException as e:
                raise JiraConnectionError(str(e)) from e
            _raise_requests_http(r)
            payload = r.json()
            batch = payload.get("comments")
            if not isinstance(batch, list) or not batch:
                break
            for c in batch:
                if len(out) >= take:
                    break
                if isinstance(c, dict):
                    out.append(
                        IssueComment(
                            author=_comment_author_name(c),
                            body=_comment_body_text(c),
                        )
                    )
            cursor += len(batch)
            if len(batch) < page_sz:
                break
        return out

    out_fb: list[IssueComment] = []
    cursor_fb = 0
    for _ in range(COMMENT_MAX_FETCH + 5):
        if len(out_fb) >= COMMENT_MAX_FETCH:
            break
        try:
            r = session.get(
                url,
                params={
                    **params_base,
                    "startAt": cursor_fb,
                    "maxResults": min(
                        COMMENT_PAGE_SIZE,
                        COMMENT_MAX_FETCH - len(out_fb),
                    ),
                },
            )
        except requests.RequestException as e:
            raise JiraConnectionError(str(e)) from e
        if r.status_code == 404:
            break
        _raise_requests_http(r)
        payload = r.json()
        batch = payload.get("comments")
        if not isinstance(batch, list) or not batch:
            break
        for c in batch:
            if len(out_fb) >= COMMENT_MAX_FETCH:
                break
            if isinstance(c, dict):
                out_fb.append(
                    IssueComment(
                        author=_comment_author_name(c),
                        body=_comment_body_text(c),
                    )
                )
        cursor_fb += len(batch)
        total_fb = payload.get("total")
        if isinstance(total_fb, int) and cursor_fb >= total_fb:
            break
        if len(batch) < COMMENT_PAGE_SIZE:
            break
    return out_fb


def fetch_issue_bundle_via_jira(
```
Paginates `/comment` via pycontribs session; tail slice when `total > 70`; returns oldest-to-newest within the window.

### `spectask_mcp/jira/http_common.py` — `fetch_issue_bundle_via_jira`

**Before**
```python
) -> IssueBundle | None:
    """Load issue with renderedFields; comments are not fetched (always empty)."""
    del trace  # traced via session hook when verbose
    safe_key = quote(issue_key, safe="")
    try:
        issue = jira.issue(safe_key, expand="renderedFields")
    except JIRAError as e:
        if e.status_code == 404:
            return None
        raise _map_jira_error(e) from e
    except requests.RequestException as e:
        raise JiraConnectionError(str(e)) from e

    raw = issue.raw
    if not isinstance(raw, dict):
        raw = {}
    key = str(raw.get("key", issue_key))
    fields = raw.get("fields")
    if not isinstance(fields, dict):
        fields = {}
    summary_raw = fields.get("summary")
    summary = "" if summary_raw is None else str(summary_raw)

    return IssueBundle(key=key, summary=summary, fields=dict(fields), comments=[])
```
Issue fetch only; comments list always empty.

**After**
```python
) -> IssueBundle | None:
    """Load issue with renderedFields; paginate comments with renderedBody when available."""
    del trace  # traced via session hook when verbose
    safe_key = quote(issue_key, safe="")
    try:
        issue = jira.issue(safe_key, expand="renderedFields")
    except JIRAError as e:
        if e.status_code == 404:
            return None
        raise _map_jira_error(e) from e
    except requests.RequestException as e:
        raise JiraConnectionError(str(e)) from e

    raw = issue.raw
    if not isinstance(raw, dict):
        raw = {}
    key = str(raw.get("key", issue_key))
    fields = raw.get("fields")
    if not isinstance(fields, dict):
        fields = {}
    summary_raw = fields.get("summary")
    summary = "" if summary_raw is None else str(summary_raw)

    comments_ordered = _paginated_issue_comments_via_session(jira, safe_key)

    return IssueBundle(
        key=key,
        summary=summary,
        fields=dict(fields),
        comments=comments_ordered,
    )
```
Issue detail bundle includes up to 70 comments with author and body.

## Additional actions
- Manual smoke: `spectask-mcp run --issue <KEY> --verbose` shows GETs to `.../comment` and a populated `Comments:` block when the issue has comments (formatting verified in step 2).
