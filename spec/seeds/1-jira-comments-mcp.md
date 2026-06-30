linked task: none

Add Jira issue comments to spectask-mcp output when fetching a single issue (CLI `run --issue` and MCP `jira_fetch` with a key).

## Current state

- Task 8 removed comment REST traffic: `fetch_issue_bundle_via_jira` always sets `comments=[]`; `_format_issue` has no Comments block; MCP tool description says "no comments".
- `IssueBundle` still has a `comments: list[str]` field (unused).
- Older implementation had paginated `/comment` fetch plus ADF/HTML-to-plain helpers (removed in task 8).

## Desired direction

- When a single issue resolves, include a readable Comments section (author, created date, plain body per comment — exact format TBD in spec).
- Listing mode (no key / key not found) stays as today: five `key<TAB>summary` lines only.
- Respect deployment split: Cloud REST v3 vs self-hosted v2 (same pattern as listing helpers in `http_cloud.py` / `http_self_hosted.py` or shared helper in `http_common.py`).
- Update `spec/design/hla.md` paragraph that currently states bundles never fetch comments.

## Open questions (for spectask-create Step 1)

- How many comments? All paginated vs cap (e.g. last 20).
- Plain-text rules for Cloud ADF vs self-hosted HTML/wiki markup.
- Whether `spectask-from-jira` skill should mention comments as optional import context.
- New MCP tool vs extending `jira_fetch` only.

## Touch points (likely)

- `spectask_mcp/jira/http_common.py` — comment fetch + body normalization
- `spectask_mcp/jira_actions.py` — `_format_issue`
- `spectask_mcp/mcp_app.py` — tool description
- `spectask_mcp/jira/types.py` — comment item shape if more than plain strings
