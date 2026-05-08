"""Stdio MCP: optional Jira tools when spec/.config/config.yaml is valid."""

from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from spectask_mcp.config import load_optional_config
from spectask_mcp.jira.base import JiraConnectionError
from spectask_mcp.jira_actions import query_jira


def _stderr_logger() -> logging.Logger:
    log = logging.getLogger("spectask_mcp.mcp_app")
    log.setLevel(logging.INFO)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        log.addHandler(handler)
        log.propagate = False
    return log


def _describe_no_tools_startup() -> str:
    return (
        "spectask-mcp: stdio MCP starting without Jira tools "
        "(no valid spec/.config/config.yaml)."
    )


def _describe_tools_startup() -> str:
    return "spectask-mcp: stdio MCP starting with jira_fetch tool."


def _jira_fetch_impl(issue_key: str | None = None) -> str:
    try:
        cfg = load_optional_config()
        if cfg is None:
            return "No valid Jira configuration found."

        return query_jira(cfg, issue_key)
    except JiraConnectionError as exc:
        return f"Jira server unreachable: {exc}"
    except ValueError as exc:
        return f"Invalid Jira configuration: {exc}"
    except OSError as exc:
        return f"Jira request failed: {exc}"


def run_stdio() -> int:
    """Run the MCP server on stdin/stdout via the official Python MCP SDK (FastMCP)."""
    log = _stderr_logger()
    cfg = load_optional_config()
    if cfg is None:
        log.info("%s", _describe_no_tools_startup())
    else:
        log.info("%s", _describe_tools_startup())

    app = FastMCP(name="spectask-mcp-jira")
    if cfg is not None:
        app.add_tool(
            _jira_fetch_impl,
            name="jira_fetch",
            description=(
                "Fetch one Jira issue (with comments) when issue_key is found; "
                "if issue_key is set but not found, returns up to 30 possible matches "
                "from open issues then the standard unresolved listing."
            ),
        )

    try:
        app.run(transport="stdio")
    except KeyboardInterrupt:
        return 130
    return 0
