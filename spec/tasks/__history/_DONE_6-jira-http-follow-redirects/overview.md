# 6: Jira HTTP client follows redirects

## Source seed
- Path: none

## Status
- [x] Spec created
- [x] Self spec review passed
- [x] Spec review passed
- [x] Code implemented
- [x] Self code review passed
- [x] Code review passed
- [x] Design documents updated

## Goal
All Jira REST calls issued through the shared httpx client must automatically follow HTTP redirects (for example 302) instead of treating them as terminal responses.

## Design overview
- Affected modules: `spectask_mcp.jira.http_common`
- Files & symbols:
  - `spectask_mcp/jira/http_common.py` — function `build_httpx_client` (instantiates `httpx.Client`); all Jira traffic uses this factory via `AtlassianCloudJiraClient` and `SelfHostedJiraClient`.
- Data flow changes: outbound requests still go through `_request`/`client.request`; the client will resolve redirect chains before `status_code`, body, and trace hooks see the outcome.
- Integration points: Atlassian Cloud and self-hosted backends both reuse `build_httpx_client`; no separate change in `cloud.py` or `self_hosted.py`.

## Before → After

### Before
- `httpx.Client` is created without `follow_redirects`; library default is `False`, so a 302/301 response is returned to callers and `raise_for_status` surfaces it as an error.

### After
- `httpx.Client` is created with `follow_redirects=True` so redirect responses are followed up to httpx default redirect limits; final response drives success/failure and tracing.

## Details
- Dependency: `httpx>=0.27` (see `pyproject.toml`); `Client` supports `follow_redirects` and default `max_redirects` (httpx built-in cap on chain length).
- GET issue and comment pagination, and POST search, all use the same client; enabling redirects at the client is the minimal, consistent fix for misconfigured base URLs or gateway behavior that issues redirects.
- Verbose HTTP trace (`trace` callback in `_request`) logs the request method and the original `url` argument; after this change the response status and body reflect the final hop after redirects (same as today for non-redirect responses).

## Code changes (single step; no subtask files)

### `spectask_mcp/jira/http_common.py` — `build_httpx_client`

**Before**

```python
    return httpx.Client(
        proxy=proxy,
        verify=verify,
        timeout=httpx.Timeout(60.0),
    )
```

Behavior: redirects are not followed; 3xx may raise in `_raise_http`.

**After**

```python
    return httpx.Client(
        proxy=proxy,
        verify=verify,
        timeout=httpx.Timeout(60.0),
        follow_redirects=True,
    )
```

Behavior: 301/302/307/308 (and other redirect codes httpx follows by policy) are resolved automatically before status checks.
