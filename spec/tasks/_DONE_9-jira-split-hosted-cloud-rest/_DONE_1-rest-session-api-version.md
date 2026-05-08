# Step 1: REST API version on JIRA session by deployment

## Goal
Ensure pycontribs `JIRA` uses REST API version 3 for Atlassian Cloud and version 2 for self-hosted so all resource URLs (including `jira.issue`) match the deployment.

## Approach
Extend `connect_jira_client` to set `options["rest_api_version"]` from `cfg.jira.type` before constructing `JIRA`. Do not change auth or proxy behavior.

## Affected files
- `spectask_mcp/jira/pycontribs_factory.py` — function `connect_jira_client`

## Code changes (before / after)

### `spectask_mcp/jira/pycontribs_factory.py` — `connect_jira_client`

**Before**
```python
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
```

Builds one options dict with TLS verify only; REST version is implicit (library default).

**After**
```python
    verify = not cfg.jira.ignore_tls
    proxies: dict[str, str] | None = None
    if cfg.proxy.enabled:
        url = _socks_proxy_url(cfg.proxy)
        proxies = {"http": url, "https": url}

    rest_api_version = (
        "3" if cfg.jira.type == "atlassian_cloud" else "2"
    )

    base_kw: dict[str, Any] = {
        "server": cfg.jira.address.rstrip("/"),
        "options": {"verify": verify, "rest_api_version": rest_api_version},
        "timeout": 60.0,
        "max_retries": 3,
        "proxies": proxies,
    }
```

Cloud gets explicit v3; self-hosted explicit v2 for every pycontribs REST call.

## Additional actions
- Quick sanity: instantiate `JIRA` from config in a REPL or trivial script is optional; no new tests required unless the repo gains a test harness later.
