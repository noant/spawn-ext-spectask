# 2: Jira open-issue search uses enhanced JQL API

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
Restore Atlassian Cloud compatibility for open-issue listing via `POST /rest/api/3/search/jql`, and keep older self-hosted instances working by falling back to `POST /rest/api/3/search` when the enhanced route is unavailable.

## Design overview
- Affected modules: shared Jira HTTP helpers used by both Cloud and self-hosted backends.
- Files and symbols:
  - `spectask_mcp/jira/http_common.py` — function `fetch_open_issues` (two-step POST with fallback, single shared response parser); optional private helper e.g. `_open_issue_pairs_from_search_body` if that avoids duplicating the `issues` / `key` / `fields.summary` loop; constants `OPEN_ISSUES_JQL` unchanged.
  - Callers unchanged: `spectask_mcp/jira/cloud.py` (`AtlassianCloudJiraClient.list_open_issues`), `spectask_mcp/jira/self_hosted.py` (`SelfHostedJiraClient.list_open_issues`), `spectask_mcp/jira_actions.py` (`query_jira` -> `backend.list_open_issues`).
- Data flow changes: same `(key, summary)` list behavior; first page only (`maxResults` = `limit`). Enhanced request omits `startAt`; legacy request keeps `startAt: 0`. At most two HTTP attempts per listing: enhanced first, legacy only when the first response status is **404** or **410**.
- Integration points: Jira REST API v3 [Search for issues using JQL enhanced search (POST)](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-jql-post); migration context [CHANGELOG CHANGE-2046](https://developer.atlassian.com/changelog/#CHANGE-2046).

## Before -> After

### Before
- `fetch_open_issues` posts to `/rest/api/3/search` with `jql`, `startAt`, `maxResults`, `fields`.
- Atlassian Cloud returns HTTP 410 with message to migrate to `/rest/api/3/search/jql`, breaking `spectask-mcp run` (and any path that lists open issues) after connect.

### After
- `fetch_open_issues` tries `POST /rest/api/3/search/jql` first (body: `jql`, `maxResults`, `fields: ["summary"]`). If the response status is **404** or **410**, it retries once with `POST /rest/api/3/search` and the legacy body (`jql`, `startAt: 0`, `maxResults`, `fields`).
- No further attempts: do **not** chain more than one fallback. Do **not** treat **401**, **403**, **400**, **429**, or **5xx** as trigger for the other endpoint (auth, validation, rate limit, server errors must surface as today via `_raise_http` / `JiraConnectionError`).
- Response parsing is identical for both success shapes: top-level `issues` array, per-issue `key` and `fields.summary`.

## Details

### Symptom (observed)
- Command: `spectask-mcp run --issue KEY` (or any flow that invokes open-issue listing on Cloud).
- Error: `Jira HTTP 410` with JSON `errorMessages` citing removal of the old search API and directing to `/rest/api/3/search/jql`.

### Why listing runs with `--issue`
- `spectask_mcp/jira_actions.py` — `query_jira`: if `issue_key` is missing/blank, or `get_issue_bundle` returns `None` (e.g. wrong key / 404), execution falls through to `backend.list_open_issues`, which calls `fetch_open_issues`.

### Request shape and pagination
- **Enhanced** (`POST {base_url}/rest/api/3/search/jql`): JSON with `jql` (`OPEN_ISSUES_JQL`), `maxResults` (`limit`), `fields: ["summary"]`. No `startAt`. Omit `nextPageToken` on the first (and only) page for this task.
- **Legacy** (`POST {base_url}/rest/api/3/search`): JSON with `jql`, `startAt: 0`, `maxResults`, `fields: ["summary"]`.
- Ignore response extras such as `isLast` / `nextPageToken` unless a later task adds multi-page listing.

### Fallback rationale
- **Cloud:** legacy `POST /search` returns **410**; enhanced works on the first try.
- **Self-hosted (no enhanced route):** enhanced may return **404** (or **410** if Atlassian ever aligns messaging); legacy succeeds on the second try.
- **Order:** enhanced first avoids an extra failing request on Cloud on every list (legacy-first would always hit 410 on Cloud before succeeding).

### Code changes (before / after)

#### `spectask_mcp/jira/http_common.py` — `fetch_open_issues`

**Before**

```python
def fetch_open_issues(
    client: httpx.Client,
    base_url: str,
    prepare: RequestPrepare,
    limit: int,
) -> list[tuple[str, str]]:
    """POST /search with unresolved JQL; return (key, summary) pairs."""
    search_url = f"{base_url}/rest/api/3/search"
    r = _request(
        client,
        "POST",
        search_url,
        prepare,
        json={
            "jql": OPEN_ISSUES_JQL,
            "startAt": 0,
            "maxResults": limit,
            "fields": ["summary"],
        },
    )
```

**After**

```python
def fetch_open_issues(
    client: httpx.Client,
    base_url: str,
    prepare: RequestPrepare,
    limit: int,
) -> list[tuple[str, str]]:
    """List open issues: POST /search/jql, fall back to POST /search on 404/410."""
    enhanced_url = f"{base_url}/rest/api/3/search/jql"
    legacy_url = f"{base_url}/rest/api/3/search"
    r = _request(
        client,
        "POST",
        enhanced_url,
        prepare,
        json={
            "jql": OPEN_ISSUES_JQL,
            "maxResults": limit,
            "fields": ["summary"],
        },
    )
    if r.status_code in (404, 410):
        r = _request(
            client,
            "POST",
            legacy_url,
            prepare,
            json={
                "jql": OPEN_ISSUES_JQL,
                "startAt": 0,
                "maxResults": limit,
                "fields": ["summary"],
            },
        )
    _raise_http(r)
    return _open_issue_pairs_from_search_body(r.json())
```

Implement `_open_issue_pairs_from_search_body` by moving the existing post-`_raise_http` JSON loop from the current `fetch_open_issues` into a private function that returns `list[tuple[str, str]]`, so both paths share one parser.

### Verification
- Against **Atlassian Cloud**: open-issue listing succeeds on the first POST (`/search/jql`); no reliance on legacy there.
- Against **self-hosted** where enhanced returns **404** or **410**: second POST (`/search`) succeeds and listing matches previous behavior.
- Optional: `spectask-mcp run --issue VALID` still returns issue detail when the issue exists.
