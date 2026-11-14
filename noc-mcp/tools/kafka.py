"""Kafka in the data path (read-only, from exporter metrics in Prometheus)."""
from __future__ import annotations

from typing import Optional

from clients.prometheus import Prometheus, render
from context import get_context
from schemas.common import ToolError, is_tbd, ok, window
from tools._base import tool


@tool("prometheus")
def get_consumer_lag(group: str, topic: str = ".*", start: Optional[str] = None, end: Optional[str] = None) -> dict:
    """Consumer-group lag per partition over the window: start, end, max and trend. Growing lag = consumer too slow or stuck;
    lag that later drops while data is missing may mean retention loss. Default window: last 60 minutes."""
    ctx = get_context()
    tmpl = (ctx.section("kafka_queries") or {}).get("consumer_lag_by_partition")
    if is_tbd(tmpl):
        raise ToolError("not_configured", "kafka_queries.consumer_lag_by_partition is TBD")
    tr = window(start, end)
    series, src = Prometheus(ctx).range(render(tmpl, group=group, topic=topic, range=tr.prom_range), tr.start, tr.end)
    parts = []
    for s in series[:100]:
        pts = [v for _, v in s["values"] if v is not None]
        if not pts:
            continue
        first, last = pts[0], pts[-1]
        trend = "growing" if last > first * 1.2 + 10 else "shrinking" if last < first * 0.8 else "flat"
        parts.append({"topic": s["labels"].get("topic"), "partition": s["labels"].get("partition"),
                      "start": first, "end": last, "max": max(pts), "trend": trend})
    parts.sort(key=lambda p: -(p["end"] or 0))
    summary = {"partitions": len(parts), "total_lag_end": sum(p["end"] for p in parts),
               "growing": sum(p["trend"] == "growing" for p in parts)}
    return ok(src, {"group": group, "topic": topic, "summary": summary, "top_partitions": parts[:20]}, tr,
              truncated=len(parts) > 20)
