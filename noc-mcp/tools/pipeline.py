"""Data-path tools used by the pipeline-walk skill: get_pipeline_map, get_hop_counts."""
from __future__ import annotations

import re
from typing import Optional

from clients.prometheus import Prometheus, render, series_key
from context import get_context
from schemas.common import ToolError, is_tbd, ok, parse_duration, window
from tools._base import as_list, tool

MEASURES = ("in", "out", "drop", "lag", "matched")


def _hop(pipeline: dict, hop_id: str) -> dict:
    for h in pipeline.get("hops", []):
        if h["id"] == hop_id:
            return h
    raise ToolError("bad_argument", f"unknown hop '{hop_id}'. Known: {[h['id'] for h in pipeline.get('hops', [])]}")


@tool("pipeline")
def get_pipeline_map() -> dict:
    """List the data-path hops in order (traffic -> servers -> Kafka -> processing -> enrichment -> rule matching -> storage -> output),
    which measures each hop exposes, whether it is per-rule, and the hermeticity/coupling KPI definitions.
    Call this first in pipeline-walk to know which hops exist."""
    p = get_context().pipeline
    hops = [{"id": h["id"], "description": h.get("description"), "per_rule": h.get("per_rule"),
             "instrumented": [m for m in MEASURES if not is_tbd(h.get(f"{m}_query"))]} for h in p.get("hops", [])]
    kpis = {k: {"definition": v.get("definition"), "measured_at": v.get("measured_at"), "instrumented": not is_tbd(v.get("query"))}
            for k, v in (p.get("kpis") or {}).items()}
    notes = [] if p.get("verified") else ["pipeline map is NOT verified yet (proposed default); treat hop names as provisional"]
    return ok("pipeline", {"verified": bool(p.get("verified")), "hops": hops, "kpis": kpis}, notes=notes)


@tool("prometheus")
def get_hop_counts(hop: str, rule_id: Optional[str] = None, instances: Optional[list[str]] = None,
                   start: Optional[str] = None, end: Optional[str] = None, compare: str = "1d,7d") -> dict:
    """Counts at ONE hop of the data path for a window: IN / OUT / DROP / LAG / MATCHED, per instance, with the same
    window yesterday and last week. Use for bisection: IN normal + OUT low = problem in this hop; IN already low = upstream.
    hop: hop id from get_pipeline_map. rule_id: for per-rule hops. instances: servers/pods/partitions to scope (from get_rule_path).
    start/end: ISO or relative ('-30m', 'now'); default last 60 minutes. compare: baseline offsets, e.g. '1d,7d'."""
    ctx = get_context()
    h = _hop(ctx.pipeline, hop)
    tr = window(start, end)
    prom = Prometheus(ctx)
    inst = as_list(instances)
    values = {"rule_id": rule_id or "", "instances": "|".join(re.escape(i) for i in inst) or ".*", "range": tr.prom_range}
    offsets = [(o, parse_duration(o)) for o in as_list(compare)][:3]

    measures, missing, used = {}, [], set()
    for m in MEASURES:
        tmpl = h.get(f"{m}_query")
        if is_tbd(tmpl):
            if f"{m}_query" in h:
                missing.append(m)
            continue
        if "{rule_id}" in tmpl and not rule_id:
            raise ToolError("bad_argument", f"hop '{hop}' is measured per rule: pass rule_id")
        q = render(tmpl, **values)
        cur, src = prom.instant(q, tr.end)
        used.add(src)
        entry = {"query": q, "total": _total(cur), "by_instance": {series_key(s["labels"]): s["value"] for s in cur[:50]},
                 "baselines": {}}
        for name, delta in offsets:
            base, src = prom.instant(q, tr.end - delta)
            used.add(src)
            entry["baselines"][name] = _total(base)
        measures[m] = entry

    if not measures:
        raise ToolError("hop_not_instrumented", f"hop '{hop}' has no configured queries (TBD in pipeline.yaml): "
                                                "report it as missing_data, not as healthy")
    data = {"hop": hop, "scope": {"rule_id": rule_id, "instances": inst or "all"}, "measures": measures,
            "derived": _derive(measures, [o for o, _ in offsets])}
    notes = [f"not instrumented at this hop: {', '.join(missing)}"] if missing else []
    return ok("+".join(sorted(used)) or "prometheus", data, tr, notes=notes)


def _total(series: list[dict]) -> Optional[float]:
    vals = [s["value"] for s in series if s["value"] is not None]
    return round(sum(vals), 6) if vals else None


def _pct(cur: Optional[float], base: Optional[float]) -> Optional[float]:
    if cur is None or not base:
        return None
    return round((cur - base) / base * 100, 1)


def _derive(measures: dict, offsets: list[str]) -> dict:
    """Deterministic comparisons; the agent interprets them."""
    out: dict = {"change_vs_baseline_pct": {}, "hints": []}
    for m, e in measures.items():
        out["change_vs_baseline_pct"][m] = {o: _pct(e["total"], e["baselines"].get(o)) for o in offsets}

    def ratio(num: str, den: str, at: Optional[str] = None) -> Optional[float]:
        if num not in measures or den not in measures:
            return None
        n = measures[num]["total"] if at is None else measures[num]["baselines"].get(at)
        d = measures[den]["total"] if at is None else measures[den]["baselines"].get(at)
        return None if n is None or not d else round(n / d, 4)

    for name, num, den in (("out_in_ratio", "out", "in"), ("match_ratio", "matched", "in")):
        cur = ratio(num, den)
        if cur is None:
            continue
        base = {o: ratio(num, den, o) for o in offsets}
        out[name] = {"current": cur, "baselines": base}
        worst = [b for b in base.values() if b is not None]
        if worst and cur < min(worst) - 0.05:
            out["hints"].append(f"{name} {cur} is below every baseline {base}: data diverges at this hop")
    chg = out["change_vs_baseline_pct"]
    if "in" in chg and all((v or 0) <= -20 for v in chg["in"].values() if v is not None) and any(chg["in"].values()):
        out["hints"].append("IN is already >=20% below baseline: the problem is likely upstream of this hop")
    if "drop" in measures and (measures["drop"]["total"] or 0) > 0:
        out["hints"].append("non-zero drops counted at this hop in the window")
    return out
