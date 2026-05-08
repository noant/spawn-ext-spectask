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
