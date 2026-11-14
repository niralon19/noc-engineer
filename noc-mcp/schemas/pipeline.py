"""Load the pipeline map (config/pipeline.yaml).

LLM NOTE: used by tools/pipeline.py (get_hop_counts, get_rule_path), the anomaly engine and
Investigation.validate(known_hops=...). The YAML is filled by Nir at work; keep `verified: false`
until every TBD is replaced.
"""
from pathlib import Path

import yaml

DEFAULT = Path(__file__).resolve().parents[1] / "config" / "pipeline.yaml"


def load_pipeline(path: Path = DEFAULT) -> dict:
    data = yaml.safe_load(path.read_text())
    ids = [h["id"] for h in data["hops"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate hop ids")
    return data


def hop_ids(path: Path = DEFAULT) -> list[str]:
    return [h["id"] for h in load_pipeline(path)["hops"]]
