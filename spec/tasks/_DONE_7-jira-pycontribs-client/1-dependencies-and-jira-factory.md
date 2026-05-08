# Step 1: Dependencies and JIRA factory from config

## Goal
Add the `jira` (pycontribs) dependency, remove the direct httpx dependency from the Jira layer, and introduce a factory that returns a configured `jira.JIRA` instance from `SpectaskLocalConfig` including SOCKS proxy and TLS verification.

## Approach
1. Edit `pyproject.toml`: add `jira` with a lower-bound version TBD from compatibility checks; drop `httpx[socks]` if nothing else in the project imports httpx (grep confirms only `spectask_mcp/jira/http_common.py` today). Add SOCKS support for `requests` if not pulled transitively (e.g. `requests[socks]` or `PySocks` as documented in the chosen stack).
2. Add a new module (name per repo conventions) that exposes a function such as `def connect_jira_client(cfg: SpectaskLocalConfig) -> JIRA` where `JIRA` is imported from `jira`.
3. Map `cfg.jira.ignore_tls` to `options.verify` (or library-equivalent keyword).
4. Map `cfg.proxy.enabled` to `options["proxies"]` or session `proxies` using the same SOCKS URL shape as today (`_socks_proxy_url` logic can move here from `http_common.py`).
5. Self-hosted: pass PAT via `token_auth=cfg.jira.pat_token` or library-documented PAT header pattern if `token_auth` differs by version.
6. Cloud: pass `basic_auth=(email, api_token)` per library constructor.
7. Set reasonable timeout (align with former `httpx.Timeout(60.0)`).

## Affected files
- `pyproject.toml`
- `spectask_mcp/jira/http_common.py` (extract or duplicate SOCKS URL helper into the new module; stop exporting `build_httpx_client` once step 4 removes consumers)
- New: `spectask_mcp/jira/{pycontribs_factory}.py` (exact filename chosen in implementation; referenced here as factory module)

## Code changes (before / after)

### `pyproject.toml` — `[project.dependencies]`

**Before**

```toml
dependencies = [
  "mcp>=1.2.0",
  "httpx[socks]>=0.27.0",
  "PyYAML>=6.0.1",
]
```

Behavior: Jira layer uses httpx.

**After**

```toml
dependencies = [
  "mcp>=1.2.0",
  "jira>=X.Y",
  "PyYAML>=6.0.1",
]
```

Behavior: Jira uses pycontribs; `X.Y` is the minimum verified version (fill during implementation). Include SOCKS-related dependency line if required in addition to `jira`.

### `spectask_mcp/jira/http_common.py` — `build_httpx_client` (context for removal in later steps)

**Before**

```python
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
```

Behavior: factory for httpx-only backends; SOCKS via httpx `proxy=` string.

**After**

```python
# build_httpx_client removed from this module once SelfHostedJiraClient and
# AtlassianCloudJiraClient use jira.JIRA; SOCKS and verify live in the new
# factory that builds options for jira.JIRA(...)
```

Behavior: same transport semantics moved to pycontribs factory (not verbatim empty comment in code; implement real factory in the new file).

### New factory module — `connect_jira_client(cfg) -> JIRA`

**Before**

```python
# (file absent)
```

Behavior: none.

**After**

```python
from jira import JIRA

def connect_jira_client(cfg: SpectaskLocalConfig) -> JIRA:
    ...
```

Behavior: returns authenticated `JIRA` with proxy and verify matching former httpx client policy.

## Additional actions
- Run `uv lock` or project lockfile update after dependency edit.
- Grep `spectask_mcp` for `httpx` and `build_httpx_client` before closing this step; only factory and non-migrated code may still reference old symbols until later subtasks land.
