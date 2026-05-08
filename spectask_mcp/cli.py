"""CLI entry for spectask-mcp."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(prog="spectask-mcp")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_int = sub.add_parser("interactive", help="Write spec/.config/config.yaml via prompts")
    p_int.add_argument(
        "--setup",
        action="store_true",
        help="Called from extension setup: ask whether to configure before the wizard",
    )
    p_run = sub.add_parser("run", help="Fetch Jira issue or list open issues once")
    p_run.add_argument("--issue", default=None, help="Jira issue key, e.g. PROJ-123")
    p_run.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Log each Jira HTTP response (method, URL, status, body) to stderr",
    )
    sub.add_parser("serve", help="Run stdio MCP server")

    ns = p.parse_args(argv)

    if ns.cmd == "interactive":
        from spectask_mcp.config_prompts import run_interactive
        raise SystemExit(run_interactive(prompted_by_setup=ns.setup))

    if ns.cmd == "run":
        from spectask_mcp.run_cmd import run_once
        raise SystemExit(run_once(issue_key=ns.issue, verbose=ns.verbose))

    if ns.cmd == "serve":
        from spectask_mcp.mcp_app import run_stdio
        raise SystemExit(run_stdio())


if __name__ == "__main__":
    main()
