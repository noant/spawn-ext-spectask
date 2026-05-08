# Step 2: CLI --verbose through backends

## Goal
Wire `spectask-mcp run -v/--verbose` to the HTTP trace hook so stderr shows each Jira call while stdout output stays unchanged.

## Approach
- In `cli.py`, add `-v`/`--verbose` to the `run` parser and pass `verbose=ns.verbose` into `run_once`.
- In `run_cmd.py`, build a `trace` closure that prints method, URL, status, and body to stderr only when `verbose` is true; pass `trace` into `query_jira`.
- In `jira_actions.py`, add `trace: JiraHttpTraceFn | None = None` to `query_jira` (import the type from `http_common`); pass it to `backend_from_config` and ensure backends forward it to `fetch_issue_bundle` / `fetch_open_issues`.
- In `factory.py`, add optional `trace` to `backend_from_config` and pass into client constructors.
- In `cloud.py` and `self_hosted.py`, store `_trace`, forward in `get_issue_bundle` and `list_open_issues`.

## Affected files
- `spectask_mcp/cli.py`
- `spectask_mcp/run_cmd.py`
- `spectask_mcp/jira_actions.py`
- `spectask_mcp/jira/factory.py`
- `spectask_mcp/jira/cloud.py`
- `spectask_mcp/jira/self_hosted.py`

## Code changes (before / after)

### `spectask_mcp/cli.py` — run parser and `run_once` call

**Before**
```python
    p_run = sub.add_parser("run", help="Fetch Jira issue or list open issues once")
    p_run.add_argument("--issue", default=None, help="Jira issue key, e.g. PROJ-123")
```

**After**
```python
    p_run = sub.add_parser("run", help="Fetch Jira issue or list open issues once")
    p_run.add_argument("--issue", default=None, help="Jira issue key, e.g. PROJ-123")
    p_run.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Log each Jira HTTP response (method, URL, status, body) to stderr",
    )
```

**Before**
```python
        raise SystemExit(run_once(issue_key=ns.issue))
```

**After**
```python
        raise SystemExit(run_once(issue_key=ns.issue, verbose=ns.verbose))
```

Behavior: users opt in with `-v` or `--verbose`.

### `spectask_mcp/run_cmd.py` — `run_once` and trace closure

**Before**
```python
def run_once(*, issue_key: str | None) -> int:
```

**After**
```python
def run_once(*, issue_key: str | None, verbose: bool = False) -> int:
```

**Before**
```python
        out = query_jira(cfg, issue_key)
```

**After**
```python
        trace = None
        if verbose:
            def _trace(method: str, url: str, status: int, body: str) -> None:
                print(
                    f"{method} {url} -> {status}\n{body}\n",
                    file=sys.stderr,
                    flush=True,
                )
            trace = _trace
        out = query_jira(cfg, issue_key, trace=trace)
```

Behavior: only verbose mode attaches a stderr sink; normal mode passes `trace=None`.

### `spectask_mcp/jira_actions.py` — imports and `query_jira`

**Before**
```python
from spectask_mcp.jira.factory import backend_from_config
```

**After**
```python
from spectask_mcp.jira.factory import backend_from_config
from spectask_mcp.jira.http_common import JiraHttpTraceFn
```

**Before**
```python
def query_jira(cfg: SpectaskLocalConfig, issue_key: str | None) -> str:
```

**After**
```python
def query_jira(
    cfg: SpectaskLocalConfig,
    issue_key: str | None,
    trace: JiraHttpTraceFn | None = None,
) -> str:
```

**Before**
```python
    backend = backend_from_config(cfg)
```

**After**
```python
    backend = backend_from_config(cfg, trace=trace)
```

**Before** (inside `if key is not None:` branch)
```python
            bundle = backend.get_issue_bundle(key)
```

**After**
```python
            bundle = backend.get_issue_bundle(key)
```
(No signature change on backend methods — trace is already on the instance.)

**Before**
```python
            pairs = backend.list_open_issues(limit=_NOT_FOUND_POOL_LIMIT)
```

**After**
Same call — client uses stored trace.

Similarly for the final `list_open_issues` calls; no extra parameters at `query_jira` call sites beyond factory.

### `spectask_mcp/jira/factory.py` — pass trace to clients

**Before**
```python
def backend_from_config(cfg: SpectaskLocalConfig) -> JiraBackend:
    if cfg.jira.type == "self_hosted":
        return SelfHostedJiraClient(cfg)
    if cfg.jira.type == "atlassian_cloud":
        return AtlassianCloudJiraClient(cfg)
    raise ValueError(f"unknown jira.type: {cfg.jira.type!r}")
```

**After** (add import if not present; add `trace` parameter)

```python
from spectask_mcp.jira.http_common import JiraHttpTraceFn

def backend_from_config(
    cfg: SpectaskLocalConfig,
    trace: JiraHttpTraceFn | None = None,
) -> JiraBackend:
    if cfg.jira.type == "self_hosted":
        return SelfHostedJiraClient(cfg, trace=trace)
    if cfg.jira.type == "atlassian_cloud":
        return AtlassianCloudJiraClient(cfg, trace=trace)
    raise ValueError(f"unknown jira.type: {cfg.jira.type!r}")
```

Behavior: existing callers use default `trace=None`; only CLI verbose supplies a callback.

### `spectask_mcp/jira/cloud.py` — constructor and delegates

**Before**
```python
class AtlassianCloudJiraClient(JiraBackend):
    def __init__(self, cfg: SpectaskLocalConfig) -> None:
        if not cfg.jira.email or not cfg.jira.api_token:
            raise ValueError("atlassian_cloud Jira requires email and api_token")
        self._base = cfg.jira.address
        self._client = build_httpx_client(cfg)
        self._basic = (cfg.jira.email, cfg.jira.api_token)
```

**After**
```python
class AtlassianCloudJiraClient(JiraBackend):
    def __init__(
        self,
        cfg: SpectaskLocalConfig,
        trace: JiraHttpTraceFn | None = None,
    ) -> None:
        if not cfg.jira.email or not cfg.jira.api_token:
            raise ValueError("atlassian_cloud Jira requires email and api_token")
        self._base = cfg.jira.address
        self._client = build_httpx_client(cfg)
        self._basic = (cfg.jira.email, cfg.jira.api_token)
        self._trace = trace
```

Add import: `from spectask_mcp.jira.http_common import JiraHttpTraceFn`.

**Before**
```python
    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle(self._client, self._base, key, self._prepare)
```

**After**
```python
    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle(
            self._client, self._base, key, self._prepare, trace=self._trace
        )
```

**Before**
```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues(self._client, self._base, self._prepare, limit)
```

**After**
```python
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues(
            self._client, self._base, self._prepare, limit, trace=self._trace
        )
```

### `spectask_mcp/jira/self_hosted.py` — mirror cloud

Apply the same constructor `trace` parameter, `self._trace`, and `fetch_*(..., trace=self._trace)` pattern as in `cloud.py`.

## Additional actions
- Grep for `backend_from_config(` and `fetch_issue_bundle(` / `fetch_open_issues(` in tests or scripts; update call sites if any pass positional args that shift (prefer keyword `trace=` for new arg).
- Manual check: `spectask-mcp run --verbose` and `spectask-mcp run --issue KEY --verbose` show multiple stderr blocks matching the number of HTTP calls; stdout matches non-verbose run.
