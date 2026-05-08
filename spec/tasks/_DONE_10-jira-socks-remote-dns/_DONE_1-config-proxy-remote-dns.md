# Step 1: Config model and SOCKS URL scheme

## Goal
Add `remote_dns` to the proxy section in code and YAML, and build `socks5h` proxy URLs when it is true.

## Approach
Extend `ProxySection` and parsing/serialization in `config.py`. Switch `_socks_proxy_url` on `proxy.remote_dns`. No changes to JIRA constructor arguments beyond the existing `proxies` dict.

## Affected files
- `spectask_mcp/config.py` -- `ProxySection`, `_parse_proxy_section`, `config_to_ordered_dict`
- `spectask_mcp/jira/pycontribs_factory.py` -- `_socks_proxy_url`

## Code changes (before / after)

### `spectask_mcp/config.py` -- `ProxySection` and `_parse_proxy_section`

**Before**
```python
@dataclass
class ProxySection:
    enabled: bool
    socks_host: str
    socks_port: int
    socks_username: str
    socks_password: str
```

**After**
```python
@dataclass
class ProxySection:
    enabled: bool
    socks_host: str
    socks_port: int
    socks_username: str
    socks_password: str
    # If True, use socks5h so the proxy resolves hostnames (not the local OS).
    remote_dns: bool = False
```

Adds optional remote DNS flag on the proxy section; default false keeps existing installs valid without YAML edits.

**Before**
```python
    socks_username = user_raw
    socks_password = pass_raw
    return ProxySection(
        enabled=enabled,
        socks_host=socks_host,
        socks_port=port,
        socks_username=socks_username,
        socks_password=socks_password,
    )
```

**After**
```python
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
```

Parses `remote_dns` from YAML; omitted key yields false via `_coerce_bool(None, False)`.

### `spectask_mcp/config.py` -- `config_to_ordered_dict` proxy block

**Before**
```python
        "proxy": {
            "enabled": p.enabled,
            "socks_host": p.socks_host,
            "socks_port": p.socks_port,
            "socks_username": p.socks_username,
            "socks_password": p.socks_password,
        },
```

**After**
```python
        "proxy": {
            "enabled": p.enabled,
            "socks_host": p.socks_host,
            "socks_port": p.socks_port,
            "socks_username": p.socks_username,
            "socks_password": p.socks_password,
            "remote_dns": p.remote_dns,
        },
```

Wizard and round-trips persist the flag in YAML.

### `spectask_mcp/jira/pycontribs_factory.py` -- `_socks_proxy_url`

**Before**
```python
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
```

**After**
```python
def _socks_proxy_url(proxy: ProxySection) -> str:
    scheme = "socks5h" if proxy.remote_dns else "socks5"
    host = proxy.socks_host.strip()
    port = int(proxy.socks_port)
    user = proxy.socks_username
    password = proxy.socks_password
    if user or password:
        u = quote(user, safe="")
        p = quote(password, safe="")
        return f"{scheme}://{u}:{p}@{host}:{port}"
    return f"{scheme}://{host}:{port}"
```

When `remote_dns` is true, requests/urllib3 uses hostname resolution through the SOCKS proxy.

## Additional actions
- Manual: with proxy enabled and `remote_dns: true`, confirm Jira calls work when local `nslookup` for the Jira host fails but the proxy resolves the name.
