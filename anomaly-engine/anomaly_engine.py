# LLM NOTE: deterministic core; no LLM or network calls. Imported by tests via tests/conftest.py
# (the directory name has a hyphen). Extend with rules.py/statistical.py, keep evaluate() pure.
"""Deterministic anomaly evaluation; no LLM invocation in the metric hot path."""
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal

Operator = Literal["gt", "gte", "lt", "lte"]

@dataclass(frozen=True)
class Rule:
    rule_id: str
    metric: str
    operator: Operator
    threshold: float
    severity: str = "warning"

@dataclass(frozen=True)
class Sample:
    metric: str
    entity: str
    value: float
    observed_at: datetime

@dataclass(frozen=True)
class Event:
    event_id: str
    rule_id: str
    metric: str
    entity: str
    value: float
    threshold: float
    severity: str
    observed_at: datetime

def evaluate(sample: Sample, rule: Rule) -> Event | None:
    if sample.metric != rule.metric:
        return None
    checks = {"gt": sample.value > rule.threshold, "gte": sample.value >= rule.threshold,
              "lt": sample.value < rule.threshold, "lte": sample.value <= rule.threshold}
    if rule.operator not in checks:
        raise ValueError(f"Unsupported operator: {rule.operator}")
    if not checks[rule.operator]:
        return None
    stamp = sample.observed_at.astimezone(timezone.utc).isoformat()
    key = f"{rule.rule_id}|{sample.metric}|{sample.entity}|{stamp}"
    return Event(sha256(key.encode()).hexdigest(), rule.rule_id, sample.metric,
                 sample.entity, sample.value, rule.threshold, rule.severity, sample.observed_at)
