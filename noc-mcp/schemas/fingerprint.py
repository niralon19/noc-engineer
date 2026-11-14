"""Stable incident fingerprint.

LLM NOTE: migrated from crew-network memory/fingerprint.py with one fix: the old version hashed the
model-written root_cause, so different wording created duplicate tickets and different 'unknown'
incidents merged. The fingerprint must come only from alert/ticket data. In this environment the
rule is the primary identity; server/topic/service is the secondary scope.
"""
import hashlib


def compute_fingerprint(kind: str, rule_id: str = "", scope: str = "", alert_rule: str = "") -> str:
    """kind: hermeticity | coupling | loss | load | app | config ...; scope: server/topic/service."""
    if not (rule_id or scope):
        raise ValueError("fingerprint needs rule_id or scope")
    raw = "|".join(x.strip().lower() for x in (kind, rule_id, scope, alert_rule))
    return hashlib.sha256(raw.encode()).hexdigest()
