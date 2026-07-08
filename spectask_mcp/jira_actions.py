"""Shared Jira query logic for CLI and MCP.

CLI issue detail uses ``_format_issue`` (Fields JSON, numbered comments).
MCP ``jira_fetch`` uses ``_format_issue_mcp`` (plain description, labels, unnumbered comments).
Listing is up to five issues assigned to the current user, unresolved,
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
        "",
        "Comments:",
    ]
    if not bundle.comments:
        lines.append("(none)")
    else:
        for i, comment in enumerate(bundle.comments, start=1):
            body = comment.body.strip() if comment.body else ""
            author = comment.author.strip() if comment.author else "unknown"
            if body:
                lines.append(f"{i}. {author}: {body}")
            else:
                lines.append(f"{i}. {author}:")
    return "\n".join(lines)


def _format_issue_mcp(bundle: IssueBundle) -> str:
    lines = [
        bundle.key,
        f"Summary: {bundle.summary}",
        "",
        "Description:",
        bundle.description.strip() if bundle.description.strip() else "(none)",
        "",
    ]
    if bundle.labels:
        lines.append(f"Labels: {', '.join(bundle.labels)}")
    else:
        lines.append("Labels: (none)")
    lines.extend(["", "Comments:"])
    if not bundle.comments:
        lines.append("(none)")
    else:
        for comment in bundle.comments:
            body = comment.body.strip() if comment.body else ""
            author = comment.author.strip() if comment.author else "unknown"
            if body:
                lines.append(f"{author}: {body}")
            else:
                lines.append(f"{author}:")
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


def query_jira_for_mcp(
    cfg: SpectaskLocalConfig,
    issue_key: str | None,
    trace: JiraHttpTraceFn | None = None,
) -> str:
    """Run one Jira query for MCP: plain issue detail when key resolves, else listing.

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
                return _format_issue_mcp(bundle)
        return _format_list(pairs)
    finally:
        close = getattr(backend, "close", None)
        if callable(close):
            close()
