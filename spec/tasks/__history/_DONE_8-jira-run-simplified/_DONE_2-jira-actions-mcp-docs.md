# Step 2: query_jira, MCP description, CLI doc line

## Goal
Implement the simplified branching in `query_jira`, drop ranking and multi-list not-found UX, strip comments from `_format_issue`, and align MCP `jira_fetch` and `run_cmd` doc text.

## Approach
Depends on Step 1: `fetch_issue_bundle_via_jira` must no longer call `/comment`, so `IssueBundle.comments` is always empty before this step revises formatting.

Rebuild `query_jira` as: load backend; compute `pairs = list_open_issues(limit=5)` once per call; if `issue_key` set and `get_issue_bundle` returns non-`None`, return `_format_issue` (fields only); otherwise return `_format_list(pairs)`. Remove `difflib` import and all ranking helpers/constants. `_format_issue` omits the Comments section entirely (no `"Comments:"` header, no enumerated lines). Update `spectask_mcp/mcp_app.py` tool description to describe five-issue list and no comments. Adjust `spectask_mcp/run_cmd.py` module docstring success line if it still implies comments or large listings.

## Affected files
- `spectask_mcp/jira_actions.py`
- `spectask_mcp/mcp_app.py`
- `spectask_mcp/run_cmd.py`

## Code changes (before / after)

### `spectask_mcp/jira_actions.py` -- imports

**Before**

```python
from __future__ import annotations

import difflib
import json

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.factory import backend_from_config
from spectask_mcp.jira.http_common import JiraHttpTraceFn
from spectask_mcp.jira.types import IssueBundle
```

Behavior: `difflib` is only used by ranking helpers.

**After**

```python
from __future__ import annotations

import json

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.factory import backend_from_config
from spectask_mcp.jira.http_common import JiraHttpTraceFn
from spectask_mcp.jira.types import IssueBundle
```

Behavior: drop `difflib` after deleting `_rank_pairs_for_query`.

### `spectask_mcp/jira_actions.py` -- listing limits and `_rank_pairs_for_query`

**Before**

```python
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
```

Behavior: pool and fuzzy candidates for legacy not-found UX.

**After**

```python
# _LIST_LIMIT, _NOT_FOUND_POOL_LIMIT, _CANDIDATE_LIMIT, _CANDIDATE_SCORE_FLOOR,
# _rank_pairs_for_query removed; listing cap is literal 5 inside query_jira.
```

Behavior: not-found path uses the same five pairs as the bare list branch.

### `spectask_mcp/jira_actions.py` -- module docstring

**Before**

```python
"""Shared Jira query logic for CLI and MCP.

Plaintext formatting matches MCP jira_fetch intent: issue detail with JSON fields body
plus comments; unresolved listing as newline-separated key/summary pairs.

CLI exit semantics are enforced in ``run_once`` (see ``run_cmd.py``). This layer
propagates ``JiraConnectionError`` for unreachable Jira; callers map that to exit 3.

Exit code reference for CLI wrappers:
    0 - success (stdout carries ``query_jira`` result).
    1 - usage/misc (e.g. invalid auth fields in loaded config detected at client init).
    2 - missing config (handled in ``run_cmd``, not here).
    3 - ``JiraConnectionError`` from transport/HTTP failures.
"""
```

Behavior: promises comments and generic listing wording.

**After**

```python
"""Shared Jira query logic for CLI and MCP.

Plaintext formatting matches MCP jira_fetch intent: issue detail with JSON fields only
(no comments). Unresolved listing is up to five newest-created issues as ``key<TAB>summary`` lines.

A wrong or missing ``issue_key`` yields the same listing shape as when no key is passed (no not-found banner).

CLI exit semantics are enforced in ``run_once`` (see ``run_cmd.py``). This layer
propagates ``JiraConnectionError`` for unreachable Jira; callers map that to exit 3.

Exit code reference for CLI wrappers:
    0 - success (stdout carries ``query_jira`` result).
    1 - usage/misc (e.g. invalid auth fields in loaded config detected at client init).
    2 - missing config (handled in ``run_cmd``, not here).
    3 - ``JiraConnectionError`` from transport/HTTP failures.
"""
```

Behavior: matches five-issue list, no comments, bare list on not-found.

### `spectask_mcp/jira_actions.py` -- `_format_issue`

**Before**

```python
        "Fields:",
        fields_json,
        "",
        "Comments:",
    ]
    if not bundle.comments:
        lines.append("(none)")
    else:
        for i, c in enumerate(bundle.comments, start=1):
```

Behavior: prints Comments block.

**After**

```python
    lines = [
        bundle.key,
        f"Summary: {bundle.summary}",
        "",
        "Fields:",
        fields_json,
    ]
```

Behavior: output ends after fields JSON; no Comments section.

### `spectask_mcp/jira_actions.py` -- `query_jira` body

**Before**

```python
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
```

Behavior: not-found path runs large search and fuzzy candidates.

**After**

```python
        pairs = backend.list_open_issues(limit=5)
        if key is not None:
            bundle = backend.get_issue_bundle(key)
            if bundle is not None:
                return _format_issue(bundle)
        return _format_list(pairs)
```

Behavior: always the same five-issue list when key absent or missing; detail only when bundle exists.

### `spectask_mcp/mcp_app.py` -- `jira_fetch` tool description

**Before**

```python
            description=(
                "Fetch one Jira issue (with comments) when issue_key is found; "
                "if issue_key is set but not found, returns up to 30 possible matches "
                "from open issues then the standard unresolved listing."
            ),
```

Behavior: documents comments and fuzzy matches.

**After**

```python
            description=(
                "When issue_key is omitted or not found: return the five most recently "
                "created unresolved issues as key<TAB>summary lines. "
                "When issue_key exists: return key, summary, and fields JSON (no comments)."
            ),
```

Behavior: matches simplified contract.

### `spectask_mcp/run_cmd.py` -- module docstring

**Before**

```python
    0 - Success; human-readable issue or listing on stdout.
```

**After**

```python
    0 - Success; issue fields (no comments) or five-issue listing on stdout.
```

Behavior: documents new stdout shape.

## Additional actions
- None (module docstring is covered above).
