"""Investigation output contract. `noc.py jira-comment` refuses to post anything that fails validate().

Status is categorical (no numeric confidence):
  CONFIRMED                 direct evidence for the location AND alternatives ruled out
  HIGH_CONFIDENCE           evidence points to the location, some alternatives not ruled out
  INCONCLUSIVE              no location fits; next_check required
  INVESTIGATION_INCOMPLETE  a system/tool could not be checked; missing_data required
"""
from __future__ import annotations

from typing import Optional

STATUSES = ("CONFIRMED", "HIGH_CONFIDENCE", "INCONCLUSIVE", "INVESTIGATION_INCOMPLETE")
VERDICTS = ("confirmed", "supported", "ruled_out", "unknown")


def validate(inv: dict, known_hops: Optional[set] = None) -> list[str]:
    errors: list[str] = []
    status = inv.get("status")
    if status not in STATUSES:
        return [f"status must be one of {STATUSES}"]
    for f in ("investigation_id", "fingerprint", "headline"):
        if not inv.get(f):
            errors.append(f"{f} required")
    loc = inv.get("suspected_location") or {}
    refs = {e.get("ref") for e in inv.get("evidence") or [] if isinstance(e, dict)}
    for e in inv.get("evidence") or []:
        if not all(e.get(k) for k in ("ref", "tool", "query", "observation")):
            errors.append("every evidence item needs ref, tool, query, observation")
            break
    cands = inv.get("candidates") or []
    for c in cands:
        if c.get("verdict") not in VERDICTS:
            errors.append(f"candidate verdict must be one of {VERDICTS}")
            break
    if status in ("CONFIRMED", "HIGH_CONFIDENCE"):
        if not loc.get("hop"):
            errors.append("suspected_location.hop required")
        needed = {"confirmed"} if status == "CONFIRMED" else {"confirmed", "supported"}
        backing = [c for c in cands if c.get("verdict") in needed]
        if not any(r in refs for c in backing for r in c.get("evidence_for") or []):
            errors.append("the leading candidate must cite existing evidence refs")
    if status == "CONFIRMED" and not inv.get("ruled_out"):
        errors.append("CONFIRMED requires ruled_out alternatives")
    if status != "CONFIRMED" and not inv.get("next_check"):
        errors.append("next_check required unless CONFIRMED")
    if status == "INVESTIGATION_INCOMPLETE" and not inv.get("missing_data"):
        errors.append("missing_data required when INVESTIGATION_INCOMPLETE")
    if known_hops:
        for h in [loc.get("hop")] + [(c.get("location") or {}).get("hop") for c in cands]:
            if h and h not in known_hops:
                errors.append(f"unknown hop: {h}")
    return errors


def render(inv: dict, marker: str) -> str:
    loc = inv.get("suspected_location") or {}
    lines = [f"*[AI investigation - review required]* {inv['headline']}", f"Status: {inv['status']}"]
    if loc:
        lines.append("Suspected location: " + ", ".join(f"{k}={v}" for k, v in loc.items() if v))
    if inv.get("onset_time"):
        lines.append(f"Onset: {inv['onset_time']}")
    for e in (inv.get("evidence") or [])[:8]:
        lines.append(f"- [{e['ref']}] {e['tool']}: {e['observation']}")
    for k, v in list((inv.get("ruled_out") or {}).items())[:8]:
        lines.append(f"- ruled out {k}: {v}")
    if inv.get("next_check"):
        lines.append(f"Next check: {inv['next_check']}")
    if inv.get("missing_data"):
        lines.append("Could not check: " + ", ".join(inv["missing_data"]))
    if inv.get("recommended_actions"):
        lines.append("Recommendations (not executed): " + "; ".join(inv["recommended_actions"][:5]))
    lines.append(marker)
    return "\n".join(lines)
