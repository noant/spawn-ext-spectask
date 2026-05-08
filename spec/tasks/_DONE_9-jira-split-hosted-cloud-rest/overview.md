# 9: Split self-hosted vs Cloud Jira REST (v2 vs v3) and scope listing JQL

## Source seed
- Path: none

## Status
- [V] Spec created
- [V] Self spec review passed
- [V] Spec review passed
- [V] Code implemented
- [V] Self code review passed
- [V] Code review passed
- [V] Design documents updated

## Goal
Separate transport and REST versioning so Atlassian Cloud uses API v3 search paths and self-hosted uses API v2 only, with listing JQL scoped to the authenticated user, unresolved issues, newest created first.

## Design overview
- Affected modules: `spectask_mcp/jira` (factory, HTTP helpers, cloud/self-hosted backends), `spectask_mcp/jira_actions.py` (documentation only), `spec/design/hla.md` (Step 7).
- Files and symbols:
  - `spectask_mcp/jira/pycontribs_factory.py` — `connect_jira_client`: pass `rest_api_version` in `options` by `cfg.jira.type` (`atlassian_cloud` -> `"3"`, `self_hosted` -> `"2"`).
  - New `spectask_mcp/jira/jql.py` — module-level `CURRENT_USER_OPEN_ISSUES_JQL` (single source for listing JQL).
  - New `spectask_mcp/jira/http_cloud.py` — `fetch_open_issues_cloud(jira, limit, trace=None)` using `POST .../rest/api/3/search/jql` then fallback `POST .../rest/api/3/search` with shared body shape and JQL constant.
  - New `spectask_mcp/jira/http_self_hosted.py` — `fetch_open_issues_self_hosted(jira, limit, trace=None)` using only `POST .../rest/api/2/search` (no `/search/jql`).
  - `spectask_mcp/jira/http_common.py` — remove `OPEN_ISSUES_JQL` and `fetch_open_issues_via_jira`; retain `fetch_issue_bundle_via_jira`, `_open_issue_pairs_from_search_body`, `_raise_requests_http`, `_map_jira_error`, `JiraHttpTraceFn` (issue fetch stays shared; REST path version comes from client options).
  - `spectask_mcp/jira/cloud.py` — `AtlassianCloudJiraClient.list_open_issues` calls `fetch_open_issues_cloud`; keep `get_issue_bundle` -> `fetch_issue_bundle_via_jira`.
  - `spectask_mcp/jira/self_hosted.py` — `SelfHostedJiraClient.list_open_issues` calls `fetch_open_issues_self_hosted`; keep `get_issue_bundle` -> `fetch_issue_bundle_via_jira`.
- Data flow changes: `backend_from_config` still returns the same two classes; each class delegates listing to deployment-specific HTTP helpers. Pycontribs `JIRA` instances differ by `options["rest_api_version"]`, so `jira.issue()` aligns with v3 on Cloud and v2 on self-hosted without duplicating issue-fetch code.
- Integration points: MCP and CLI continue to use `query_jira` -> `backend.list_open_issues(5)` unchanged.

## Before -> After

### Before
- One shared `fetch_open_issues_via_jira` posts to `/rest/api/3/...` for all deployments.
- Listing JQL is global unresolved issues, not scoped to current user.
- `connect_jira_client` does not set `rest_api_version`; library default is `"2"` even for Cloud.

### After
- Cloud listing uses v3 search endpoints only; self-hosted listing uses v2 `/search` only.
- Listing JQL: `assignee = currentUser() AND resolution = Unresolved ORDER BY created DESC`.
- Cloud clients use `rest_api_version` `"3"`; self-hosted use `"2"` for all pycontribs REST URLs including issue fetch.

## Details
- **Implementation clarifications (agreed defaults):**
  - "Not closed" is expressed as `resolution = Unresolved` (same family as the previous `OPEN_ISSUES_JQL` filter).
  - "Latest created" is `ORDER BY created DESC` with existing caller `limit` (e.g. 5 in `query_jira`).
  - Issue fetch remains `fetch_issue_bundle_via_jira` in `http_common.py`; behavior differs by deployment only through `rest_api_version` on the `JIRA` object (no duplicated issue parsers).
  - Trace callbacks stay unused in listing helpers (`del trace` pattern preserved).
- **Backward compatibility:** Listing output shape unchanged: `(key, summary)` tuples. MCP plaintext semantics unchanged except issue set is now "my open issues" not all open issues.
- After implementation, Step 7 updates `spec/design/hla.md` to describe v2 vs v3 split and new modules.

## Execution Scheme
> Each step id is the subtask filename (e.g. `1-abstractions`).
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions -- even if a step seems trivial or small.
- Phase 1 (sequential): step `_DONE_1-rest-session-api-version` -> step `_DONE_2-split-search-http-and-jql`
