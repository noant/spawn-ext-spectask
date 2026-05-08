"""Shared Jira query logic for CLI and MCP.

Plaintext formatting matches MCP jira_fetch intent: issue detail with JSON fields only
(no comments). Listing is up to five issues assigned to the current user, unresolved,
newest-created first, as ``key<TAB>summary`` lines (see ``CURRENT_USER_OPEN_ISSUES_JQL`` in ``spectask_mcp.jira.jql``).

A wrong or missing ``issue_key`` yields the same listing shape as when no key is passed (no not-found banner).

CLI exit semantics are enforced in ``run_once`` (see ``run_cmd.py``). This layer
propagates ``JiraConnectionError`` for unreachable Jira; callers map that to exit 3.

Exit code reference for CLI wrappers:
    0 - success (stdout carries ``query_jira`` result).
    1 - usage/misc (e.g. invalid auth fields in loaded config detected at client init).
    2 - missing config (handled in ``run_cmd``, not here).
    3 - ``JiraConnectionError`` from transport/HTTP failures.
"""

from __future__ import annotations

import json

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.factory import backend_from_config
from spectask_mcp.jira.http_common import JiraHttpTraceFn
from spectask_mcp.jira.types import IssueBundle


def _format_issue(bundle: IssueBundle) -> str:
    fields_json = json.dumps(bundle.fields, indent=2, sort_keys=True, default=str)
    lines = [
        bundle.key,
        f"Summary: {bundle.summary}",
        "",
        "Fields:",
        fields_json,
    ]
    return "\n".join(lines)


def _format_list(pairs: list[tuple[str, str]]) -> str:
    if not pairs:
        return "(no open issues returned)"
    return "\n".join(f"{k}\t{s}" for k, s in pairs)


def query_jira(
    cfg: SpectaskLocalConfig,
    issue_key: str | None,
    trace: JiraHttpTraceFn | None = None,
) -> str:
    """Run one Jira query: issue detail when key resolves, else five-issue listing.

    Raises:
        JiraConnectionError: network/HTTP failures talking to Jira.
        ValueError: backend cannot be constructed from config (e.g. missing token).
    """
    backend = backend_from_config(cfg, trace=trace)
    try:
        key = issue_key.strip() if isinstance(issue_key, str) else None
        if not key:
            key = None

        pairs = backend.list_open_issues(limit=5)
        if key is not None:
            bundle = backend.get_issue_bundle(key)
            if bundle is not None:
                return _format_issue(bundle)
        return _format_list(pairs)
    finally:
        close = getattr(backend, "close", None)
        if callable(close):
            close()
