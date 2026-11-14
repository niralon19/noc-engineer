from datetime import datetime, timezone
import pytest
from anomaly_engine import Rule, Sample, evaluate

def test_rule_emits_stable_event_id():
    sample = Sample("latency", "api-a", 3.0, datetime(2026, 1, 1, tzinfo=timezone.utc))
    rule = Rule("latency-high", "latency", "gt", 2.0)
    first = evaluate(sample, rule)
    assert first is not None and first.event_id == evaluate(sample, rule).event_id

def test_non_matching_metric_is_ignored():
    assert evaluate(Sample("cpu", "host-a", 90, datetime.now(timezone.utc)), Rule("r", "latency", "gt", 2)) is None

def test_unknown_operator_rejected():
    with pytest.raises(ValueError):
        evaluate(Sample("latency", "api-a", 3, datetime.now(timezone.utc)), Rule("r", "latency", "approx", 2))
