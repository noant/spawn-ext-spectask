# 7: Migrate Jira access to pycontribs/jira

## Source seed
- Path: none

## Status
- [x] Spec created
- [ ] Self spec review passed
- [x] Spec review passed
- [x] Code implemented
- [x] Self code review passed
- [x] Code review passed
- [x] Design documents updated

## Goal
Replace the hand-written httpx REST layer in `spectask_mcp` with the `jira` package (pycontribs) while keeping the same config semantics (self-hosted PAT, Cloud email plus API token, SOCKS proxy, TLS verification toggle) and the same outward behavior for MCP and CLI.

## Design overview
- Affected modules: `spectask_mcp.jira` package (replace HTTP transport), `pyproject.toml` dependencies, possibly `spectask_mcp/jira/__init__.py` public exports.
- Files and symbols (planned touch list):
  - `pyproject.toml` — `[project.dependencies]` replace `httpx[socks]` with `jira` and SOCKS-capable stack (see Details).
  - `spectask_mcp/jira/http_common.py` — today: `build_httpx_client`, `_request`, `fetch_issue_bundle`, `fetch_open_issues`, `_raise_http`, trace typing; After: either removed or reduced to parsing helpers (`OPEN_ISSUES_JQL`, `_open_issue_pairs_from_search_body`, `_comment_body_text`, ADF helpers) plus thin wrappers if still needed.
  - New module e.g. `spectask_mcp/jira/pycontribs_factory.py` (exact name left to implementation) — factory building `jira.JIRA` from `SpectaskLocalConfig` (auth, `verify`, proxy mapping, timeouts).
  - `spectask_mcp/jira/self_hosted.py` — `SelfHostedJiraClient`: hold `jira.JIRA` (or subclass) instead of `httpx.Client`; wire `token_auth` / bearer per library docs.
  - `spectask_mcp/jira/cloud.py` — `AtlassianCloudJiraClient`: Basic auth via library options instead of manual `_prepare` on httpx.
  - `spectask_mcp/run_cmd.py` — only if verbose trace hook type or wiring changes.
- Data flow changes: all Jira HTTPS traffic goes through `requests` sessions owned by pycontribs `JIRA`; SOCKS proxy applied via `proxies` on that session per config proxy section.
- Integration points: `spectask_mcp.jira.factory.backend_from_config`, `spectask_mcp.jira_actions.query_jira` unchanged at the Python API level if `JiraBackend` protocol stays the same.

## Before → After

### Before
- Direct `httpx.Client` calls construct URLs under `/rest/api/3/`, including POST `/search/jql` then POST `/search` fallback, GET issue and paginated GET comments.

### After
- One `jira.JIRA` (or documented subclass) per backend instance drives issue fetch, comment retrieval, and JQL search using library APIs; where the library does not expose an endpoint parity, use the documented `session` or resource layer to issue the same REST paths as today (explicitly justified in subtasks).

## Details
- Implementation clarifications (Step 1.1):
  - **In scope:** dependency on **pycontribs `jira`**; map `spectask_mcp` config to library auth (PAT / email plus API token); map optional SOCKS proxy to `requests` proxies (SOCKS requires compatible stack, e.g. `requests[socks]` / PySocks); preserve `follow_redirects` behavior equivalent to current httpx default (`True`).
  - **Out of scope:** switching to a different third-party client later; OAuth-only flows not already implied by config.
  - Lock a **minimum `jira` version** in `pyproject.toml` once the implementer confirms which release supports required calls (enhanced search if needed).
  - **Verbose HTTP trace (`-v`):** pycontribs may not expose per-request hooks like today; subtasks must either attach to the library `requests` session where supported or document a deliberate reduction of trace detail (no silent removal of the flag).
  - **Exit codes and errors:** map library exceptions to existing `JiraConnectionError` / `ValueError` patterns used by `run_cmd.run_once` and MCP.

## Execution Scheme
> Each step id is the subtask filename. MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions — even if a step seems trivial or small.
- Phase 1 (sequential): step `1-dependencies-and-jira-factory` → step `2-migrate-issue-bundle` → step `3-migrate-open-issues-search` → step `4-cleanup-exports-and-trace`
