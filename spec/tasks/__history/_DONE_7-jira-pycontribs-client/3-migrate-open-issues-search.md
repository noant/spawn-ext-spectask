# Step 3: Migrate open-issues listing (JQL search)

## Goal
Implement `JiraBackend.list_open_issues` using pycontribs so the unresolved listing matches today: same `OPEN_ISSUES_JQL`, same `(key, summary)` pairs up to `limit`, and equivalent fallback when the enhanced search API is unavailable.

## Approach
1. Prefer the library’s high-level JQL search (e.g. `search_issues` or documented equivalent) with `jql_str=OPEN_ISSUES_JQL`, `maxResults=limit`, `fields=["summary"]`.
2. If the library targets only legacy `POST /search` but the instance requires `POST /rest/api/3/search/jql`, use the underlying authenticated session to reproduce the current enhanced-then-legacy sequence from `fetch_open_issues` (same JSON bodies as in the current implementation).
3. Reuse `_open_issue_pairs_from_search_body` when the response body shape is still the Jira search JSON dict; otherwise map library return type to `list[tuple[str, str]]` without changing downstream ranking in `jira_actions.query_jira`.
4. Map failures to `JiraConnectionError` consistently with step 2.

## Affected files
- `spectask_mcp/jira/self_hosted.py` — `list_open_issues`
- `spectask_mcp/jira/cloud.py` — `list_open_issues`
- `spectask_mcp/jira/http_common.py` — `fetch_open_issues`, `_open_issue_pairs_from_search_body` (parser may stay)

## Code changes (before / after)

### `spectask_mcp/jira/http_common.py` — `fetch_open_issues`

**Before**

```python
def fetch_open_issues(
    client: httpx.Client,
    base_url: str,
    prepare: RequestPrepare,
    limit: int,
    trace: JiraHttpTraceFn | None = None,
) -> list[tuple[str, str]]:
    """POST /search/jql first; on 404/410 fall back to POST /search. Return (key, summary) pairs."""
    enhanced_url = f"{base_url}/rest/api/3/search/jql"
    legacy_url = f"{base_url}/rest/api/3/search"
    r = _request(
        client,
        "POST",
        enhanced_url,
        prepare,
        trace=trace,
        json={
            "jql": OPEN_ISSUES_JQL,
            "maxResults": limit,
            "fields": ["summary"],
        },
    )
```

Behavior: explicit dual-endpoint strategy.

**After**

```python
def fetch_open_issues_via_jira(
    jira: JIRA,
    limit: int,
    trace: JiraHttpTraceFn | None = None,
) -> list[tuple[str, str]]:
    ...
```

Behavior: same user-visible listing; internal calls use `jira` APIs or session POSTs that preserve enhanced-then-legacy semantics if needed.

### `spectask_mcp/jira/cloud.py` — `list_open_issues`

**Before**

```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues(
            self._client, self._base, self._prepare, limit, trace=self._trace
        )
```

Behavior: httpx path.

**After**

```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues_via_jira(
            self._jira, limit, trace=self._trace
        )
```

Behavior: pycontribs path only.

## Additional actions
- Run `spectask-mcp run` without `--issue` and compare stdout to pre-migration run against the same Jira (spot-check keys and summaries).
