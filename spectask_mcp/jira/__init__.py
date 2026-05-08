"""Jira backends: Cloud vs self-hosted; REST API version and search paths differ by deployment."""

from __future__ import annotations

from spectask_mcp.jira.base import JiraBackend, JiraConnectionError
from spectask_mcp.jira.cloud import AtlassianCloudJiraClient
from spectask_mcp.jira.factory import backend_from_config
from spectask_mcp.jira.jql import CURRENT_USER_OPEN_ISSUES_JQL
from spectask_mcp.jira.pycontribs_factory import connect_jira_client
from spectask_mcp.jira.self_hosted import SelfHostedJiraClient
from spectask_mcp.jira.types import IssueBundle

__all__ = [
    "CURRENT_USER_OPEN_ISSUES_JQL",
    "AtlassianCloudJiraClient",
    "IssueBundle",
    "JiraBackend",
    "JiraConnectionError",
    "SelfHostedJiraClient",
    "backend_from_config",
    "connect_jira_client",
]
