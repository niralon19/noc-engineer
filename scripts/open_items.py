#!/usr/bin/env python3
"""List every fact still missing from Nir, with the question ID from docs/OPEN-QUESTIONS.md.

Run at the start of every session:  python3 scripts/open_items.py   [--json] [--brief]
Two sources: (1) signals in the repo (TBD/REPLACE placeholders, unverified pipeline, empty skill knowledge,
missing config files), (2) questions still marked ❓/⏳ in docs/OPEN-QUESTIONS.md.
The agent must ASK Nir for these (Hebrew, max 5 at a time) instead of guessing.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
Q_FILE = ROOT / "docs" / "OPEN-QUESTIONS.md"


def tbd(v) -> bool:
    return v is None or (isinstance(v, str) and (not v.strip() or "TBD" in v or "REPLACE" in v))


def load(p: Path) -> dict:
    return yaml.safe_load(p.read_text()) or {} if p.exists() else {}


def questionnaire() -> dict[str, dict]:
    out = {}
    for line in Q_FILE.read_text().splitlines():
        m = re.match(r"^\|\s*([A-J]\d+)\s*\|\s*(.+?)\s*\|.*\|\s*(❓|⏳|✅)[^|]*\|\s*$", line)
        if m:
            out[m.group(1)] = {"question": m.group(2), "state": m.group(3)}
    return out


def scan() -> dict[str, list[str]]:
    f: dict[str, list[str]] = defaultdict(list)

    def has(path: str, needle: str) -> bool:
        p = ROOT / path
        return p.exists() and needle in p.read_text()

    # B / C: deployment
    if has("deployment/k8s/hermes.yaml", "TBD-hermes-image") or has("deployment/k8s/hermes.yaml", "TBD-path"):
        f["B1"].append("deployment/k8s/hermes.yaml: Hermes image / HERMES_HOME path are TBD")
    cfg = load(ROOT / "hermes-profile" / "config.yaml")
    if tbd((cfg.get("model") or {}).get("base_url")):
        f["B2"].append("hermes-profile/config.yaml: model.base_url is a placeholder")
    if has("deployment/k8s/kustomization.yaml", "TBD-noc-engineer"):
        f["C1"].append("deployment/k8s/kustomization.yaml: namespace TBD")
    if has("deployment/k8s/noc-mcp.yaml", "TBD-registry"):
        f["C2"].append("deployment/k8s/noc-mcp.yaml: image TBD")
    if has("deployment/k8s/noc-mcp.yaml", "emptyDir"):
        f["C3"].append("deployment/k8s/noc-mcp.yaml: history/audit on emptyDir (lost on restart)")
    if has("deployment/argocd/application.yaml", "TBD"):
        f["C4"].append("deployment/argocd/application.yaml: project / cluster / namespace TBD")
        if has("deployment/argocd/application.yaml", "TBD-internal-git-url"):
            f["A1"].append("deployment/argocd/application.yaml: repoURL TBD (repo still on public GitHub?)")

    # E: pipeline
    pipe = load(ROOT / "noc-mcp" / "config" / "pipeline.yaml")
    if not pipe.get("verified"):
        f["E1"].append("noc-mcp/config/pipeline.yaml: verified=false (hops are the proposed default)")
    for h in pipe.get("hops", []):
        missing = [k for k in h if k.endswith("_query") and tbd(h[k])]
        if missing:
            f["E2"].append(f"pipeline.yaml hop {h['id']}: {', '.join(missing)} TBD")
        if tbd(h.get("per_rule")) if not isinstance(h.get("per_rule"), bool) else False:
            f["E5"].append(f"pipeline.yaml hop {h['id']}: per_rule TBD")
    kpis = pipe.get("kpis") or {}
    for k, q in (("hermeticity", "E3"), ("coupling", "E4")):
        if tbd((kpis.get(k) or {}).get("query")) or tbd((kpis.get(k) or {}).get("definition")):
            f[q].append(f"pipeline.yaml kpis.{k}: definition/query TBD")

    # F / G / H: backends (real file if present, else everything is open)
    real = ROOT / "noc-mcp" / "config" / "backends.yaml"
    b = load(real) if real.exists() else load(ROOT / "noc-mcp" / "config" / "backends.example.yaml")
    src = "backends.yaml" if real.exists() else "backends.yaml missing (only the example exists)"
    rules = b.get("rules") or {}
    if tbd(rules.get("get_rule_path")):
        f["F1"].append(f"{src}: rules.get_rule_path TBD")
    if tbd(rules.get("changes_path")) or tbd(rules.get("global_changes_path")):
        f["F2"].append(f"{src}: rules.changes_path / global_changes_path TBD")
    if tbd(rules.get("rule_path_path")) and not (ROOT / "noc-mcp" / "config" / "rule-paths.yaml").exists():
        f["F3"].append("no rule -> path source: rules.rule_path_path TBD and noc-mcp/config/rule-paths.yaml missing")
    if not real.exists():
        f["G1"].append("noc-mcp/config/backends.yaml missing: Prometheus/Thanos URLs and retention unknown")
    for key, q in (("server_queries", "G2"), ("kafka_queries", "G3")):
        open_ = [k for k, v in (b.get(key) or {}).items() if tbd(v)]
        if open_:
            f[q].append(f"{src}: {key}.{', '.join(open_)} TBD")
    if tbd((b.get("elasticsearch") or {}).get("default_index")):
        f["G4"].append(f"{src}: elasticsearch.default_index TBD")
    if tbd((b.get("maintenance") or {}).get("source")):
        f["G7"].append(f"{src}: maintenance.source TBD")
    if not real.exists():
        for q in ("G5", "G6", "H1"):
            f[q].append("backends.yaml missing")

    # I: skills knowledge
    skill_q = {"traffic-hermetic": "I1", "coupling": "I2", "enrichment-quality": "I2", "capture-servers": "I3",
               "kafka-pipeline": "I4", "platform-operations": "I5", "coatr": "I5", "jira-operations": "H2"}
    for p in sorted((ROOT / "hermes-profile" / "skills").glob("*/SKILL.md")):
        t = p.read_text()
        if "## Environment knowledge" in t and re.search(r"## Environment knowledge[\s\S]*?- TBD", t):
            f[skill_q.get(p.parent.name, "I5")].append(f"skill {p.parent.name}: Environment knowledge empty")
    if has("docs/runbooks.md", "do not invent runbooks"):
        f["I6"].append("docs/runbooks.md: no real runbooks yet")

    # J: evaluation set
    cases = list((ROOT / "evals" / "cases").glob("*")) if (ROOT / "evals" / "cases").exists() else []
    if len(cases) < 20:
        f["J1"].append(f"evals/cases: {len(cases)} cases (need 20-30)")
    return f


def main() -> int:
    qs, found = questionnaire(), scan()
    ids = sorted(set(found) | {k for k, v in qs.items() if v["state"] != "✅"},
                 key=lambda x: (x[0], int(x[1:])))
    items = [{"id": i, "question": qs.get(i, {}).get("question", "(missing from OPEN-QUESTIONS.md)"),
              "state": qs.get(i, {}).get("state", "❓"), "evidence": found.get(i, [])} for i in ids]
    if "--json" in sys.argv:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    elif "--brief" in sys.argv:
        print(f"{len(items)} open questions for Nir: {', '.join(ids)}")
    else:
        print(f"OPEN ITEMS FOR NIR: {len(items)}  (details: docs/OPEN-QUESTIONS.md)")
        print("Ask before working on anything that depends on them: Hebrew, max 5 per message, with ID + example.\n")
        for it in items:
            print(f"[{it['id']}] {it['state']} {it['question']}")
            for e in it["evidence"]:
                print(f"      - {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
