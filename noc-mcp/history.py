"""Investigation history store. JSONL now (one record per published investigation); swap for the org Postgres later
with the same save()/search() interface. Written by the ingestion bridge, read by search_investigations."""
from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Optional

from context import Context
from schemas.common import ToolError, iso, now, parse_time


class History:
    def __init__(self, ctx: Context):
        cfg = ctx.section("history")
        if cfg.get("backend", "jsonl") != "jsonl":
            raise ToolError("not_configured", f"history backend '{cfg.get('backend')}' not implemented yet (use jsonl)")
        self.path = Path(cfg.get("path") or "/data/noc-history/investigations.jsonl")

    def save(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        rec = dict(record)
        rec.setdefault("created_at", iso(now()))
        with self.path.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    def search(self, rule_id: Optional[str] = None, fingerprint: Optional[str] = None, hop: Optional[str] = None,
               text: Optional[str] = None, since_days: int = 30, limit: int = 10) -> list[dict]:
        if not self.path.exists():
            return []
        cutoff = now() - timedelta(days=since_days)
        out = []
        for line in reversed(self.path.read_text().splitlines()):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("created_at") and parse_time(r["created_at"], cutoff) < cutoff:
                continue
            loc = r.get("suspected_location") or {}
            if rule_id and rule_id not in (loc.get("rule_id"), r.get("rule_id")):
                continue
            if fingerprint and r.get("fingerprint") != fingerprint:
                continue
            if hop and loc.get("hop") != hop:
                continue
            if text and text.lower() not in json.dumps(r).lower():
                continue
            out.append({k: r.get(k) for k in ("investigation_id", "created_at", "status", "headline", "suspected_location",
                                              "onset_time", "fingerprint", "jira_issue", "next_check")})
            if len(out) >= limit:
                break
        return out
