"""Load optional Jira config from spec/.config/config.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import yaml

JiraType = Literal["self_hosted", "atlassian_cloud"]


@dataclass
class ProxySection:
    enabled: bool
    socks_host: str
    socks_port: int
    socks_username: str
    socks_password: str
    # If True, use socks5h so the proxy resolves hostnames (not the local OS).
    remote_dns: bool = False


@dataclass
class JiraSection:
    type: JiraType
    address: str
    ignore_tls: bool
    pat_token: str | None
    email: str | None
    api_token: str | None


@dataclass
class SpectaskLocalConfig:
    jira: JiraSection
    proxy: ProxySection


def resolve_workspace_with_spec(start: Path | None = None) -> Path | None:
    """Walk parents from start or cwd; return first directory that has subdirectory ./spec."""
    cur = (start if start is not None else Path.cwd()).resolve()
    while True:
        spec_dir = cur / "spec"
        try:
            if spec_dir.is_dir():
                return cur
        except OSError:
            pass
        if cur == cur.parent:
            break
        cur = cur.parent
    return None


def config_yaml_path(workspace: Path) -> Path:
    """`<workspace>/spec/.config/config.yaml` (call only when workspace is not None)."""
    return workspace / "spec" / ".config" / "config.yaml"


def normalize_jira_base_url(url: str) -> str:
    """Strip whitespace and remove trailing slashes from a Jira base URL."""
    s = url.strip()
    while len(s) > 1 and s.endswith("/"):
        s = s[:-1]
    return s


def _coerce_bool(value: Any, default: bool = False) -> bool | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return None


def _coerce_str(value: Any) -> str | None:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return None


def _coerce_port(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        if 1 <= value <= 65535:
            return value
        return None
    if isinstance(value, str):
        try:
            n = int(value.strip(), 10)
        except ValueError:
            return None
        if 1 <= n <= 65535:
            return n
        return None
    return None


def _parse_jira_section(raw: Any) -> JiraSection | None:
    if not isinstance(raw, dict):
        return None
    jira_type = raw.get("type")
    if jira_type not in ("self_hosted", "atlassian_cloud"):
        return None
    address_raw = _coerce_str(raw.get("address"))
    if address_raw is None:
        return None
    address = normalize_jira_base_url(address_raw)
    if not address:
        return None
    ib = _coerce_bool(raw.get("ignore_tls"), False)
    if ib is None:
        return None
    ignore_tls = ib
    pat_s = _coerce_str(raw.get("pat_token"))
    email_s = _coerce_str(raw.get("email"))
    api_s = _coerce_str(raw.get("api_token"))
    pat_token = None if pat_s == "" else pat_s
    email = None if email_s == "" else email_s
    api_token = None if api_s == "" else api_s
    return JiraSection(
        type=jira_type,
        address=address,
        ignore_tls=ignore_tls,
        pat_token=pat_token,
        email=email,
        api_token=api_token,
    )


def _parse_proxy_section(raw: Any) -> ProxySection | None:
    if not isinstance(raw, dict):
        return None
    eb = _coerce_bool(raw.get("enabled"), False)
    if eb is None:
        return None
    enabled = eb
    host_raw = _coerce_str(raw.get("socks_host"))
    if host_raw is None:
        return None
    socks_host = host_raw.strip()
    port = _coerce_port(raw.get("socks_port"))
    if port is None:
        return None
    user_raw = _coerce_str(raw.get("socks_username"))
    pass_raw = _coerce_str(raw.get("socks_password"))
    if user_raw is None or pass_raw is None:
        return None
    socks_username = user_raw
    socks_password = pass_raw
    rdb = _coerce_bool(raw.get("remote_dns"), False)
    if rdb is None:
        return None
    remote_dns = rdb
    return ProxySection(
        enabled=enabled,
        socks_host=socks_host,
        socks_port=port,
        socks_username=socks_username,
        socks_password=socks_password,
        remote_dns=remote_dns,
    )


def _parse_document(doc: Any) -> SpectaskLocalConfig | None:
    if not isinstance(doc, dict):
        return None
    jira = _parse_jira_section(doc.get("jira"))
    proxy = _parse_proxy_section(doc.get("proxy"))
    if jira is None or proxy is None:
        return None
    return SpectaskLocalConfig(jira=jira, proxy=proxy)


def load_optional_config(path: Path | None = None) -> SpectaskLocalConfig | None:
    """Resolve workspace with spec; load parsed config or None if file missing/unreadable/invalid."""
    cfg_path: Path
    if path is not None:
        cfg_path = path
    else:
        ws = resolve_workspace_with_spec()
        if ws is None:
            return None
        cfg_path = config_yaml_path(ws)
    try:
        text = cfg_path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return _parse_document(doc)


def is_valid_http_url(url: str) -> bool:
    """Return True if url uses http or https and has a network location."""
    normalized = normalize_jira_base_url(url)
    parsed = urlparse(normalized)
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.netloc:
        return False
    return True


def config_to_ordered_dict(cfg: SpectaskLocalConfig) -> dict[str, Any]:
    """Serialize config to a plain dict suitable for YAML dumping."""
    j = cfg.jira
    p = cfg.proxy
    return {
        "jira": {
            "type": j.type,
            "address": j.address,
            "pat_token": "" if j.pat_token is None else j.pat_token,
            "ignore_tls": j.ignore_tls,
            "email": "" if j.email is None else j.email,
            "api_token": "" if j.api_token is None else j.api_token,
        },
        "proxy": {
            "enabled": p.enabled,
            "socks_host": p.socks_host,
            "socks_port": p.socks_port,
            "socks_username": p.socks_username,
            "socks_password": p.socks_password,
            "remote_dns": p.remote_dns,
        },
    }
