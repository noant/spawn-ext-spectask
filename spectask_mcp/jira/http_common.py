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


def _paginated_issue_comments_via_session(jira: JIRA, safe_key: str) -> list[str]:
    """Fetch up to COMMENT_MAX_FETCH comments, preferring newest when the thread is longer.

    Uses ``total`` from the comment index to compute ``startAt`` so we slice the tail,
    preserving chronological order oldest-to-newest in the returned list.

    Fallback (no numeric ``total``): scan from the beginning and stop after COMMENT_MAX_FETCH.
    """
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
        out: list[str] = []
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
                    out.append(_comment_body_text(c))
            cursor += len(batch)
            if len(batch) < page_sz:
                break
        return out

    # No reliable total: cap from the start of the thread (up to COMMENT_MAX_FETCH).
    out_fb: list[str] = []
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
                out_fb.append(_comment_body_text(c))
        cursor_fb += len(batch)
        total_fb = payload.get("total")
        if isinstance(total_fb, int) and cursor_fb >= total_fb:
            break
        if len(batch) < COMMENT_PAGE_SIZE:
            break
    return out_fb


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

    comments_ordered = _paginated_issue_comments_via_session(jira, safe_key)

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
