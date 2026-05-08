"""REST client for Jira Server/Data Center (self-hosted PAT).

Some older Jira Server releases may not accept ``Authorization: Bearer`` for PATs;
if integration tests fail against your instance, verify supported auth for your version.
"""

from __future__ import annotations

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    fetch_issue_bundle_via_jira,
)
from spectask_mcp.jira.http_self_hosted import fetch_open_issues_self_hosted
from spectask_mcp.jira.pycontribs_factory import connect_jira_client
from spectask_mcp.jira.types import IssueBundle


class SelfHostedJiraClient(JiraBackend):
    def __init__(
        self,
        cfg: SpectaskLocalConfig,
        trace: JiraHttpTraceFn | None = None,
    ) -> None:
        if not cfg.jira.pat_token:
            raise ValueError("self_hosted Jira requires pat_token")
        self._trace = trace
        self._jira = connect_jira_client(cfg, trace=trace)

    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle_via_jira(
            self._jira,
            key,
            trace=self._trace,
        )

    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues_self_hosted(self._jira, limit, trace=self._trace)

    def close(self) -> None:
        self._jira.close()
