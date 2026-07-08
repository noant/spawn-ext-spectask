"""Data types for Jira issue payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IssueComment:
    """One Jira issue comment for MCP/CLI serialization."""

    author: str
    body: str


@dataclass
class IssueBundle:
    """One issue with comments, for MCP/CLI serialization."""

    key: str
    summary: str
    description: str
    labels: list[str]
    fields: dict[str, Any]
    comments: list[IssueComment]
