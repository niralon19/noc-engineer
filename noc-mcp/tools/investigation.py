"""Investigation history (read-only for the agent)."""
from __future__ import annotations

from typing import Optional

from context import get_context
from history import History
from schemas.common import ok
from tools._base import tool


@tool("history")
def search_investigations(rule_id: Optional[str] = None, fingerprint: Optional[str] = None, hop: Optional[str] = None,
                          text: Optional[str] = None, since_days: int = 30, limit: int = 10) -> dict:
    """Past investigations (newest first) matching rule, fingerprint, hop or free text. A similar past incident is a
    hint to TEST, never proof."""
    found = History(get_context()).search(rule_id, fingerprint, hop, text, min(int(since_days), 365), min(int(limit), 20))
    return ok("history", {"count": len(found), "investigations": found})
