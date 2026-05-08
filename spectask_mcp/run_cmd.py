"""One-shot CLI fetch from spec/.config Jira settings.

Exit codes:
    0 - Success; human-readable issue or listing on stdout.
    1 - Usage or miscellaneous errors (e.g. invalid auth for selected Jira type).
    2 - No valid config (missing spec workspace, missing/unreadable config.yaml).
    3 - Jira unreachable (connection timeout, DNS, HTTP errors after connect).
"""

from __future__ import annotations

import sys

from spectask_mcp.config import load_optional_config
from spectask_mcp.jira.base import JiraConnectionError
from spectask_mcp.jira_actions import query_jira

_MISSING_CFG = (
    "spectask-mcp: no valid Jira config. "
    "Create spec/.config/config.yaml (run `spectask-mcp interactive`)."
)


def run_once(*, issue_key: str | None, verbose: bool = False) -> int:
    """Load optional config from spec/.config; print issue bundle or listing; return exit code."""
    cfg = load_optional_config()
    if cfg is None:
        print(_MISSING_CFG, file=sys.stderr)
        return 2
    try:
        trace = None
        if verbose:
            def _trace(method: str, url: str, status: int, body: str) -> None:
                print(
                    f"{method} {url} -> {status}\n{body}\n",
                    file=sys.stderr,
                    flush=True,
                )

            trace = _trace
        out = query_jira(cfg, issue_key, trace=trace)
    except JiraConnectionError as exc:
        print(f"Jira server unreachable: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f"spectask-mcp run: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"spectask-mcp run: {exc}", file=sys.stderr)
        return 1
    print(out)
    return 0
