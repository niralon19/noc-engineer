"""Thin Jira REST v2 client. Policy (dedup, validation, write gate) lives in tools/jira.py."""
from __future__ import annotations

from typing import Any

from clients.http import bearer
from context import Context
from schemas.common import is_tbd, not_configured


class Jira:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.cfg = ctx.section("jira")
        if is_tbd(self.cfg.get("url")):
            raise not_configured("jira.url")
        self.base = self.cfg["url"].rstrip("/") + "/rest/api/2"

    def _auth(self) -> dict:
        if self.cfg.get("user"):
            return {"auth": (self.cfg["user"], self.cfg.get("token", ""))}
        return {"headers": bearer(self.cfg.get("token"))}

    def issue(self, key: str, fields: str) -> Any:
        return self.ctx.http.get(f"{self.base}/issue/{key}", params={"fields": fields}, **self._auth())

    def search(self, jql: str, fields: str, limit: int) -> Any:
        return self.ctx.http.post(f"{self.base}/search", json={"jql": jql, "fields": fields.split(","), "maxResults": limit},
                                  **self._auth())

    def comments(self, key: str) -> list[dict]:
        body = self.ctx.http.get(f"{self.base}/issue/{key}/comment", params={"maxResults": 100}, **self._auth())
        return (body or {}).get("comments", [])

    def add_comment(self, key: str, text: str) -> Any:
        return self.ctx.http.post(f"{self.base}/issue/{key}/comment", json={"body": text}, **self._auth())
