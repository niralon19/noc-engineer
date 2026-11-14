"""Argo CD API client (read-only token): application sync history and status."""
from __future__ import annotations

from clients.http import bearer
from context import Context
from schemas.common import is_tbd, not_configured


class Argo:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.cfg = ctx.section("argocd")
        if is_tbd(self.cfg.get("url")):
            raise not_configured("argocd.url")

    def application(self, name: str) -> dict:
        return self.ctx.http.get(f"{self.cfg['url'].rstrip('/')}/api/v1/applications/{name}",
                                 headers=bearer(self.cfg.get("token")))
