import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "noc-mcp"))
from schemas.investigation import (Candidate, Evidence, Investigation, InvestigationStatus as S,  # noqa: E402
                                   Location, Verdict)
from schemas.fingerprint import compute_fingerprint  # noqa: E402
from schemas.pipeline import hop_ids  # noqa: E402

import pytest  # noqa: E402

EV = Evidence("e1", "get_hop_counts", "kafka_ingest rule=R1", {"start": "a", "end": "b"}, "OUT 40% below IN on partition 3")
LOC = Location(hop="kafka_ingest", rule_id="R1", component="topic-x", instances=["p3"])


def inv(status, **kw):
    return Investigation("i1", "grafana_alert", "fp", status, "h", **kw)


def test_confirmed_valid_and_hop_known():
    i = inv(S.CONFIRMED, suspected_location=LOC, evidence=[EV],
            candidates=[Candidate(LOC, Verdict.CONFIRMED, ["e1"])],
            ruled_out={"server_nic": "no NIC drops on all servers"})
    assert i.validate(known_hops=set(hop_ids())) == []


def test_unknown_hop_rejected():
    bad = Location(hop="somewhere")
    i = inv(S.HIGH_CONFIDENCE, suspected_location=bad, evidence=[EV], next_check="x",
            candidates=[Candidate(bad, Verdict.SUPPORTED, ["e1"])])
    assert "unknown hop: somewhere" in i.validate(known_hops=set(hop_ids()))


def test_location_requires_hop():
    i = inv(S.HIGH_CONFIDENCE, suspected_location=Location(rule_id="R1"), evidence=[EV], next_check="x",
            candidates=[Candidate(LOC, Verdict.SUPPORTED, ["e1"])])
    assert "suspected_location.hop required" in i.validate()


def test_high_confidence_accepts_supported_candidate():
    i = inv(S.HIGH_CONFIDENCE, suspected_location=LOC, evidence=[EV], next_check="check consumer group",
            candidates=[Candidate(LOC, Verdict.SUPPORTED, ["e1"])])
    assert i.validate() == []


def test_confirmed_rejects_only_supported_and_missing_evidence():
    errs = inv(S.CONFIRMED, suspected_location=LOC,
               candidates=[Candidate(LOC, Verdict.SUPPORTED, ["missing"])]).validate()
    assert "CONFIRMED requires ruled_out alternatives" in errs
    assert "leading candidate must cite existing evidence" in errs


def test_inconclusive_requires_next_check():
    assert "next_check required unless CONFIRMED" in inv(S.INCONCLUSIVE).validate()
    assert inv(S.INCONCLUSIVE, next_check="compare path B").validate() == []


def test_incomplete_requires_missing_data():
    assert "missing_data required when incomplete" in inv(S.INVESTIGATION_INCOMPLETE, next_check="x").validate()


def test_fingerprint_rule_based_and_stable():
    assert compute_fingerprint("hermeticity", "R1", "srv-a") == compute_fingerprint("Hermeticity", "r1 ", "SRV-A")
    assert compute_fingerprint("hermeticity", "R1") != compute_fingerprint("coupling", "R1")
    with pytest.raises(ValueError):
        compute_fingerprint("hermeticity")


def test_pipeline_has_kpi_hops():
    ids = hop_ids()
    assert len(ids) == len(set(ids))
    for needed in ("rule_matching", "internal_enrichment", "kafka_ingest", "server_nic"):
        assert needed in ids
