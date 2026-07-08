# High-Level Architecture (HLA)

This document describes the high-level architecture and interaction of abstractions in the project.

## spectask-mcp (Jira)

Deployment type selects behavior end-to-end. `backend_from_config` in `spectask_mcp/jira/factory.py` returns either `AtlassianCloudJiraClient` (`spectask_mcp/jira/cloud.py`) or `SelfHostedJiraClient` (`spectask_mcp/jira/self_hosted.py`).

`connect_jira_client` in `spectask_mcp/jira/pycontribs_factory.py` builds pycontribs `jira.JIRA` with `options["rest_api_version"]` set to `"3"` for Atlassian Cloud and `"2"` for self-hosted. All library-built REST URLs (including `jira.issue` used by `fetch_issue_bundle_via_jira` in `spectask_mcp/jira/http_common.py`) follow that version.

Open-issue listing is not shared between deployments: Cloud uses `fetch_open_issues_cloud` in `spectask_mcp/jira/http_cloud.py`, posting to `POST /rest/api/3/search/jql` first and falling back to `POST /rest/api/3/search` on 404 or 410. Self-hosted uses only `fetch_open_issues_self_hosted` in `spectask_mcp/jira/http_self_hosted.py`, posting to `POST /rest/api/2/search`. Both helpers read JQL from `CURRENT_USER_OPEN_ISSUES_JQL` in `spectask_mcp/jira/jql.py` (`assignee = currentUser() AND resolution = Unresolved ORDER BY created DESC`). Shared parsing and HTTP error helpers live in `http_common.py`.

All Jira HTTPS traffic uses that session on `JIRA._session`. TLS verification and optional SOCKS5 proxies are applied from local config (`spectask_mcp/config.py`). When `proxy.enabled` is true, `_socks_proxy_url` in `spectask_mcp/jira/pycontribs_factory.py` builds `socks5://` or `socks5h://` depending on `proxy.remote_dns` (remote resolution on the proxy vs local OS). `requests` follows redirects by default (`allow_redirects=True`), matching the former httpx client policy.

Both CLI and MCP share issue loading via `fetch_issue_bundle_via_jira` in `http_common.py`, which GETs the issue with `renderedFields`, derives plain description and labels into `IssueBundle` (`spectask_mcp/jira/types.py`: `description`, `labels`, `fields`, `comments`), and paginates `GET issue/{key}/comment` via `_paginated_issue_comments_via_session` (`COMMENT_MAX_FETCH = 70`; when the thread is longer, the newest 70 comments are fetched and returned oldest-to-newest within that window). Comment rows are `IssueComment` instances; author names come from Jira comment JSON (`displayName`, then `name`, then `key`).

`query_jira` and `query_jira_for_mcp` in `spectask_mcp/jira_actions.py` each load listing once with `list_open_issues(limit=5)`. With no issue key, or when a supplied key does not resolve, both return those five issues as `key<TAB>summary` lines (same shape, no not-found message). When a key resolves, CLI `query_jira` formats via `_format_issue` (key, summary, JSON `fields` block, up to 70 numbered comment lines). MCP `query_jira_for_mcp` (used by `jira_fetch` in `mcp_app.py`) formats via `_format_issue_mcp` (key, summary, plain `Description:`, comma-separated `Labels:`, up to 70 unnumbered `author: body` comment lines).

CLI `spectask-mcp run --verbose` passes an optional HTTP trace callback into `query_jira`, then `backend_from_config` and `connect_jira_client`, which registers a `requests` response hook on the Jira session. Each response is traced with method, URL, status code, and response body on stderr (no request headers logged); MCP `serve` calls `query_jira_for_mcp` with no trace by default.

Spawn ships stdio MCP descriptors under `extsrc/mcp/` (`windows.json`, `linux.json`, `macos.json`) for server `spectask-mcp-jira`. Each platform runs `uvx spectask-mcp serve` so MCP resolves the latest PyPI release on start (requires `uv` on PATH). The after-install hook still runs `uv tool install` / `uv tool upgrade` for CLI commands (`spectask-mcp run`, `spectask-mcp interactive`); MCP and CLI may run different package versions until the user upgrades the tool.
