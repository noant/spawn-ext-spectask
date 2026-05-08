# Step 2: Migrate issue bundle fetch (issue plus comments)

## Goal
Implement `JiraBackend.get_issue_bundle` using pycontribs so returned `IssueBundle` matches current plaintext and JSON field formatting in `spectask_mcp.jira_actions`.

## Approach
1. Replace `fetch_issue_bundle(... httpx.Client ...)` calls from `SelfHostedJiraClient` and `AtlassianCloudJiraClient` with logic driven by `jira.JIRA`:
   - Load issue with rendered fields equivalent to `params={"expand": "renderedFields"}` (library keyword such as `expand` on `issue()`).
   - Resolve 404-not-found the same way: return `None` when the issue key does not exist.
2. Paginate comments with `renderedBody` where the library supports it; otherwise use `.raw` from the REST payload to preserve `_comment_body_text` behavior (ADF and HTML stripping).
3. Build `IssueBundle(key=..., summary=..., fields=..., comments=...)` where `fields` remains a plain `dict` suitable for `json.dumps` in `_format_issue` (use `issue.raw` or selective dict copy from the resource).
4. Map transport failures (`JIRAError`, `requests` exceptions) to `JiraConnectionError` with messages similar in spirit to `_raise_http` today.

## Affected files
- `spectask_mcp/jira/self_hosted.py` — `get_issue_bundle`
- `spectask_mcp/jira/cloud.py` — `get_issue_bundle`
- `spectask_mcp/jira/http_common.py` — remove or refactor `fetch_issue_bundle`, `_request` usage for this path; keep `_comment_body_text`, `_adf_to_plain`, `_strip_html` as shared helpers unless moved.

## Code changes (before / after)

### `spectask_mcp/jira/self_hosted.py` — `get_issue_bundle`

**Before**

```python
    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle(
            self._client, self._base, key, self._prepare, trace=self._trace
        )
```

Behavior: delegates to httpx helper.

**After**

```python
    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        return fetch_issue_bundle_via_jira(
            self._jira, key, trace=self._trace
        )
```

Behavior: uses `JIRA` instance from step 1 (`self._jira` replaces `self._client` naming in constructor); implementation lives beside factory or in `http_common` after refactor.

### `spectask_mcp/jira/http_common.py` — `fetch_issue_bundle` signature (removed or replaced)

**Before**

```python
def fetch_issue_bundle(
    client: httpx.Client,
    base_url: str,
    issue_key: str,
    prepare: RequestPrepare,
    trace: JiraHttpTraceFn | None = None,
) -> IssueBundle | None:
```

Behavior: httpx-only; `prepare` injects auth.

**After**

```python
def fetch_issue_bundle_via_jira(
    jira: JIRA,
    issue_key: str,
    trace: JiraHttpTraceFn | None = None,
) -> IssueBundle | None:
```

Behavior: auth already on `JIRA`; trace hook behavior preserved or explicitly narrowed per overview Details.

## Additional actions
- Manual check: `spectask-mcp run --issue <KEY>` matches pre-migration output shape for Fields and Comments sections (ordering of comments by created time unchanged).
