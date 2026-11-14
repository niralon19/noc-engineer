"""Server-side policy: write gate and audit log. SOUL.md is not a permission mechanism; this is."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from context import Context
from schemas.common import ToolError, iso, now

SECRET_KEYS = ("token", "password", "secret", "authorization", "api_key")


def writes_allowed(ctx: Context) -> bool:
    return str(ctx.section("security").get("allow_writes", "false")).lower() in ("1", "true", "yes")


def require_writes(ctx: Context, tool: str) -> None:
    if not writes_allowed(ctx):
        raise ToolError("permission_denied", f"{tool} is a write tool and writes are disabled on this server "
                                             "(security.allow_writes=false). Return the result instead.")


def redact(obj):
    if isinstance(obj, dict):
        return {k: ("***" if any(s in k.lower() for s in SECRET_KEYS) else redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    return obj


def audit(ctx: Context, tool: str, args: dict, outcome: str) -> None:
    path = ctx.section("security").get("audit_log")
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {"at": iso(now()), "tool": tool, "outcome": outcome,
           "args_sha256": hashlib.sha256(json.dumps(redact(args), sort_keys=True, default=str).encode()).hexdigest(),
           "args": redact({k: v for k, v in args.items() if k != "investigation"})}
    with p.open("a") as f:
        f.write(json.dumps(rec) + "\n")
