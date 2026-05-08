"""Select Jira backend from local config."""

from __future__ import annotations

from spectask_mcp.config import SpectaskLocalConfig
from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.jira.cloud import AtlassianCloudJiraClient
from spectask_mcp.jira.self_hosted import SelfHostedJiraClient


def backend_from_config(cfg: SpectaskLocalConfig) -> JiraBackend:
    if cfg.jira.type == "self_hosted":
        return SelfHostedJiraClient(cfg)
    if cfg.jira.type == "atlassian_cloud":
        return AtlassianCloudJiraClient(cfg)
    raise ValueError(f"unknown jira.type: {cfg.jira.type!r}")
