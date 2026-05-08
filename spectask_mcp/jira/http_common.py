"""Shared httpx helpers: client factory and Jira REST API v3 calls."""

from __future__ import annotations

import html
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import quote

import httpx

from spectask_mcp.config import ProxySection, SpectaskLocalConfig
from spectask_mcp.jira.base import JiraConnectionError
from spectask_mcp.jira.types import IssueBundle

OPEN_ISSUES_JQL = "resolution = Unresolved ORDER BY updated DESC"

RequestPrepare = Callable[[dict[str, Any]], None] | None
JiraHttpTraceFn = Callable[[str, str, int, str], None]

COMMENT_PAGE_SIZE = 100


def _socks_proxy_url(proxy: ProxySection) -> str:
    host = proxy.socks_host.strip()
    port = int(proxy.socks_port)
    user = proxy.socks_username
    password = proxy.socks_password
    if user or password:
        u = quote(user, safe="")
        p = quote(password, safe="")
        return f"socks5://{u}:{p}@{host}:{port}"
    return f"socks5://{host}:{port}"


def build_httpx_client(cfg: SpectaskLocalConfig) -> httpx.Client:
    """Build a client with TLS verify and optional SOCKS5 proxy from config."""
    verify = not cfg.jira.ignore_tls
    proxy: str | None = None
    if cfg.proxy.enabled:
        proxy = _socks_proxy_url(cfg.proxy)
    return httpx.Client(
        proxy=proxy,
        verify=verify,
        timeout=httpx.Timeout(60.0),
        follow_redirects=True,
    )


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


def _raise_http(resp: httpx.Response) -> None:
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        snippet = ""
        try:
            snippet = (e.response.text or "")[:500]
        except OSError:
            snippet = ""
        msg = f"Jira HTTP {e.response.status_code}"
        if snippet:
            msg = f"{msg}: {snippet}"
        raise JiraConnectionError(msg) from e


def fetch_issue_bundle(
    client: httpx.Client,
    base_url: str,
    issue_key: str,
    prepare: RequestPrepare,
    trace: JiraHttpTraceFn | None = None,
) -> IssueBundle | None:
    """GET issue with renderedFields; comments paginated with renderedBody when available."""
    safe_key = quote(issue_key, safe="")
    issue_url = f"{base_url}/rest/api/3/issue/{safe_key}"
    r_issue = _request(
        client,
        "GET",
        issue_url,
        prepare,
        trace=trace,
        params={"expand": "renderedFields"},
    )
    if r_issue.status_code == 404:
        return None
    _raise_http(r_issue)
    issue = r_issue.json()
    key = str(issue.get("key", issue_key))
    fields = issue.get("fields")
    if not isinstance(fields, dict):
        fields = {}
    summary_raw = fields.get("summary")
    summary = "" if summary_raw is None else str(summary_raw)

    comments_ordered: list[str] = []
    start_at = 0
    while True:
        c_url = f"{base_url}/rest/api/3/issue/{safe_key}/comment"
        r_c = _request(
            client,
            "GET",
            c_url,
            prepare,
            trace=trace,
            params={
                "startAt": start_at,
                "maxResults": COMMENT_PAGE_SIZE,
                "expand": "renderedBody",
                "orderBy": "created",
            },
        )
        _raise_http(r_c)
        payload = r_c.json()
        batch = payload.get("comments")
        if not isinstance(batch, list) or not batch:
            break
        for c in batch:
            if isinstance(c, dict):
                comments_ordered.append(_comment_body_text(c))
        start_at += len(batch)
        total = payload.get("total")
        if isinstance(total, int) and start_at >= total:
            break
        if len(batch) < COMMENT_PAGE_SIZE:
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
    if r.status_code in (404, 410):
        r = _request(
            client,
            "POST",
            legacy_url,
            prepare,
            trace=trace,
            json={
                "jql": OPEN_ISSUES_JQL,
                "startAt": 0,
                "maxResults": limit,
                "fields": ["summary"],
            },
        )
    _raise_http(r)
    return _open_issue_pairs_from_search_body(r.json())
