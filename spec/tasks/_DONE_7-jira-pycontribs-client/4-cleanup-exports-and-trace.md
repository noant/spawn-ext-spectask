# Step 4: Cleanup exports, close lifecycle, and verbose trace

## Goal
Remove dead httpx-based symbols, align `spectask_mcp/jira/__init__.py` exports, implement `close()` on backends using library lifecycle, and preserve or document `spectask-mcp run -v` HTTP tracing after the migration.

## Approach
1. Delete unused functions: `_request`, `_raise_http`, and any leftover httpx-only `fetch_*` once replaced; retain pure helpers (`OPEN_ISSUES_JQL`, ADF/HTML comment parsing, `_open_issue_pairs_from_search_body`) in a module that does not import httpx.
2. Update `spectask_mcp/jira/__init__.py`: stop exporting `build_httpx_client` if removed; export what MCP integrators still need (`OPEN_ISSUES_JQL` unchanged if still public).
3. `SelfHostedJiraClient.close` and `AtlassianCloudJiraClient.close`: close the underlying `requests` session on the `JIRA` object per library guidance (e.g. `jira.close()` if available).
4. Verbose trace: if `JiraHttpTraceFn` remains, wire it using `requests` event hooks on the session behind `JIRA` (`response` hook logging URL, status, bounded body) or reduce trace to documented fields; ensure stderr output remains usable and does not leak tokens in header logs.
5. `spectask_mcp/run_cmd.py`: adjust trace lambda signature only if `JiraHttpTraceFn` type alias changed in step 4.
6. Grep the repository for `httpx`, `build_httpx_client`, and old `fetch_issue_bundle` names; zero stale references.

## Affected files
- `spectask_mcp/jira/http_common.py`
- `spectask_mcp/jira/__init__.py`
- `spectask_mcp/jira/self_hosted.py` — `close`
- `spectask_mcp/jira/cloud.py` — `close`
- `spectask_mcp/jira/factory.py` — imports if any
- `spectask_mcp/run_cmd.py` — optional trace closure
- `spectask_mcp/jira_actions.py` — only if trace type imports change

## Code changes (before / after)

### `spectask_mcp/jira/__init__.py` — exports

**Before**

```python
from spectask_mcp.jira.http_common import OPEN_ISSUES_JQL, build_httpx_client
```

**After**

```python
from spectask_mcp.jira.http_common import OPEN_ISSUES_JQL
# build_httpx_client removed; export only remaining public helpers
```

Behavior: public API no longer implies httpx transport.

### `spectask_mcp/jira/self_hosted.py` — `close`

**Before**

```python
    def close(self) -> None:
        self._client.close()
```

**After**

```python
    def close(self) -> None:
        self._jira.close()
```

Behavior: release pycontribs session resources (exact method per library version).

## Additional actions
- Confirm `uv.lock` / lockfile consistent with final dependencies.
- Optional: add a one-line note to `spec/design/hla.md` in Step 7 that Jira integration uses pycontribs `jira` (do not edit HLA during Steps 1–2).
