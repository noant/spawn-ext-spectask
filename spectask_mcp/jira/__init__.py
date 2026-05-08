"""Jira REST v3 backends (self-hosted PAT and Atlassian Cloud Basic)."""

from __future__ import annotations

from spectask_mcp.jira.base import JiraBackend, JiraConnectionError
from spectask_mcp.jira.cloud import AtlassianCloudJiraClient
from spectask_mcp.jira.factory import backend_from_config
from spectask_mcp.jira.http_common import OPEN_ISSUES_JQL
from spectask_mcp.jira.pycontribs_factory import connect_jira_client
from spectask_mcp.jira.self_hosted import SelfHostedJiraClient
from spectask_mcp.jira.types import IssueBundle

__all__ = [
    "OPEN_ISSUES_JQL",
    "AtlassianCloudJiraClient",
    "IssueBundle",
    "JiraBackend",
    "JiraConnectionError",
    "SelfHostedJiraClient",
    "backend_from_config",
    "connect_jira_client",
]
