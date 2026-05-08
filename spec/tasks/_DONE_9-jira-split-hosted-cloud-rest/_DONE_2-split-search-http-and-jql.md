# Step 2: Deployment-specific search HTTP and current-user JQL

## Goal
Move open-issue listing HTTP onto Cloud-only v3 endpoints and self-hosted-only v2 endpoint; centralize new JQL; wire both backend classes.

## Approach
1. Add `spectask_mcp/jira/jql.py` with `CURRENT_USER_OPEN_ISSUES_JQL`.
2. Add `http_cloud.py` by adapting current `fetch_open_issues_via_jira` logic (v3 URLs + same 404/410 fallback), importing JQL from `jql.py`.
3. Add `http_self_hosted.py` with a single `POST .../rest/api/2/search` path using the same JQL and JSON body fields as the legacy branch (`jql`, `startAt`, `maxResults`, `fields`).
4. Strip `OPEN_ISSUES_JQL` and `fetch_open_issues_via_jira` from `http_common.py`; keep parsing helpers and `fetch_issue_bundle_via_jira`.
5. Update `cloud.py` and `self_hosted.py` imports and `list_open_issues` bodies.
6. Update module docstring in `jira_actions.py` to describe the new JQL and "my open issues" semantics.

## Affected files
- `spectask_mcp/jira/jql.py` — new
- `spectask_mcp/jira/http_cloud.py` — new
- `spectask_mcp/jira/http_self_hosted.py` — new
- `spectask_mcp/jira/http_common.py` — remove listing constant and function
- `spectask_mcp/jira/cloud.py` — `AtlassianCloudJiraClient`
- `spectask_mcp/jira/self_hosted.py` — `SelfHostedJiraClient`
- `spectask_mcp/jira_actions.py` — docstring only

## Code changes (before / after)

### `spectask_mcp/jira/jql.py` — new module

**Before**
```text
(nothing)
```

**After**
```python
"""Shared Jira JQL fragments for listing helpers."""

CURRENT_USER_OPEN_ISSUES_JQL = (
    "assignee = currentUser() AND resolution = Unresolved ORDER BY created DESC"
)
```

Defines the listing query once for Cloud and self-hosted.

---

### `spectask_mcp/jira/http_cloud.py` — new module

**Before**
```text
(nothing)
```

**After**
```python
"""Cloud-only Jira search HTTP (REST API v3)."""

from __future__ import annotations

import requests
from jira import JIRA

from spectask_mcp.jira.base import JiraConnectionError
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    _open_issue_pairs_from_search_body,
    _raise_requests_http,
)
from spectask_mcp.jira.jql import CURRENT_USER_OPEN_ISSUES_JQL


def fetch_open_issues_cloud(
    jira: JIRA,
    limit: int,
    trace: JiraHttpTraceFn | None = None,
) -> list[tuple[str, str]]:
    del trace
    base = jira.server_url.rstrip("/")
    enhanced_url = f"{base}/rest/api/3/search/jql"
    legacy_url = f"{base}/rest/api/3/search"
    session = jira._session
    try:
        r = session.post(
            enhanced_url,
            json={
                "jql": CURRENT_USER_OPEN_ISSUES_JQL,
                "maxResults": limit,
                "fields": ["summary"],
            },
        )
    except requests.RequestException as e:
        raise JiraConnectionError(str(e)) from e

    if r.status_code in (404, 410):
        try:
            r = session.post(
                legacy_url,
                json={
                    "jql": CURRENT_USER_OPEN_ISSUES_JQL,
                    "startAt": 0,
                    "maxResults": limit,
                    "fields": ["summary"],
                },
            )
        except requests.RequestException as e:
            raise JiraConnectionError(str(e)) from e

    _raise_requests_http(r)
    return _open_issue_pairs_from_search_body(r.json())
```

Preserves Cloud behavior and enhanced-search fallback; swaps in shared JQL constant.

---

### `spectask_mcp/jira/http_self_hosted.py` — new module

**Before**
```text
(nothing)
```

**After**
```python
"""Self-hosted Jira search HTTP (REST API v2 only)."""

from __future__ import annotations

import requests
from jira import JIRA

from spectask_mcp.jira.base import JiraConnectionError
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    _open_issue_pairs_from_search_body,
    _raise_requests_http,
)
from spectask_mcp.jira.jql import CURRENT_USER_OPEN_ISSUES_JQL


def fetch_open_issues_self_hosted(
    jira: JIRA,
    limit: int,
    trace: JiraHttpTraceFn | None = None,
) -> list[tuple[str, str]]:
    del trace
    base = jira.server_url.rstrip("/")
    url = f"{base}/rest/api/2/search"
    session = jira._session
    try:
        r = session.post(
            url,
            json={
                "jql": CURRENT_USER_OPEN_ISSUES_JQL,
                "startAt": 0,
                "maxResults": limit,
                "fields": ["summary"],
            },
        )
    except requests.RequestException as e:
        raise JiraConnectionError(str(e)) from e

    _raise_requests_http(r)
    return _open_issue_pairs_from_search_body(r.json())
```

Self-hosted never calls `/rest/api/3/...` for listing.

---

### `spectask_mcp/jira/http_common.py` — trim listing-only pieces

**Before**
```python
OPEN_ISSUES_JQL = "resolution = Unresolved ORDER BY created DESC"

JiraHttpTraceFn = Callable[[str, str, int, str], None]
```

**After**
```python
JiraHttpTraceFn = Callable[[str, str, int, str], None]
```

Removes obsolete global JQL; callers import from `jql.py`.

**Before**
```python
def fetch_open_issues_via_jira(
    jira: JIRA,
    limit: int,
    trace: JiraHttpTraceFn | None = None,
) -> list[tuple[str, str]]:
    """POST /search/jql first; on 404/410 fall back to POST /search. Return (key, summary) pairs."""
    del trace  # session hook when verbose
    base = jira.server_url.rstrip("/")
    enhanced_url = f"{base}/rest/api/3/search/jql"
    legacy_url = f"{base}/rest/api/3/search"
    session = jira._session
    try:
        r = session.post(
            enhanced_url,
            json={
                "jql": OPEN_ISSUES_JQL,
                "maxResults": limit,
                "fields": ["summary"],
            },
        )
    except requests.RequestException as e:
        raise JiraConnectionError(str(e)) from e

    if r.status_code in (404, 410):
        try:
            r = session.post(
                legacy_url,
                json={
                    "jql": OPEN_ISSUES_JQL,
                    "startAt": 0,
                    "maxResults": limit,
                    "fields": ["summary"],
                },
            )
        except requests.RequestException as e:
            raise JiraConnectionError(str(e)) from e

    _raise_requests_http(r)
    return _open_issue_pairs_from_search_body(r.json())
```

Shared listing lived here for all deployments.

**After**
```text
(function removed entirely; see http_cloud.py and http_self_hosted.py)
```

Listing transport is no longer shared.

---

### `spectask_mcp/jira/cloud.py` — `AtlassianCloudJiraClient`

**Before**
```python
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    fetch_issue_bundle_via_jira,
    fetch_open_issues_via_jira,
)
```

**After**
```python
from spectask_mcp.jira.http_cloud import fetch_open_issues_cloud
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    fetch_issue_bundle_via_jira,
)
```

Cloud imports only Cloud listing helper.

**Before**
```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues_via_jira(self._jira, limit, trace=self._trace)
```

**After**
```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues_cloud(self._jira, limit, trace=self._trace)
```

---

### `spectask_mcp/jira/self_hosted.py` — `SelfHostedJiraClient`

**Before**
```python
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    fetch_issue_bundle_via_jira,
    fetch_open_issues_via_jira,
)
```

**After**
```python
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    fetch_issue_bundle_via_jira,
)
from spectask_mcp.jira.http_self_hosted import fetch_open_issues_self_hosted
```

**Before**
```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues_via_jira(self._jira, limit, trace=self._trace)
```

**After**
```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues_self_hosted(self._jira, limit, trace=self._trace)
```

---

### `spectask_mcp/jira_actions.py` — module docstring

**Before**
```python
"""Shared Jira query logic for CLI and MCP.

Plaintext formatting matches MCP jira_fetch intent: issue detail with JSON fields only
(no comments). Unresolved listing is up to five newest-created issues as ``key<TAB>summary`` lines.
```

**After**
```python
"""Shared Jira query logic for CLI and MCP.

Plaintext formatting matches MCP jira_fetch intent: issue detail with JSON fields only
(no comments). Listing is up to five issues assigned to the current user, unresolved,
newest-created first, as ``key<TAB>summary`` lines (see ``CURRENT_USER_OPEN_ISSUES_JQL`` in ``spectask_mcp.jira.jql``).
```

Documents new semantics without changing call sites.

## Additional actions
- Grep the repo for `OPEN_ISSUES_JQL` or `fetch_open_issues_via_jira` after edits; remove stale imports.
- Step 7 (separate phase): update `spec/design/hla.md` to match the split described in task overview.
