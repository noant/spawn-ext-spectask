# 8: Simplify Jira run and MCP query to five recent open issues

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
Reduce CLI `run` and MCP `jira_fetch` to a minimal Jira surface: default output is exactly five newest-created unresolved issues as `key<TAB>summary`; issue detail never loads comments; if a passed issue key is missing, output matches the default list with no extra messaging.

## Design overview
- Affected modules: `spectask_mcp.jira_actions` (orchestration and formatting), `spectask_mcp.jira.http_common` (JQL, issue fetch without comment traffic), MCP tool copy in `spectask_mcp.mcp_app`, CLI docstring in `spectask_mcp.run_cmd`; `JiraBackend` protocol and client methods keep the same signatures.
- Files and symbols:
  - `spectask_mcp/jira/http_common.py` — `OPEN_ISSUES_JQL`; `fetch_issue_bundle_via_jira`; remove comment-only helpers (`_paginated_issue_comments_via_session`, `_comment_body_text`, `_adf_to_plain`, `_strip_html`, `COMMENT_PAGE_SIZE`, `COMMENT_MAX_FETCH`) once unused.
  - `spectask_mcp/jira_actions.py` — module docstring; remove `_rank_pairs_for_query`, `_LIST_LIMIT`, `_NOT_FOUND_POOL_LIMIT`, `_CANDIDATE_*`; `_format_issue` (no Comments block); `query_jira`.
  - `spectask_mcp/mcp_app.py` — `jira_fetch` tool `description=` for `_jira_fetch_impl`.
  - `spectask_mcp/run_cmd.py` — module docstring line describing stdout.
  - Step 7 (after code review): `spec/design/hla.md` and `extsrc/files/spec/design/hla.md` — replace the paragraph about `query_jira` not-found behavior and mention no comment fetch.
- Data flow changes: one search path for the five-issue list (`list_open_issues` with `limit=5` and new JQL); optional single GET issue for key detail with `comments=[]` and zero comment endpoints.
- Integration points: `backend_from_config`, `SelfHostedJiraClient` / `AtlassianCloudJiraClient`; `OPEN_ISSUES_JQL` remains exported from `spectask_mcp/jira/__init__.py` with new semantics.

## Before → After

### Before
- Bare `run` lists up to 50 unresolved issues ordered by updated; MCP doc promises comments and not-found fuzzy matching.

### After
- Bare `run` lists exactly five unresolved issues ordered by created descending; `--issue KEY` prints fields JSON and summary without comments when found; when not found prints the same five-issue list as bare `run`.

## Details

**Step 1.1 Implementation clarifications (agreed defaults):**

1. **What counts as "open":** unresolved only: JQL predicate `resolution = Unresolved`.
2. **"Most recently created five":** append `ORDER BY created DESC`; `maxResults` / `limit` for that search is **5**.
3. **Output format:** each line `key\t` + summary (`_format_list` TAB join kept); empty search returns `(no open issues returned)`.
4. **Missing issue key:** do not prepend `Issue XYZ not found` or candidate blocks; behave exactly like absent `--issue` (same `_format_list` over the five pairs).
5. **Found issue (`--issue` or MCP key):** keep `Summary:` and indented JSON `fields` block in `_format_issue`; remove the entire Comments section from the formatter and skip all `/comment` REST calls in `fetch_issue_bundle_via_jira`.
6. **Backends:** retain `list_open_issues(self, limit: int = 50)` signature for minimal diff; callers pass `limit=5` exclusively for this behavior (implementer may change default to `5` if all call sites agree).
7. **Public constant:** keep name `OPEN_ISSUES_JQL` but replace its string value to the new JQL (callers/embedders see changed semantics documented here).

## Execution Scheme
> Each step id is the subtask filename.
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions -- even if a step seems trivial or small.
- Phase 1 (sequential): step `1-http-issue-and-list-jql` -> step `2-jira-actions-mcp-docs`
