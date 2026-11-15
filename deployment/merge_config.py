"""Merge the repo's Hermes config fragment into a live HERMES_HOME/config.yaml.

Managed keys only: model.*, gateway.api_server.*, mcp_servers.noc_mcp.* (everything else in the live file is kept).
Never overwrites a real live value with a placeholder (REPLACE/TBD). Writes a timestamped backup first.
Usage: python3 deployment/merge_config.py SRC_FRAGMENT LIVE_CONFIG [--apply]   (default: show the plan only)
Note: YAML comments in the live file are not preserved; prefer `hermes config set` for single keys.
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

import yaml

MANAGED = (("model",), ("gateway", "api_server"), ("mcp_servers", "noc_mcp"))


def placeholder(v) -> bool:
    return isinstance(v, str) and ("REPLACE" in v or "TBD" in v)


def flat(d, prefix=()):
    for k, v in (d or {}).items():
        if isinstance(v, dict):
            yield from flat(v, prefix + (k,))
        else:
            yield prefix + (k,), v


def get(d, path):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return None
        d = d[p]
    return d


def put(d, path, value):
    for p in path[:-1]:
        d = d.setdefault(p, {})
    d[path[-1]] = value


def plan(src: dict, live: dict) -> list[tuple[tuple, object, object]]:
    changes = []
    for root in MANAGED:
        for path, value in flat(get(src, root) or {}, root):
            cur = get(live, path)
            if placeholder(value) and cur is not None:
                continue                      # keep the real live value
            if cur != value:
                changes.append((path, cur, value))
    return changes


def main() -> int:
    src_p, live_p = Path(sys.argv[1]), Path(sys.argv[2])
    src = yaml.safe_load(src_p.read_text()) or {}
    if not live_p.exists():
        if "--apply" in sys.argv:
            live_p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src_p, live_p)
        print(f"{'seeded' if '--apply' in sys.argv else 'would seed'} {live_p} from {src_p}")
        return 0
    live = yaml.safe_load(live_p.read_text()) or {}
    changes = plan(src, live)
    if not changes:
        print("config.yaml: managed keys already up to date")
        return 0
    for path, cur, new in changes:
        print(f"  {'.'.join(map(str, path))}: {cur!r} -> {new!r}")
    if "--apply" not in sys.argv:
        print(f"{len(changes)} change(s) planned. Re-run with --apply to write (a backup is kept).")
        return 0
    backup = live_p.with_name(f"config.yaml.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.copy(live_p, backup)
    for path, _, new in changes:
        put(live, path, new)
    live_p.write_text(yaml.safe_dump(live, sort_keys=False, allow_unicode=True))
    print(f"applied {len(changes)} change(s); backup: {backup}. Then: hermes config check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
