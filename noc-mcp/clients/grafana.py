"""Grafana API client: Alertmanager silences (used as maintenance windows when configured)."""
from __future__ import annotations

from clients.http import bearer
from context import Context
from schemas.common import is_tbd, not_configured


class Grafana:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.cfg = ctx.section("maintenance")
        if is_tbd(self.cfg.get("grafana_url")):
            raise not_configured("maintenance.grafana_url")

    def silences(self) -> list[dict]:
        return self.ctx.http.get(f"{self.cfg['grafana_url'].rstrip('/')}/api/alertmanager/grafana/api/v2/silences",
                                 headers=bearer(self.cfg.get("grafana_token"))) or []
