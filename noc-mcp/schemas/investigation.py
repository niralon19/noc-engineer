"""Uniform investigation result."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class InvestigationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"                              # root cause verified by evidence
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"                  # strong, not fully verified
    INVESTIGATION_INCOMPLETE = "INVESTIGATION_INCOMPLETE"
    INCONCLUSIVE = "INCONCLUSIVE"                        # not enough evidence


@dataclass
class Investigation:
    investigation_id: str
    source: str                      # grafana_alert | jira | proactive
    target: dict[str, Any]
    status: InvestigationStatus
    summary: str
    root_cause: Optional[dict[str, Any]] = None
    findings: list = field(default_factory=list)
    hypotheses: list = field(default_factory=list)
    evidence_refs: list = field(default_factory=list)
    metrics_evidence: list = field(default_factory=list)
    log_evidence: list = field(default_factory=list)
    timeline: list = field(default_factory=list)
    recommended_actions: list = field(default_factory=list)
    missing_data: list = field(default_factory=list)
    tool_execution_status: list = field(default_factory=list)
    data_freshness: dict[str, Any] = field(default_factory=dict)
    jira_issue: Optional[str] = None
    created_at: str = ""
    schema_version: str = "1.0"
