# 14: MCP jira_fetch plain-text issue output

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
When MCP `jira_fetch` resolves an issue, return lean plain text (key, summary, description, labels, comments as `author: text`) instead of a full `Fields:` JSON dump; CLI `spectask-mcp run --issue` keeps the existing fields JSON format.

## Design overview
- Affected modules: `spectask_mcp.jira.types`, `spectask_mcp.jira.http_common`, `spectask_mcp.jira_actions`, `spectask_mcp.mcp_app`; Step 7 updates `spec/design/hla.md` and `extsrc/files/spec/design/hla.md`.
- Files and symbols:
  - `spectask_mcp/jira/types.py` — add `description: str`, `labels: list[str]` on `IssueBundle`.
  - `spectask_mcp/jira/http_common.py` — `_description_plain(fields, rendered_fields)`, `_labels_from_fields(fields)`; populate new bundle fields in `fetch_issue_bundle_via_jira`.
  - `spectask_mcp/jira_actions.py` — keep `_format_issue` / `query_jira` for CLI; add `_format_issue_mcp`, `query_jira_for_mcp`.
  - `spectask_mcp/mcp_app.py` — `_jira_fetch_impl` calls `query_jira_for_mcp`; update tool `description=`.
- Data flow: shared fetch (`fetch_issue_bundle_via_jira`); MCP path formats plain sections only; CLI path unchanged (key, summary, `Fields:` JSON, numbered comments).
- Integration points: `JiraBackend.get_issue_bundle` unchanged; listing (`list_open_issues(5)`) unchanged for both MCP and CLI.

## Before -> After

### Before
- MCP and CLI share `query_jira` -> `_format_issue`: key, `Summary:`, full `Fields:` JSON (`json.dumps` of all Jira fields), numbered `Comments:` (`{n}. {author}: {body}`).

### After
- MCP: `query_jira_for_mcp` -> `_format_issue_mcp`: key, `Summary:`, `Description:` (plain), `Labels:` (comma-separated Jira labels), `Comments:` lines `{author}: {body}` (no numbering; up to 70 comments unchanged).
- CLI: still `query_jira` -> `_format_issue` with `Fields:` JSON and numbered comments.

## Details

**Step 1.1 clarifications (agreed):**

1. **Issue sections (MCP):** `KEY` line, `Summary:`, `Description:` (plain text from Jira description), `Labels:` from `fields.labels` (not epic link).
2. **Tags:** Jira `labels` only; render as comma-separated on one line, or `(none)` when empty.
3. **Epic link:** out of scope (not in MCP output).
4. **Scope:** MCP `jira_fetch` only; CLI `spectask-mcp run --issue` keeps current output.
5. **Comments (MCP):** `{author}: {body}` per line, no index prefix; `COMMENT_MAX_FETCH = 70` and tail-window behavior unchanged.
6. **Listing / not-found:** unchanged — five open issues as `key<TAB>summary` for MCP and CLI.
7. **Description plain text:** prefer `renderedFields.description` (HTML stripped via `_strip_html`); else string `fields.description`; else ADF `fields.description` via `_adf_to_plain`; empty -> `(none)` under `Description:`.
8. **Out of scope (recommended but declined):** status, issue type, assignee, priority, parent, dates as separate plain lines.

**MCP output shape (exact labels):**

```
{key}
Summary: {summary}

Description:
{description plain or (none)}

Labels: {label1, label2}
(or Labels: (none))

Comments:
{author}: {body}
...
(or Comments: (none))
```

## Execution Scheme
> Each step id is the subtask filename.
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions — even if a step seems trivial or small.
- Phase 1 (sequential): step `1-bundle-description-labels` -> step `2-mcp-plain-formatter`
