"""Shared Jira JQL fragments for listing helpers."""

CURRENT_USER_OPEN_ISSUES_JQL = (
    "assignee = currentUser() AND resolution = Unresolved ORDER BY created DESC"
)
