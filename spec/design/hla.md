# High-Level Architecture (HLA)

This document describes the high-level architecture and interaction of abstractions in the project.

## spectask-mcp (Jira)

The `spectask_mcp` package talks to Jira via REST API v3. Open-issue listing uses `POST /rest/api/3/search/jql` first; if the server responds with 404 or 410, the client retries once with `POST /rest/api/3/search` (legacy) so Atlassian Cloud and older self-hosted instances both work.

`query_jira` in `spectask_mcp/jira_actions.py`: when the caller supplies an issue key that does not resolve via GET issue, it loads a larger open-issue pool (`list_open_issues` with a higher limit), ranks possible matches (substring and `difflib` against key/summary), prints up to 30 candidates, then prints the standard first-page unresolved listing as before.

CLI `spectask-mcp run --verbose` passes an optional HTTP trace callback into `query_jira`, then `backend_from_config`, Jira clients, and `spectask_mcp/jira/http_common.py` fetch helpers. After each HTTP response, `_request` invokes the trace with method, URL, status code, and full response body to stderr; MCP `serve` uses the same stack with no trace by default.
