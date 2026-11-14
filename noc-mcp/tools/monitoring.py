"""Generic monitoring queries: PromQL (Prometheus/Thanos) and logs (ECK). Bounded results."""
from __future__ import annotations

from typing import Optional

from clients.eck import Elastic
from clients.prometheus import Prometheus
from context import get_context
from schemas.common import is_tbd, not_configured, ok, window
from tools._base import tool


@tool("prometheus")
def query_metrics(promql: str, start: Optional[str] = None, end: Optional[str] = None, step_seconds: Optional[int] = None) -> dict:
    """Run a PromQL range query (Thanos is used automatically for old windows). Always aggregate (sum by, topk):
    results are capped. Use rate()/increase() for counters. Default window: last 60 minutes."""
    ctx = get_context()
    tr = window(start, end)
    series, src = Prometheus(ctx).range(promql, tr.start, tr.end, step_seconds)
    cap = int(ctx.section("prometheus").get("max_series", 50))
    data = [{"labels": s["labels"], "points": len(s["values"]), "first": s["values"][0] if s["values"] else None,
             "last": s["values"][-1] if s["values"] else None,
             "min": min((v for _, v in s["values"] if v is not None), default=None),
             "max": max((v for _, v in s["values"] if v is not None), default=None),
             "values": s["values"][:: max(1, len(s["values"]) // 30)]} for s in series[:cap]]
    notes = [f"{len(series)} series returned, showing {cap}: aggregate the query"] if len(series) > cap else []
    return ok(src, {"query": promql, "series": data}, tr, truncated=len(series) > cap, notes=notes)


@tool("eck")
def query_logs(query: str, index: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None,
               size: int = 20, group_by: Optional[str] = None) -> dict:
    """Search logs/records in ECK (Elasticsearch query_string syntax) in a window, oldest first, with an optional terms
    aggregation (group_by field) that includes first_seen per value: use it to find the FIRST new error signature after onset.
    Default window: last 60 minutes; size max 50."""
    ctx = get_context()
    cfg = ctx.section("elasticsearch")
    idx = index or cfg.get("default_index")
    if is_tbd(idx):
        raise not_configured("elasticsearch.default_index (or pass index)")
    tr = window(start, end)
    size = max(0, min(int(size), int(cfg.get("max_hits", 50))))
    body = Elastic(ctx).search(idx, query, tr, size, group_by)
    hits = []
    for h in (body.get("hits") or {}).get("hits", []):
        src = h.get("_source") or {}
        msg = src.get("message") or src.get("log") or ""
        hits.append({"ts": src.get(cfg.get("timestamp_field", "@timestamp")), "index": h.get("_index"),
                     "message": str(msg)[:300],
                     "fields": {k: v for k, v in src.items() if k not in ("message", "log") and not isinstance(v, (dict, list))}})
    total = (body.get("hits") or {}).get("total")
    data = {"index": idx, "query": query, "total": total.get("value") if isinstance(total, dict) else total, "hits": hits}
    if group_by:
        data["groups"] = [{"value": b["key"], "count": b["doc_count"], "first_seen": (b.get("first_seen") or {}).get("value_as_string")}
                          for b in (body.get("aggregations") or {}).get("by", {}).get("buckets", [])]
    return ok("eck", data, tr)
