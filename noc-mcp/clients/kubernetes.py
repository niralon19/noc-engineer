"""Kubernetes API client for both clusters (Rancher, OpenShift). Read-only service accounts."""
from __future__ import annotations

from typing import Optional

from clients.http import bearer
from context import Context
from schemas.common import ToolError, is_tbd, not_configured


class Kube:
    def __init__(self, ctx: Context, cluster: str):
        self.ctx = ctx
        clusters = ctx.section("kubernetes").get("clusters") or {}
        if cluster not in clusters:
            raise ToolError("bad_argument", f"unknown cluster '{cluster}'; known: {sorted(clusters)}")
        self.cfg = clusters[cluster]
        if is_tbd(self.cfg.get("api_url")):
            raise not_configured(f"kubernetes.clusters.{cluster}.api_url")

    def replicasets(self, namespace: Optional[str], label_selector: Optional[str] = None) -> list[dict]:
        base = self.cfg["api_url"].rstrip("/")
        path = f"/apis/apps/v1/namespaces/{namespace}/replicasets" if namespace else "/apis/apps/v1/replicasets"
        params = {"limit": 500}
        if label_selector:
            params["labelSelector"] = label_selector
        body = self.ctx.http.get(base + path, params=params, headers=bearer(self.cfg.get("token")),
                                 verify=self.cfg.get("verify_tls", True))
        return (body or {}).get("items", [])
