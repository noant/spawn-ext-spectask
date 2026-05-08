"""Shared Jira REST helpers (parsing, search, issue bundle via pycontribs ``JIRA``)."""

from __future__ import annotations

import html
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

import requests
from jira import JIRA
from jira.exceptions import JIRAError

from spectask_mcp.jira.base import JiraConnectionError
from spectask_mcp.jira.types import IssueBundle

OPEN_ISSUES_JQL = "resolution = Unresolved ORDER BY updated DESC"

JiraHttpTraceFn = Callable[[str, str, int, str], None]

COMMENT_PAGE_SIZE = 100


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
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        snippet = ""
        try:
            snippet = (e.response.text or "")[:500]
        except OSError:
            snippet = ""
        msg = f"Jira HTTP {e.response.status_code}"
        if snippet:
            msg = f"{msg}: {snippet}"
        raise JiraConnectionError(msg) from e


def _map_jira_error(exc: BaseException) -> JiraConnectionError:
    if isinstance(exc, JIRAError):
        snippet = (exc.text or "")[:500] if getattr(exc, "text", None) else ""
        code = getattr(exc, "status_code", None)
        msg = f"Jira HTTP {code}" if code is not None else str(exc)
        if snippet:
            msg = f"{msg}: {snippet}"
        return JiraConnectionError(msg)
    if isinstance(exc, requests.RequestException):
        return JiraConnectionError(str(exc))
    return JiraConnectionError(str(exc))


def fetch_issue_bundle_via_jira(
    jira: JIRA,
    issue_key: str,
    trace: JiraHttpTraceFn | None = None,
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

    comments_ordered: list[str] = []
    start_at = 0
    while True:
        try:
            comment_list = jira.comments(
                safe_key,
                expand="renderedBody",
                start_at=start_at,
                max_results=COMMENT_PAGE_SIZE,
                order_by="created",
            )
        except JIRAError as e:
            raise _map_jira_error(e) from e
        except requests.RequestException as e:
            raise JiraConnectionError(str(e)) from e

        if not comment_list:
            break
        for c in comment_list:
            raw_c = getattr(c, "raw", None)
            if isinstance(raw_c, dict):
                comments_ordered.append(_comment_body_text(raw_c))
        start_at += len(comment_list)
        if len(comment_list) < COMMENT_PAGE_SIZE:
            break

    return IssueBundle(key=key, summary=summary, fields=dict(fields), comments=comments_ordered)


def _open_issue_pairs_from_search_body(body: Any) -> list[tuple[str, str]]:
    """Parse Jira search JSON (legacy or enhanced); return (issue key, summary) pairs."""
    if not isinstance(body, dict):
        return []
    issues = body.get("issues")
    if not isinstance(issues, list):
        return []
    out: list[tuple[str, str]] = []
    for item in issues:
        if not isinstance(item, dict):
            continue
        k = item.get("key")
        if not k:
            continue
        fields = item.get("fields")
        summ = ""
        if isinstance(fields, dict):
            s = fields.get("summary")
            if s is not None:
                summ = str(s)
        out.append((str(k), summ))
    return out


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
