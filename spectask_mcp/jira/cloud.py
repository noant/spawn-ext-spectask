"""REST client for Atlassian Cloud (site URL + email/API token Basic)."""

from __future__ import annotations

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.jira.http_cloud import fetch_open_issues_cloud
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    fetch_issue_bundle_via_jira,
)
from spectask_mcp.jira.pycontribs_factory import connect_jira_client
from spectask_mcp.jira.types import IssueBundle


class AtlassianCloudJiraClient(JiraBackend):
    def __init__(
        self,
        cfg: SpectaskLocalConfig,
        trace: JiraHttpTraceFn | None = None,
    ) -> None:
        if not cfg.jira.email or not cfg.jira.api_token:
            raise ValueError("atlassian_cloud Jira requires email and api_token")
        self._trace = trace
        self._jira = connect_jira_client(cfg, trace=trace)

    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle_via_jira(
            self._jira,
            key,
            trace=self._trace,
        )

    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues_cloud(self._jira, limit, trace=self._trace)

    def close(self) -> None:
        self._jira.close()
