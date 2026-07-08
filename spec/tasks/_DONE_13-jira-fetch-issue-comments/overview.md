# 13: Jira issue fetch includes comments with author

## Source seed
- Path: none

## Status
- [V] Spec created [composer-2.5-fast]
- [V] Self spec review passed [composer-2.5-fast]
- [V] Spec review passed
- [V] Code implemented [composer-2.5-fast]
- [V] Self code review passed [composer-2.5-fast]
- [V] Code review passed
- [V] Design documents updated [composer-2.5-fast]

## Goal
When `jira_fetch` or `spectask-mcp run --issue KEY` resolves an issue, load up to 70 comments (newest when truncated) and include each comment author in the plaintext output.

## Design overview
- Affected modules: `spectask_mcp.jira.types`, `spectask_mcp.jira.http_common`, `spectask_mcp.jira_actions`, `spectask_mcp.mcp_app`, `spectask_mcp.run_cmd`; Step 7 updates `spec/design/hla.md` and `extsrc/files/spec/design/hla.md`.
- Files and symbols:
  - `spectask_mcp/jira/types.py` — new `IssueComment` dataclass; `IssueBundle.comments` becomes `list[IssueComment]`.
  - `spectask_mcp/jira/http_common.py` — add `import html`, `import re`; import `IssueComment`; restore `COMMENT_PAGE_SIZE`, `COMMENT_MAX_FETCH` (70), `_strip_html`, `_adf_to_plain`, `_comment_body_text`, `_comment_author_name`, `_paginated_issue_comments_via_session`; wire into `fetch_issue_bundle_via_jira`.
  - `spectask_mcp/jira_actions.py` — module docstring; `query_jira` -> `_format_issue` adds numbered `author: body` lines under `Comments:` (MCP and CLI share this path).
  - `spectask_mcp/mcp_app.py` — `jira_fetch` tool `description=` for `_jira_fetch_impl`.
  - `spectask_mcp/run_cmd.py` — module docstring exit-code line for stdout shape.
- Data flow: `query_jira` -> `backend.get_issue_bundle` -> `fetch_issue_bundle_via_jira` GET issue plus paginated `GET issue/{key}/comment?expand=renderedBody&orderBy=created`; cap at 70 bodies with author names; `_format_issue` serializes for MCP and CLI.
- Integration points: unchanged `JiraBackend` protocol signature; both `SelfHostedJiraClient` and `AtlassianCloudJiraClient` delegate to shared `fetch_issue_bundle_via_jira` (REST version from `connect_jira_client` options).

## Before -> After

### Before
- Issue detail returns key, summary, and fields JSON only; `IssueBundle.comments` is always `[]`; no `/comment` REST traffic.

### After
- Issue detail adds a `Comments:` section: numbered lines `{n}. {author}: {body}`; up to 70 comments oldest-to-newest within the fetched window; when the issue has more than 70 comments, the window is the 70 most recently created.

## Details

**Step 1.1 clarifications (agreed):**

1. **Comment cap:** `COMMENT_MAX_FETCH = 70`. When `total > 70`, fetch the tail (newest 70) using `startAt = total - take` (same strategy as pre-task-8 code with 150).
2. **Author:** required in output; resolve from comment JSON `author.displayName`, then `author.name`, then `author.key`, else `"unknown"`.
3. **Scope:** all issue-detail paths — MCP `jira_fetch` with a resolving key and CLI `spectask-mcp run --issue KEY`; listing-only behavior (five open issues) unchanged.
4. **Comment body:** plain text via existing helpers — prefer `renderedBody` (HTML stripped), else string `body`, else ADF via `_adf_to_plain`.
5. **Listing / not-found:** no change to five-issue list or missing-key fallback.

## Execution Scheme
> Each step id is the subtask filename.
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions — even if a step seems trivial or small.
- Phase 1 (sequential): step `1-types-and-http-comments` -> step `2-format-and-tool-docs`
