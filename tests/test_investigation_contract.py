import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "noc-mcp"))
from schemas.investigation import (Candidate, Evidence, Investigation, InvestigationStatus as S,  # noqa: E402
                                   Location, Verdict)
from schemas.fingerprint import compute_fingerprint  # noqa: E402

EV = Evidence("e1", "query_metrics", "rate(x[5m])", {"start": "a", "end": "b"}, "drop on link A only")


def inv(status, **kw):
    return Investigation("i1", "grafana_alert", "fp", status, "h", **kw)


def test_confirmed_valid():
    i = inv(S.CONFIRMED, suspected_location=Location(layer="link", entity="A"), evidence=[EV],
            candidates=[Candidate(Location(entity="A"), Verdict.CONFIRMED, ["e1"])],
            ruled_out={"provider": "other links of the provider are normal"})
    assert i.validate() == []


def test_confirmed_without_ruled_out_or_evidence_fails():
    errs = inv(S.CONFIRMED, suspected_location=Location(entity="A"),
               candidates=[Candidate(Location(entity="A"), Verdict.CONFIRMED, ["missing"])]).validate()
    assert "CONFIRMED requires ruled_out alternatives" in errs
    assert "confirmed candidate must cite existing evidence" in errs


def test_inconclusive_requires_next_check():
    assert "next_check required unless CONFIRMED" in inv(S.INCONCLUSIVE).validate()
    assert inv(S.INCONCLUSIVE, next_check="compare path B").validate() == []


def test_incomplete_requires_missing_data():
    assert "missing_data required when incomplete" in inv(S.INVESTIGATION_INCOMPLETE, next_check="x").validate()


def test_fingerprint_ignores_model_text_and_case():
    assert compute_fingerprint("coatr", "API", "db1") == compute_fingerprint("COATR", "api ", "db1")
    assert compute_fingerprint("coatr", "api", "db1") != compute_fingerprint("coatr", "api", "db2")
