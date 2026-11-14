"""Rule & configuration management tools (read-only)."""
from __future__ import annotations

from typing import Optional

from clients.prometheus import Prometheus, render
from clients.rules import Rules
from context import get_context
from schemas.common import ToolError, iso, is_tbd, not_configured, ok, parse_duration, window
from tools._base import as_list, tool


@tool("rules")
def get_rule(rule_id: str) -> dict:
    """Current definition of a rule from the rule & configuration management system (scope, status, owner, version)."""
    return ok("rules", {"rule_id": rule_id, "rule": Rules(get_context()).rule(rule_id)})


@tool("rules")
def get_rule_path(rule_id: str) -> dict:
    """Which servers, Kafka topics/consumer groups, services (cluster/namespace/name), enrichment sources and Argo apps
    serve this rule. Use it to scope get_hop_counts, get_server_drops, get_consumer_lag and change queries."""
    path = Rules(get_context()).path(rule_id)
    if path is None:
        raise ToolError("not_found", f"no data-path mapping for rule '{rule_id}' (add it to rule-paths.yaml or the rules API)")
    return ok("rules", {"rule_id": rule_id, "path": path})


@tool("rules")
def get_rule_changes(rule_id: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> dict:
    """Changes in the rule & configuration system in a window: the rule itself and global configuration.
    Default window: last 24h. Use first in every investigation (change-correlation)."""
    ctx = get_context()
    tr = window(start, end, default_minutes=24 * 60)
    rules = Rules(ctx)
    data, notes = {}, []
    if rule_id:
        data["rule_changes"] = rules.changes(rule_id, iso(tr.start), iso(tr.end))
    try:
        data["global_changes"] = rules.changes(None, iso(tr.start), iso(tr.end))
    except ToolError as e:
        if e.code != "not_configured":
            raise
        notes.append("global configuration changes are not configured; only rule changes were checked")
    if not data:
        raise ToolError("bad_argument", "pass rule_id, or configure rules.global_changes_path")
    return ok("rules", data, tr, notes=notes)


@tool("prometheus")
def get_rule_kpis(rule_id: str, kpis: str = "hermeticity,coupling", start: Optional[str] = None,
                  end: Optional[str] = None, compare: str = "1d,7d") -> dict:
    """Hermeticity and/or coupling of a rule over the window (downsampled series) plus the same value yesterday and last week.
    Definitions come from the pipeline map. Use to confirm the symptom and find the real onset."""
    ctx = get_context()
    tr = window(start, end, default_minutes=6 * 60)
    defs = ctx.pipeline.get("kpis") or {}
    prom = Prometheus(ctx)
    out, notes, src = {}, [], "prometheus"
    step_range = "300s"
    for k in as_list(kpis):
        if k not in defs:
            raise ToolError("bad_argument", f"unknown KPI '{k}'; known: {sorted(defs)}")
        if is_tbd(defs[k].get("query")):
            notes.append(f"{k}: query TBD in pipeline.yaml")
            continue
        series, src = prom.range(render(defs[k]["query"], rule_id=rule_id, range=step_range), tr.start, tr.end)
        current_q = render(defs[k]["query"], rule_id=rule_id, range=tr.prom_range)
        cur, _ = prom.instant(current_q, tr.end)
        base = {}
        for o in as_list(compare)[:3]:
            b, _ = prom.instant(current_q, tr.end - parse_duration(o))
            base[o] = b[0]["value"] if b else None
        out[k] = {"definition": defs[k].get("definition"), "window_value": cur[0]["value"] if cur else None,
                  "baselines": base, "series": series[:3]}
    if not out:
        raise not_configured("kpis (" + "; ".join(notes) + ")")
    return ok(src, {"rule_id": rule_id, "kpis": out}, tr, notes=notes)
