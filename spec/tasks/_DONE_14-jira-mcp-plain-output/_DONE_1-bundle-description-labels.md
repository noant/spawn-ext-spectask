# Step 1: IssueBundle description and labels from Jira fetch

Status: Done | model: claude-4.6-sonnet-medium

## Goal
Extend `IssueBundle` and `fetch_issue_bundle_via_jira` so description (plain) and labels are available to formatters without dumping full `fields` JSON for MCP.

## Approach
1. Add `description: str` and `labels: list[str]` to `IssueBundle`.
2. Add `_description_plain` and `_labels_from_fields` in `http_common.py` (reuse `_strip_html`, `_adf_to_plain`).
3. Read `renderedFields` from `issue.raw` alongside `fields` in `fetch_issue_bundle_via_jira`.
4. Keep `fields: dict[str, Any]` on the bundle for CLI `_format_issue` JSON block.

## Affected files
- `spectask_mcp/jira/types.py` — `IssueBundle`
- `spectask_mcp/jira/http_common.py` — `_description_plain`, `_labels_from_fields`, `fetch_issue_bundle_via_jira`

## Code changes (before / after)

### `spectask_mcp/jira/types.py` — `IssueBundle`

**Before**
```python
@dataclass
class IssueBundle:
    """One issue with comments, for MCP/CLI serialization."""

    key: str
    summary: str
    fields: dict[str, Any]
    comments: list[IssueComment]
```
Bundle has no pre-parsed description or labels.

**After**
```python
@dataclass
class IssueBundle:
    """One issue with comments, for MCP/CLI serialization."""

    key: str
    summary: str
    description: str
    labels: list[str]
    fields: dict[str, Any]
    comments: list[IssueComment]
```
Plain description and label list populated at fetch time; `fields` retained for CLI JSON dump.

### `spectask_mcp/jira/http_common.py` — `_description_plain`, `_labels_from_fields`

**Before**
```python
    if isinstance(body, dict):
        return _adf_to_plain(body).strip()
    return ""


def _raise_requests_http(resp: requests.Response) -> None:
```
No issue-level description or label helpers between `_comment_body_text` and `_raise_requests_http`.

**After**
```python
def _description_plain(
    fields: dict[str, Any],
    rendered_fields: dict[str, Any] | None,
) -> str:
    rendered = rendered_fields if isinstance(rendered_fields, dict) else {}
    rd = rendered.get("description")
    if isinstance(rd, str) and rd.strip():
        return _strip_html(rd)
    desc = fields.get("description")
    if isinstance(desc, str) and desc.strip():
        return desc.strip()
    if isinstance(desc, dict):
        return _adf_to_plain(desc).strip()
    return ""


def _labels_from_fields(fields: dict[str, Any]) -> list[str]:
    raw = fields.get("labels")
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _raise_requests_http(resp: requests.Response) -> None:
```
Description prefers rendered HTML, then ADF/string; labels from Jira `labels` array.

### `spectask_mcp/jira/http_common.py` — `fetch_issue_bundle_via_jira`

**Before**
```python
    fields = raw.get("fields")
    if not isinstance(fields, dict):
        fields = {}
    summary_raw = fields.get("summary")
    summary = "" if summary_raw is None else str(summary_raw)

    comments_ordered = _paginated_issue_comments_via_session(jira, safe_key)

    return IssueBundle(
        key=key,
        summary=summary,
        fields=dict(fields),
        comments=comments_ordered,
    )
```
Only summary extracted besides raw fields dict.

**After**
```python
    fields = raw.get("fields")
    if not isinstance(fields, dict):
        fields = {}
    rendered_fields = raw.get("renderedFields")
    summary_raw = fields.get("summary")
    summary = "" if summary_raw is None else str(summary_raw)
    description = _description_plain(fields, rendered_fields)
    labels = _labels_from_fields(fields)

    comments_ordered = _paginated_issue_comments_via_session(jira, safe_key)

    return IssueBundle(
        key=key,
        summary=summary,
        description=description,
        labels=labels,
        fields=dict(fields),
        comments=comments_ordered,
    )
```
Bundle carries plain description and labels for MCP formatter; CLI still uses `fields`.

## Additional actions
- Grep for `IssueBundle(` construction sites; only `fetch_issue_bundle_via_jira` should construct bundles (update if tests exist).
