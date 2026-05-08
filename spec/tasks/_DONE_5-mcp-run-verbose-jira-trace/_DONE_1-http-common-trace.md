# Step 1: HTTP trace hook in http_common

## Goal
Add an optional per-response trace callback to shared Jira HTTP helpers so every `client.request` can report method, URL, status, and body text.

## Approach
- Introduce a `Protocol` or `Callable` type alias for the trace function `(method, url, status_code, body_str) -> None`.
- Extend `_request` to accept optional `trace`; after a successful `client.request`, read `resp.text`, invoke `trace` if set, then return `resp`.
- Extend `fetch_issue_bundle` and `fetch_open_issues` with optional `trace` defaulted to `None`, passing it into each `_request` invocation (issue GET, comment pages, search POST(s)).
- Do not log request headers or kwargs that might contain secrets.

## Affected files
- `spectask_mcp/jira/http_common.py`

## Code changes (before / after)

### `spectask_mcp/jira/http_common.py` — types and `_request` trace

**Before**
```python
RequestPrepare = Callable[[dict[str, Any]], None] | None
```

**After**
```python
RequestPrepare = Callable[[dict[str, Any]], None] | None
JiraHttpTraceFn = Callable[[str, str, int, str], None]
```

Behavior: names the callback type for method, URL, status, body.

**Before**
```python
def _request(
    client: httpx.Client,
    method: str,
    url: str,
    prepare: RequestPrepare,
    **kwargs: Any,
) -> httpx.Response:
    req_kwargs = dict(kwargs)
    if prepare is not None:
        prepare(req_kwargs)
    try:
        return client.request(method, url, **req_kwargs)
    except httpx.RequestError as e:
        raise JiraConnectionError(str(e)) from e
```

**After**
```python
def _request(
    client: httpx.Client,
    method: str,
    url: str,
    prepare: RequestPrepare,
    *,
    trace: JiraHttpTraceFn | None = None,
    **kwargs: Any,
) -> httpx.Response:
    req_kwargs = dict(kwargs)
    if prepare is not None:
        prepare(req_kwargs)
    try:
        resp = client.request(method, url, **req_kwargs)
    except httpx.RequestError as e:
        raise JiraConnectionError(str(e)) from e
    if trace is not None:
        try:
            body = resp.text
        except OSError:
            body = ""
        trace(method, url, resp.status_code, body)
    return resp
```

Behavior: after each response, optional trace receives full status and body; failures before response still raise as today.

### `spectask_mcp/jira/http_common.py` — `fetch_issue_bundle` signature and calls

**Before**
```python
def fetch_issue_bundle(
    client: httpx.Client,
    base_url: str,
    issue_key: str,
    prepare: RequestPrepare,
) -> IssueBundle | None:
```

**After**
```python
def fetch_issue_bundle(
    client: httpx.Client,
    base_url: str,
    issue_key: str,
    prepare: RequestPrepare,
    trace: JiraHttpTraceFn | None = None,
) -> IssueBundle | None:
```

Behavior: callers can pass trace through; default preserves current behavior.

**Before** (first `_request` inside `fetch_issue_bundle`)
```python
    r_issue = _request(
        client,
        "GET",
        issue_url,
        prepare,
        params={"expand": "renderedFields"},
    )
```

**After**
```python
    r_issue = _request(
        client,
        "GET",
        issue_url,
        prepare,
        trace=trace,
        params={"expand": "renderedFields"},
    )
```

Repeat the same `trace=trace` addition for every `_request` call in `fetch_issue_bundle` (comment pagination loop) and in `fetch_open_issues` (initial POST, optional fallback POST).

### `spectask_mcp/jira/http_common.py` — `fetch_open_issues` signature

**Before**
```python
def fetch_open_issues(
    client: httpx.Client,
    base_url: str,
    prepare: RequestPrepare,
    limit: int,
) -> list[tuple[str, str]]:
```

**After**
```python
def fetch_open_issues(
    client: httpx.Client,
    base_url: str,
    prepare: RequestPrepare,
    limit: int,
    trace: JiraHttpTraceFn | None = None,
) -> list[tuple[str, str]]:
```

Behavior: search and legacy fallback both report through the same trace.

## Additional actions
- None.
