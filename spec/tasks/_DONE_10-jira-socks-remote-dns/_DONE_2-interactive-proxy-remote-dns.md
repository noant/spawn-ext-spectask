# Step 2: Interactive wizard writes `remote_dns`

## Goal
When the user enables SOCKS5 in `spectask-mcp interactive` (or `interactive --setup` after the configure gate), prompt for remote DNS and write `proxy.remote_dns` into `spec/.config/config.yaml`.

## Approach
Inside `run_interactive`, only when `proxy_enabled` is true: after SOCKS password prompt, call `_prompt_yes_no` for remote DNS; pass `remote_dns` into `ProxySection` and rely on `config_to_ordered_dict` for YAML output.

## Affected files
- `spectask_mcp/config_prompts.py` -- `run_interactive`, `ProxySection` construction at end of wizard

## Code changes (before / after)

### `spectask_mcp/config_prompts.py` -- SOCKS block and `ProxySection` in `run_interactive`

**Before**
```python
        socks_host = "127.0.0.1"
        socks_port = 1080
        socks_username = ""
        socks_password = ""

        if proxy_enabled:
            host = _prompt_nonempty("SOCKS5 host: ")
            ...
            socks_password = getpass("SOCKS5 password (optional, input hidden): ")

        jira = JiraSection(
```

**After**
```python
        socks_host = "127.0.0.1"
        socks_port = 1080
        socks_username = ""
        socks_password = ""
        remote_dns = False

        if proxy_enabled:
            host = _prompt_nonempty("SOCKS5 host: ")
            ...
            socks_password = getpass("SOCKS5 password (optional, input hidden): ")

            yn_rd = _prompt_yes_no(
                "Resolve Jira hostname through the proxy (remote DNS / socks5h)?",
                default_no=True,
            )
            if yn_rd is None:
                print("Answer y or n (empty means No); aborted.", file=sys.stderr)
                return 1
            remote_dns = yn_rd

        jira = JiraSection(
```

Initializes `remote_dns` to false when proxy is off; when proxy is on, mandatory y/n with default No matches safe default (local DNS unchanged).

**Before**
```python
        proxy = ProxySection(
            enabled=proxy_enabled,
            socks_host=socks_host,
            socks_port=socks_port,
            socks_username=socks_username,
            socks_password=socks_password,
        )
```

**After**
```python
        proxy = ProxySection(
            enabled=proxy_enabled,
            socks_host=socks_host,
            socks_port=socks_port,
            socks_username=socks_username,
            socks_password=socks_password,
            remote_dns=remote_dns,
        )
```

Persists the answers into the dataclass written to YAML.

## Additional actions
- Run `spectask-mcp interactive` in a TTY: enable SOCKS, answer Yes to remote DNS, inspect generated `spec/.config/config.yaml` for `remote_dns: true`.
