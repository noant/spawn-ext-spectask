"""REST client for Atlassian Cloud (site URL + email/API token Basic)."""

from __future__ import annotations

from typing import Any

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.jira.http_common import (
    build_httpx_client,
    fetch_issue_bundle,
    fetch_open_issues,
)
from spectask_mcp.jira.types import IssueBundle


class AtlassianCloudJiraClient(JiraBackend):
    def __init__(self, cfg: SpectaskLocalConfig) -> None:
        if not cfg.jira.email or not cfg.jira.api_token:
            raise ValueError("atlassian_cloud Jira requires email and api_token")
        self._base = cfg.jira.address
        self._client = build_httpx_client(cfg)
        self._basic = (cfg.jira.email, cfg.jira.api_token)

    def _prepare(self, kwargs: dict[str, Any]) -> None:
        kwargs["auth"] = self._basic

    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle(self._client, self._base, key, self._prepare)

    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues(self._client, self._base, self._prepare, limit)

    def close(self) -> None:
        self._client.close()
