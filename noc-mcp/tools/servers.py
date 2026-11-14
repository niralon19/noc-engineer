"""Monitored capture servers: drops at NIC / kernel / capture application (read-only)."""
from __future__ import annotations

import re
from typing import Optional

from clients.prometheus import Prometheus, render, series_key
from context import get_context
from schemas.common import ToolError, is_tbd, not_configured, ok, parse_duration, window
from tools._base import as_list, tool


@tool("prometheus")
def get_server_drops(servers: list[str], start: Optional[str] = None, end: Optional[str] = None,
                     compare: str = "1d") -> dict:
    """Packet/record drops and load on the given servers for the window (NIC rx drops, capture-app drops, softirq...),
    per server, with the same window at the comparison offset. Compare servers of the same feed: one server = local
    problem; all servers = upstream/shared. Default window: last 60 minutes."""
    ctx = get_context()
    names = as_list(servers)
    if not names:
        raise ToolError("bad_argument", "pass at least one server (see get_rule_path)")
    tr = window(start, end)
    queries = {k: v for k, v in (ctx.section("server_queries") or {}).items() if not is_tbd(v)}
    if not queries:
        raise not_configured("server_queries")
    prom = Prometheus(ctx)
    vals = {"instances": "|".join(re.escape(n) for n in names), "range": tr.prom_range}
    out, src = {}, "prometheus"
    for name, tmpl in queries.items():
        q = render(tmpl, **vals)
        cur, src = prom.instant(q, tr.end)
        base = {}
        for o in as_list(compare)[:2]:
            b, _ = prom.instant(q, tr.end - parse_duration(o))
            base[o] = {series_key(s["labels"]): s["value"] for s in b}
        out[name] = {"query": q, "by_server": {series_key(s["labels"]): s["value"] for s in cur}, "baselines": base}
    missing = [k for k, v in (ctx.section("server_queries") or {}).items() if is_tbd(v)]
    return ok(src, {"servers": names, "measures": out}, tr, notes=[f"not configured: {missing}"] if missing else [])
