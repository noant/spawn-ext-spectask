# 5: MCP CLI run --verbose Jira trace

## Source seed
- Path: none

## Status
- [x] Spec created
- [x] Self spec review passed
- [x] Spec review passed
- [x] Code implemented
- [x] Self code review passed
- [x] Code review passed
- [x] Design documents updated

## Goal
Add `spectask-mcp run --verbose` so each Jira REST call logs method, URL, HTTP status, and full response body to stderr without changing normal stdout.

## Design overview
- Affected modules: CLI (`spectask_mcp`), Jira HTTP helpers (`spectask_mcp.jira.http_common`), backends (`spectask_mcp.jira.cloud`, `spectask_mcp.jira.self_hosted`), factory, shared query (`jira_actions`).
- Files and symbols:
  - `spectask_mcp/cli.py` — `main`, `run` subparser
  - `spectask_mcp/run_cmd.py` — `run_once`
  - `spectask_mcp/jira_actions.py` — `query_jira`
  - `spectask_mcp/jira/factory.py` — `backend_from_config`
  - `spectask_mcp/jira/cloud.py` — `AtlassianCloudJiraClient.__init__`, `get_issue_bundle`, `list_open_issues`
  - `spectask_mcp/jira/self_hosted.py` — `SelfHostedJiraClient` (same methods)
  - `spectask_mcp/jira/http_common.py` — `_request`, `fetch_issue_bundle`, `fetch_open_issues`
- Data flow: `--verbose` -> `run_once(verbose=True)` -> `query_jira(..., trace=fn)` -> `backend_from_config(..., trace=fn)` -> clients pass `trace` into `fetch_*` -> `_request` calls `trace` after each response with method, URL, status, body text.
- Integration points: MCP `serve` path unchanged; only `run` subcommand gains the flag.

## Before -> After
### Before
- `run` has no verbosity flag; Jira traffic is invisible on the CLI.

### After
- `run` accepts `-v` / `--verbose`; stderr shows one block per HTTP response (method, URL, status, full body). Stdout remains the same formatted issue or listing as today.

## Details
- Log destination: stderr only (preserve stdout for scripts and pipes).
- Body formatting: use response text as returned by httpx (pretty JSON where the API returns JSON); no truncation in verbose mode.
- Security: do not log request headers or auth material; response bodies may still contain sensitive fields — verbose is for local debugging only.
- 404 on GET issue: log the response body like any other response before returning `None`.
- Type for trace callback: a small alias e.g. `JiraHttpTraceFn = Callable[[str, str, int, str], None]` for `(method, url, status_code, body_text)` in `http_common.py` (or a dedicated `spectask_mcp/jira/trace_types.py` if imports get circular — prefer keeping the alias in `http_common` unless a cycle appears).

## Execution Scheme
> Each step id is the subtask filename (e.g. `1-abstractions`).
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions — even if a step seems trivial or small.
- Phase 1 (sequential): step 1-http-common-trace -> step 2-cli-through-backend
