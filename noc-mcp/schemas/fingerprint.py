"""Stable incident fingerprint.

LLM NOTE: migrated from crew-network memory/fingerprint.py with one fix: the old version hashed the
model-written root_cause, so different wording created duplicate tickets and different 'unknown'
incidents merged. The fingerprint must come only from alert data.
"""
import hashlib


def compute_fingerprint(alert_type: str, service: str, entity: str = "", rule: str = "") -> str:
    raw = "|".join(x.strip().lower() for x in (alert_type, service, entity, rule))
    return hashlib.sha256(raw.encode()).hexdigest()
