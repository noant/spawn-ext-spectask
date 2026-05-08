"""Build a configured pycontribs ``JIRA`` client from Spectask local config."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from jira import JIRA

from spectask_mcp.config import ProxySection, SpectaskLocalConfig
from spectask_mcp.jira.http_common import JiraHttpTraceFn


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


def _attach_jira_verbose_trace(jira: JIRA, trace: JiraHttpTraceFn) -> None:
    session = jira._session

    def _hook(resp: Any, **kwargs: Any) -> None:
        try:
            body = resp.text
        except OSError:
            body = ""
        trace(resp.request.method, resp.url, resp.status_code, body)

    session.hooks["response"].append(_hook)


def connect_jira_client(
    cfg: SpectaskLocalConfig,
    *,
    trace: JiraHttpTraceFn | None = None,
) -> JIRA:
    """Return an authenticated ``JIRA`` with TLS, optional SOCKS proxy, and 60s timeout."""
    verify = not cfg.jira.ignore_tls
    proxies: dict[str, str] | None = None
    if cfg.proxy.enabled:
        url = _socks_proxy_url(cfg.proxy)
        proxies = {"http": url, "https": url}

    base_kw: dict[str, Any] = {
        "server": cfg.jira.address.rstrip("/"),
        "options": {"verify": verify},
        "timeout": 60.0,
        "max_retries": 3,
        "proxies": proxies,
    }

    if cfg.jira.type == "self_hosted":
        if not cfg.jira.pat_token:
            raise ValueError("self_hosted Jira requires pat_token")
        client = JIRA(token_auth=cfg.jira.pat_token.strip(), **base_kw)
    elif cfg.jira.type == "atlassian_cloud":
        if not cfg.jira.email or not cfg.jira.api_token:
            raise ValueError("atlassian_cloud Jira requires email and api_token")
        client = JIRA(
            basic_auth=(
                cfg.jira.email.strip(),
                cfg.jira.api_token.strip(),
            ),
            **base_kw,
        )
    else:
        raise ValueError(f"unknown jira.type: {cfg.jira.type!r}")

    if trace is not None:
        _attach_jira_verbose_trace(client, trace)

    return client
