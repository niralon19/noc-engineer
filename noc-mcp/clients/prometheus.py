"""Prometheus / Thanos query client (read-only HTTP API v1). Thanos is used for windows older than local retention."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from clients.http import bearer
from context import Context
from schemas.common import ToolError, is_tbd, not_configured, now


class Prometheus:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.cfg = ctx.section("prometheus")
        self.thanos = ctx.section("thanos")
        if is_tbd(self.cfg.get("url")):
            raise not_configured("prometheus.url")

    def _base(self, oldest: datetime) -> tuple[str, dict, str]:
        hours = float(self.cfg.get("local_retention_hours", 24))
        if oldest < now() - timedelta(hours=hours) and not is_tbd(self.thanos.get("url")):
            return self.thanos["url"].rstrip("/"), bearer(self.thanos.get("token")), "thanos"
        return self.cfg["url"].rstrip("/"), bearer(self.cfg.get("token")), "prometheus"

    def _call(self, path: str, params: dict, oldest: datetime) -> tuple[list, str]:
        base, headers, name = self._base(oldest)
        body = self.ctx.http.get(f"{base}{path}", params=params, headers=headers)
        if not isinstance(body, dict) or body.get("status") != "success":
            err = body.get("error") if isinstance(body, dict) else str(body)[:200]
            raise ToolError("bad_query", f"{name} rejected the query: {err}")
        return body["data"]["result"], name

    def instant(self, query: str, at: datetime) -> tuple[list[dict], str]:
        result, name = self._call("/api/v1/query", {"query": query, "time": at.timestamp()}, at)
        return [{"labels": r.get("metric", {}), "value": _num(r["value"][1])} for r in result], name

    def range(self, query: str, start: datetime, end: datetime, step: Optional[int] = None) -> tuple[list[dict], str]:
        step = step or max(15, int((end - start).total_seconds() // 120))      # <= ~120 points per series
        result, name = self._call("/api/v1/query_range",
                                  {"query": query, "start": start.timestamp(), "end": end.timestamp(), "step": step}, start)
        return [{"labels": r.get("metric", {}), "values": [[int(t), _num(v)] for t, v in r["values"]]} for r in result], name


def _num(v: str) -> Optional[float]:
    try:
        f = float(v)
        return None if f != f else f        # NaN -> None
    except (TypeError, ValueError):
        return None


def render(template: str, **values: str) -> str:
    """Fill {placeholders} in a PromQL template without touching PromQL's own braces."""
    out = template
    for k, v in values.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def series_key(labels: dict) -> str:
    for k in ("instance", "pod", "partition", "server", "host", "topic"):
        if k in labels:
            return f"{k}={labels[k]}"
    return ",".join(f"{k}={v}" for k, v in sorted(labels.items()) if k != "__name__") or "total"
