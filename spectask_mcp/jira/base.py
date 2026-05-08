"""Abstract backend for issue fetch operations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from spectask_mcp.jira.types import IssueBundle


class JiraConnectionError(Exception):
    """HTTP failures, timeouts, or transport errors when talking to Jira."""


class JiraBackend(ABC):
    @abstractmethod
    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        ...

    @abstractmethod
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        """Return tuples (key, summary)."""
