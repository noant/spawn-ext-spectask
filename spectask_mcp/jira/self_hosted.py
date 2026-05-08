"""REST client for Jira Server/Data Center (self-hosted PAT).

Some older Jira Server releases may not accept ``Authorization: Bearer`` for PATs;
if integration tests fail against your instance, verify supported auth for your version.
"""

from __future__ import annotations

from typing import Any

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.jira.http_common import (
    JiraHttpTraceFn,
    build_httpx_client,
    fetch_issue_bundle,
    fetch_open_issues,
)
from spectask_mcp.jira.types import IssueBundle


class SelfHostedJiraClient(JiraBackend):
    def __init__(
        self,
        cfg: SpectaskLocalConfig,
        trace: JiraHttpTraceFn | None = None,
    ) -> None:
        if not cfg.jira.pat_token:
            raise ValueError("self_hosted Jira requires pat_token")
        self._base = cfg.jira.address
        self._client = build_httpx_client(cfg)
        self._token = cfg.jira.pat_token
        self._trace = trace

    def _prepare(self, kwargs: dict[str, Any]) -> None:
        merged = dict(kwargs.get("headers") or ())
        merged["Authorization"] = f"Bearer {self._token}"
        kwargs["headers"] = merged

    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle(
            self._client, self._base, key, self._prepare, trace=self._trace
        )

    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        return fetch_open_issues(
            self._client, self._base, self._prepare, limit, trace=self._trace
        )

    def close(self) -> None:
        self._client.close()
