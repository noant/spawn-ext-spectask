# High-Level Architecture (HLA)

This document describes the high-level architecture and interaction of abstractions in the project.

## spectask-mcp (Jira)

The `spectask_mcp` package talks to Jira via REST API v3. Open-issue listing uses `POST /rest/api/3/search/jql` first; if the server responds with 404 or 410, the client retries once with `POST /rest/api/3/search` (legacy) so Atlassian Cloud and older self-hosted instances both work.

All Jira HTTPS traffic uses pycontribs `jira.JIRA` instances from `connect_jira_client` in `spectask_mcp/jira/pycontribs_factory.py`, backed by a `requests.Session` on `JIRA._session`. TLS verification and optional SOCKS5 proxies are applied to that session from local config. `requests` follows redirects by default (`allow_redirects=True`), matching the former httpx client policy.

`query_jira` in `spectask_mcp/jira_actions.py` loads unresolved issues once with `list_open_issues(limit=5)` and JQL `resolution = Unresolved ORDER BY created DESC` (`OPEN_ISSUES_JQL` in `spectask_mcp/jira/http_common.py`). With no issue key, or when a supplied key does not resolve, output is those five issues as `key<TAB>summary` lines (same shape, no not-found message). When a key resolves, output is key, summary, and a JSON `fields` block. Single-issue loading uses `fetch_issue_bundle_via_jira`, which does not request Jira comments; bundles always have an empty `comments` list.

CLI `spectask-mcp run --verbose` passes an optional HTTP trace callback into `query_jira`, then `backend_from_config` and `connect_jira_client`, which registers a `requests` response hook on the Jira session. Each response is traced with method, URL, status code, and response body on stderr (no request headers logged); MCP `serve` uses the same stack with no trace by default.
