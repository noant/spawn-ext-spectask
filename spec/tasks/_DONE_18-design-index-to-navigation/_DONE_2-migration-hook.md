# Step 2: Migration in the after-install hook

Status: Done
Suggested model: glm-5.3-flash
Used model: GLM-5.3-flash

## Goal
Existing target repos: spec/design.yaml documents move into spawn/navigation.yaml read-contextual; the file is deleted only after a successful write.

## Approach
Structured round-trip YAML editing via ruamel (guaranteed in the spawn-cli interpreter that runs setup scripts). No string manipulation. Migration runs before uv calls; all failures keep design.yaml intact; best-effort `spawn refresh` after migration so rows render immediately (after-install hooks run after navigation generation in the same install flow).

## Affected files
- `extsrc/setup/install_spectask_mcp.py` — new `_migrate_design_yaml`, call in `main`; FileNotFoundError handling in `_run_uv_best_effort`

## Code changes (before / after)

### `extsrc/setup/install_spectask_mcp.py` — new function

**Before**
Hook only installs spectask-mcp via uv.

**After**
```python
def _migrate_design_yaml(cwd: str) -> None:
    """Move spec/design.yaml documents into spawn/navigation.yaml; delete the file on success."""
    root = Path(cwd)
    design = root / "spec" / "design.yaml"
    if not design.is_file():
        return
    try:
        from ruamel.yaml import YAML
        from ruamel.yaml.comments import CommentedMap, CommentedSeq

        ry = YAML(typ="rt")
        with design.open("r", encoding="utf-8") as fh:
            data = ry.load(fh) or {}
        docs = data.get("documents") or []
        rows = [
            {"path": str(d.get("path", "")).strip(), "description": str(d.get("description", "")).strip()}
            for d in docs
            if isinstance(d, dict) and str(d.get("path", "")).strip()
        ]
        nav = root / "spawn" / "navigation.yaml"
        nav.parent.mkdir(parents=True, exist_ok=True)
        if nav.is_file():
            with nav.open("r", encoding="utf-8") as fh:
                navdata = ry.load(fh)
        else:
            navdata = None
        if not isinstance(navdata, dict):
            navdata = CommentedMap()
        rc = navdata.get("read-contextual")
        if not isinstance(rc, list):
            rc = CommentedSeq()
            navdata["read-contextual"] = rc
        rules_seq = None
        for grp in rc:
            if isinstance(grp, dict) and isinstance(grp.get("rules"), list):
                rules_seq = grp["rules"]
                break
        if rules_seq is None:
            grp = CommentedMap()
            rules_seq = CommentedSeq()
            grp["rules"] = rules_seq
            rc.append(grp)
        known = set()
        for section in (navdata.get("read-required"), rc):
            if not isinstance(section, list):
                continue
            for g in section:
                if isinstance(g, dict):
                    for lst in (g.get("rules"), g.get("files")):
                        for item in lst or []:
                            if isinstance(item, dict) and item.get("path"):
                                known.add(str(item["path"]))
        changed = False
        for row in rows:
            if row["path"] in known:
                continue
            m = CommentedMap()
            m["path"] = row["path"]
            m["description"] = row["description"]
            rules_seq.append(m)
            changed = True
        with nav.open("w", encoding="utf-8") as fh:
            ry.dump(navdata, fh)
        design.unlink()
        if changed:
            subprocess.run(["spawn", "refresh"], cwd=str(root), check=False)
    except Exception as exc:
        print(f"spectask: design.yaml migration skipped: {exc}", file=sys.stderr)
        return
```
Failures keep the source file; duplicates skipped by exact path comparison; deletion only after the navigation write succeeds.

### `extsrc/setup/install_spectask_mcp.py` — `_run_uv_best_effort`

**Before**
Does not catch FileNotFoundError when uv is absent.

**After**
Wrap the subprocess.run call with `except FileNotFoundError:` logging to stderr and returning.

### `extsrc/setup/install_spectask_mcp.py` — main()

**Before**
```python
def main() -> int:
    cwd = _cwd()
    pkg = "spectask-mcp"
    _run_uv_best_effort(["uv", "tool", "install", pkg], cwd)
    _run_uv_best_effort(["uv", "tool", "upgrade", pkg], cwd)
    _run_interactive_setup(cwd)
    return 0
```

**After**
```python
def main() -> int:
    cwd = _cwd()
    _migrate_design_yaml(cwd)
    pkg = "spectask-mcp"
    _run_uv_best_effort(["uv", "tool", "install", pkg], cwd)
    _run_uv_best_effort(["uv", "tool", "upgrade", pkg], cwd)
    _run_interactive_setup(cwd)
    return 0
```

## Additional actions
- Smoke test in a temp dir: spec/design.yaml with 2 documents + existing navigation.yaml with a `- rules: []` contextual group; run the function; verify rows appended as valid YAML, file removed; second run is a no-op.
- Release order: spawn-cli 35 must be published (PyPI) before spectask 2.0.0 propagates, otherwise older CLI prunes migrated rows on next refresh.
