"""noc-mcp self check (no network): which backends and pipeline measures are configured."""
from __future__ import annotations

from context import get_context
from schemas.common import is_tbd, ok, question_for
from security.policy import writes_allowed
from tools._base import REGISTRY, WRITE_TOOLS, tool

CHECKS = {
    "prometheus": ("prometheus", "url"), "thanos": ("thanos", "url"), "eck": ("elasticsearch", "url"),
    "argocd": ("argocd", "url"), "rules": ("rules", "base_url"), "jira": ("jira", "url"),
    "maintenance": ("maintenance", "source"),
}


@tool("health")
def noc_mcp_health() -> dict:
    """Configuration status of noc-mcp: which backends are configured, how many pipeline hops are instrumented,
    whether writes are enabled, and the registered tools. Use when tools return not_configured."""
    ctx = get_context()
    backends = {name: not is_tbd(ctx.section(sec).get(key)) for name, (sec, key) in CHECKS.items()}
    clusters = {c: not is_tbd(v.get("api_url")) for c, v in (ctx.section("kubernetes").get("clusters") or {}).items()}
    hops = ctx.pipeline.get("hops", [])
    instrumented = sum(any(not is_tbd(h.get(f"{m}_query")) for m in ("in", "out", "drop", "lag", "matched")) for h in hops)
    ask = sorted({f"{question_for(CHECKS[n][0])}: {n} not configured" for n, v in backends.items() if not v})
    ask += [f"G6: kubernetes cluster {c} not configured" for c, v in clusters.items() if not v]
    if instrumented < len(hops):
        ask.append(f"E2: {len(hops) - instrumented} pipeline hops have no queries")
    if not ctx.pipeline.get("verified"):
        ask.append("E1: pipeline map not verified")
    return ok("health", {"ask_team": ask, "backends": backends, "kubernetes": clusters, "pipeline_verified": bool(ctx.pipeline.get("verified")),
                         "hops_instrumented": f"{instrumented}/{len(hops)}", "writes_enabled": writes_allowed(ctx),
                         "tools": sorted(REGISTRY), "write_tools": sorted(WRITE_TOOLS)})
