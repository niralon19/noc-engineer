# LLM NOTE: single result format for every investigation (alert, ticket, proactive).
# Mirrors the output contract in hermes-profile/skills/alert-investigation/SKILL.md; keep both in sync.
# Categorical status only; no numeric confidence.
"""Uniform investigation result."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class InvestigationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"                    # location has direct evidence, main alternatives ruled out
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"        # strongly supported, some alternatives not ruled out
    INCONCLUSIVE = "INCONCLUSIVE"              # no location fits; next_check required
    INVESTIGATION_INCOMPLETE = "INVESTIGATION_INCOMPLETE"  # a required tool/system failed


class Verdict(str, Enum):
    CONFIRMED = "confirmed"
    RULED_OUT = "ruled_out"
    UNKNOWN = "unknown"


@dataclass
class Location:
    layer: Optional[str] = None        # e.g. pipeline, link, provider, routing, app, db
    component: Optional[str] = None
    entity: Optional[str] = None       # host / link / customer / prefix
    provider: Optional[str] = None
    service: Optional[str] = None


@dataclass
class Evidence:
    ref: str
    tool: str
    query: str
    time_range: dict[str, str]
    observation: str


@dataclass
class Candidate:
    location: Location
    verdict: Verdict
    evidence_for: list[str] = field(default_factory=list)      # Evidence.ref
    evidence_against: list[str] = field(default_factory=list)


@dataclass
class Investigation:
    investigation_id: str
    source: str                         # grafana_alert | anomaly | jira | chat
    fingerprint: str                    # from alert data, NEVER from model text
    status: InvestigationStatus
    headline: str                       # "<symptom> caused by <location> since <onset>"
    suspected_location: Optional[Location] = None
    onset_time: Optional[str] = None
    impact: dict[str, Any] = field(default_factory=dict)
    candidates: list[Candidate] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    ruled_out: dict[str, str] = field(default_factory=dict)
    next_check: Optional[str] = None
    missing_data: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    jira_issue: Optional[str] = None
    created_at: str = ""
    schema_version: str = "2.0"

    def validate(self) -> list[str]:
        """Contract checks the agent output must pass before it is published."""
        errors = []
        refs = {e.ref for e in self.evidence}
        if self.status in (InvestigationStatus.CONFIRMED, InvestigationStatus.HIGH_CONFIDENCE):
            if not self.suspected_location:
                errors.append("suspected_location required")
            confirmed = [c for c in self.candidates if c.verdict == Verdict.CONFIRMED]
            if not confirmed or not any(r in refs for c in confirmed for r in c.evidence_for):
                errors.append("confirmed candidate must cite existing evidence")
        if self.status == InvestigationStatus.CONFIRMED and not self.ruled_out:
            errors.append("CONFIRMED requires ruled_out alternatives")
        if self.status != InvestigationStatus.CONFIRMED and not self.next_check:
            errors.append("next_check required unless CONFIRMED")
        if self.status == InvestigationStatus.INVESTIGATION_INCOMPLETE and not self.missing_data:
            errors.append("missing_data required when incomplete")
        return errors
