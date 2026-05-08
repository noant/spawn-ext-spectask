"""Data types for Jira issue payloads."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IssueBundle:
    """One issue with all comments, for MCP/CLI serialization."""

    key: str
    summary: str
    fields: dict[str, Any]
    comments: list[str]
