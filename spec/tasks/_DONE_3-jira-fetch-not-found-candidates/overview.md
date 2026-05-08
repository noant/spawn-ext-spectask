# 3: Jira fetch not-found candidate hints

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
When `jira_fetch` / CLI requests a specific issue key that does not exist, prepend up to 30 likely candidate issues (from the open-issue pool) before the usual unresolved listing.

## Design overview
- Affected modules: `spectask_mcp/jira_actions.py` (formatting and query flow); optional docstring-only touch `spectask_mcp/mcp_app.py` (tool description).
- Files and symbols:
  - `spectask_mcp/jira_actions.py`: add `import difflib`; constants `_LIST_LIMIT`, `_NOT_FOUND_POOL_LIMIT`, `_CANDIDATE_LIMIT`, `_CANDIDATE_SCORE_FLOOR`; helpers `_format_issue`, `_format_list`, `_rank_pairs_for_query`; `query_jira` extended branch when `key is not None` and `get_issue_bundle` returns `None`.
  - `spectask_mcp/mcp_app.py`: `app.add_tool` / `_jira_fetch_impl` description string for `jira_fetch` to mention candidate block + listing.
- Data flow: unchanged Jira API surface (`JiraBackend.get_issue_bundle`, `list_open_issues`). On not-found only: call `list_open_issues(limit=_NOT_FOUND_POOL_LIMIT)` where `_NOT_FOUND_POOL_LIMIT >= _LIST_LIMIT` (e.g. 100 vs 50), rank pairs `(key, summary)` against the requested string, emit labeled candidate section (cap `_CANDIDATE_LIMIT` at 30), then emit the same unresolved listing as today using the first `_LIST_LIMIT` pairs from that fetch (preserves previous listing size and order).
- Integration points: MCP tool `jira_fetch`, CLI `spectask-mcp run [--issue KEY]` via `run_once` -> `query_jira`.

## Before -> After

### Before
- Missing or unknown issue key: output is only the tab-separated open-issue list (up to `_LIST_LIMIT` rows), with no hint which keys might have matched the user input.

### After
- Unknown issue key (non-empty key provided, `get_issue_bundle` returns `None`): output starts with a short labeled section listing up to 30 candidate rows (key + summary), scored by relevance to the requested key string; then the standard unresolved list (first `_LIST_LIMIT` issues in JQL order).

## Details

### Candidate ranking (stdlib only)

- Normalize with `str.casefold()` for comparisons involving key and summary.
- Score each `(key, summary)` from the fetched pool; higher is better. Suggested ordering:
  1. Exact key match after casefold (should not occur if REST returned None, but harmless).
  2. Issue key starts with the query or contains the query as substring.
  3. Summary contains the full query as substring.
  4. Else `difflib.SequenceMatcher(None, query, issue_key).ratio()` as tie-breaker.
- Sort by score descending, then key ascending for stability.
- Take first `_CANDIDATE_LIMIT` (30) rows with score strictly above a small floor (e.g. `0.34`) so random keys do not fill candidates; if none pass the floor, omit the candidate section body but keep the not-found message (see Format).

### Format (plaintext)

Suggested shape (exact labels can be adjusted but keep ASCII):

```
Issue <KEY> not found.

Possible matches (up to 30):
KEY<TAB>SUMMARY
...

Open unresolved issues:
KEY<TAB>SUMMARY
...
```

If no candidates pass the floor:

```
Issue <KEY> not found.

Open unresolved issues:
...
```

### Constants

- `_CANDIDATE_LIMIT = 30`
- `_LIST_LIMIT = 50` (unchanged effective rows for the main listing block)
- `_NOT_FOUND_POOL_LIMIT = 100` (single search request when key missing on server; must be >= `_LIST_LIMIT`)

When `issue_key` is omitted or blank, behavior stays exactly as today (listing only, one call with `_LIST_LIMIT`).

### Tool description

Update MCP tool description text so callers know a not-found key yields candidates plus listing.

## Code changes (before / after)

### `spectask_mcp/jira_actions.py` — `query_jira` not-found branch + helpers

**Before**

```python
_LIST_LIMIT = 50


def query_jira(cfg: SpectaskLocalConfig, issue_key: str | None) -> str:
    backend = backend_from_config(cfg)
    try:
        key = issue_key.strip() if isinstance(issue_key, str) else None
        if not key:
            key = None

        if key is not None:
            bundle = backend.get_issue_bundle(key)
            if bundle is not None:
                return _format_issue(bundle)
        pairs = backend.list_open_issues(limit=_LIST_LIMIT)
        return _format_list(pairs)
    finally:
        close = getattr(backend, "close", None)
        if callable(close):
            close()
```

**After**

```python
import json
import difflib

_LIST_LIMIT = 50
_NOT_FOUND_POOL_LIMIT = 100
_CANDIDATE_LIMIT = 30
_CANDIDATE_SCORE_FLOOR = 0.34


def _rank_pairs_for_query(query: str, pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    q = query.casefold().strip()
    if not q:
        return []
    scored: list[tuple[float, tuple[str, str]]] = []
    for k, s in pairs:
        kf = k.casefold()
        sf = s.casefold()
        if q == kf:
            score = 1.0
        elif kf.startswith(q) or q in kf:
            score = 0.9
        elif q in sf:
            score = 0.7
        else:
            score = difflib.SequenceMatcher(None, q, kf).ratio()
        scored.append((score, (k, s)))
    scored.sort(key=lambda item: (-item[0], item[1][0]))
    out: list[tuple[str, str]] = []
    for sc, pair in scored:
        if sc <= _CANDIDATE_SCORE_FLOOR:
            break
        out.append(pair)
        if len(out) >= _CANDIDATE_LIMIT:
            break
    return out


def query_jira(cfg: SpectaskLocalConfig, issue_key: str | None) -> str:
    backend = backend_from_config(cfg)
    try:
        key = issue_key.strip() if isinstance(issue_key, str) else None
        if not key:
            key = None

        if key is not None:
            bundle = backend.get_issue_bundle(key)
            if bundle is not None:
                return _format_issue(bundle)
            pairs = backend.list_open_issues(limit=_NOT_FOUND_POOL_LIMIT)
            candidates = _rank_pairs_for_query(key, pairs)
            lines = [f"Issue {key} not found.", ""]
            if candidates:
                lines.extend(["Possible matches (up to 30):", _format_list(candidates), ""])
            lines.extend(["Open unresolved issues:", _format_list(pairs[:_LIST_LIMIT])])
            return "\n".join(lines)
        pairs = backend.list_open_issues(limit=_LIST_LIMIT)
        return _format_list(pairs)
    finally:
        close = getattr(backend, "close", None)
        if callable(close):
            close()
```

Behavior: single bundle fetch attempt; one listing fetch on not-found with `_NOT_FOUND_POOL_LIMIT`; main block uses first `_LIST_LIMIT` pairs.

### `spectask_mcp/mcp_app.py` — `jira_fetch` description

**Before**

```python
            description=(
                "Fetch one Jira issue (with comments) when issue_key is found; "
                "otherwise list open unresolved issues."
            ),
```

**After**

```python
            description=(
                "Fetch one Jira issue (with comments) when issue_key is found; "
                "if issue_key is set but not found, returns up to 30 possible matches "
                "from open issues then the standard unresolved listing."
            ),
```

## Additional verification

- Manual: with valid Jira config, `spectask-mcp run --issue NOPE-99999` shows not-found line, optional candidates, then listing; `spectask-mcp run` without `--issue` unchanged.
- No automated tests required for this repo unless the author adds a test harness later.
