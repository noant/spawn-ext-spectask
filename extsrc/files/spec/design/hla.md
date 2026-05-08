# High-Level Architecture (HLA)

This document describes the high-level architecture and interaction of abstractions in the project.

## spectask-mcp (Jira)

The `spectask_mcp` package talks to Jira via REST API v3. Open-issue listing uses `POST /rest/api/3/search/jql` first; if the server responds with 404 or 410, the client retries once with `POST /rest/api/3/search` (legacy) so Atlassian Cloud and older self-hosted instances both work.
