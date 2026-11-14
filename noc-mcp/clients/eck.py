"""Elasticsearch (ECK) client: bounded search + aggregations, read-only."""
from __future__ import annotations

from typing import Optional

from context import Context
from schemas.common import TimeRange, iso, is_tbd, not_configured


class Elastic:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.cfg = ctx.section("elasticsearch")
        if is_tbd(self.cfg.get("url")):
            raise not_configured("elasticsearch.url")

    def search(self, index: str, query: str, tr: TimeRange, size: int, group_by: Optional[str] = None) -> dict:
        ts = self.cfg.get("timestamp_field", "@timestamp")
        body = {
            "size": size, "track_total_hits": True, "sort": [{ts: "asc"}],
            "query": {"bool": {"filter": [{"range": {ts: {"gte": iso(tr.start), "lte": iso(tr.end)}}}],
                               "must": [{"query_string": {"query": query or "*"}}]}},
        }
        if group_by:
            body["aggs"] = {"by": {"terms": {"field": group_by, "size": 20},
                                   "aggs": {"first_seen": {"min": {"field": ts}}}}}
        auth = (self.cfg["user"], self.cfg.get("password", "")) if self.cfg.get("user") else None
        return self.ctx.http.post(f"{self.cfg['url'].rstrip('/')}/{index}/_search", json=body, auth=auth)
