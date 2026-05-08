"""Select Jira backend from local config."""

from __future__ import annotations

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.jira.cloud import AtlassianCloudJiraClient
from spectask_mcp.jira.http_common import JiraHttpTraceFn
from spectask_mcp.jira.self_hosted import SelfHostedJiraClient


def backend_from_config(
    cfg: SpectaskLocalConfig,
    trace: JiraHttpTraceFn | None = None,
) -> JiraBackend:
    if cfg.jira.type == "self_hosted":
        return SelfHostedJiraClient(cfg, trace=trace)
    if cfg.jira.type == "atlassian_cloud":
        return AtlassianCloudJiraClient(cfg, trace=trace)
    raise ValueError(f"unknown jira.type: {cfg.jira.type!r}")
