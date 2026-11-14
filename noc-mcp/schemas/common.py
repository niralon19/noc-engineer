"""Shared pieces for every noc-mcp tool: result envelope, time windows, errors.

Every tool returns ToolResult.as_dict(): ok, data, error{code,message,retryable}, source, queried_at,
time_range{start,end}, truncated, notes. Tools never raise to the caller (see tools/_base.py).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

MAX_RESULT_CHARS = 20_000      # keep tool output small enough for the model context


class ToolError(Exception):
    """Expected failure with a stable code the agent can reason about."""

    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.code, self.message, self.retryable = code, message, retryable


# config key prefix -> question ID in docs/OPEN-QUESTIONS.md (so the agent can ask for exactly the right thing)
QUESTION_FOR = {
    "prometheus": "G1", "thanos": "G1", "elasticsearch": "G4", "argocd": "G5", "kubernetes": "G6",
    "maintenance": "G7", "rules.get_rule_path": "F1", "rules.changes_path": "F2", "rules.global_changes_path": "F2",
    "rules.rule_path_path": "F3", "rules": "F1", "jira": "H1", "server_queries": "G2", "kafka_queries": "G3",
    "pipeline": "E2", "kpis": "E3",
}


def question_for(key: str) -> str:
    best = max((k for k in QUESTION_FOR if key.startswith(k)), key=len, default=None)
    return QUESTION_FOR[best] if best else "?"


def not_configured(what: str) -> ToolError:
    q = question_for(what)
    return ToolError("not_configured", f"{what} is not configured yet (open question {q}). Do not guess: tell the user "
                                       f"exactly what is missing and ask the NOC team owner to provide it.")


@dataclass
class TimeRange:
    start: datetime
    end: datetime

    @property
    def seconds(self) -> int:
        return max(1, int((self.end - self.start).total_seconds()))

    @property
    def prom_range(self) -> str:
        """Window as a PromQL duration, e.g. '1800s'."""
        return f"{self.seconds}s"

    def as_dict(self) -> dict:
        return {"start": iso(self.start), "end": iso(self.end)}


_REL = re.compile(r"^(?:now)?\s*-\s*(\d+)\s*([smhdw])$")
_UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(value: Optional[str], default: datetime, ref: Optional[datetime] = None) -> datetime:
    """Accepts ISO-8601, 'now', '-2h', 'now-30m', or epoch seconds. Relative times count back from ref (now)."""
    if value in (None, ""):
        return default
    ref = ref or now()
    v = str(value).strip()
    if v == "now":
        return ref
    m = _REL.match(v)
    if m:
        return ref - timedelta(**{_UNITS[m.group(2)]: int(m.group(1))})
    if v.isdigit():
        return datetime.fromtimestamp(int(v), tz=timezone.utc)
    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError as e:
        raise ToolError("bad_argument", f"cannot parse time '{value}' (use ISO-8601, 'now' or '-2h')") from e
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def parse_duration(value: str) -> timedelta:
    m = re.match(r"^(\d+)\s*([smhdw])$", str(value).strip())
    if not m:
        raise ToolError("bad_argument", f"bad duration '{value}' (use e.g. 30m, 1d, 7d)")
    return timedelta(**{_UNITS[m.group(2)]: int(m.group(1))})


def window(start: Optional[str], end: Optional[str], default_minutes: int = 60, max_days: int = 31) -> TimeRange:
    ref = now()
    e = parse_time(end, ref, ref)
    s = parse_time(start, e - timedelta(minutes=default_minutes), ref)
    if s >= e:
        raise ToolError("bad_argument", "start must be before end")
    if e - s > timedelta(days=max_days):
        raise ToolError("bad_argument", f"window longer than {max_days} days; narrow it")
    return TimeRange(s, e)


@dataclass
class ToolResult:
    ok: bool
    source: str
    data: Any = None
    error: Optional[dict] = None
    time_range: Optional[dict] = None
    truncated: bool = False
    notes: list = field(default_factory=list)
    queried_at: str = field(default_factory=lambda: iso(now()))

    def as_dict(self) -> dict:
        d = asdict(self)
        text = json.dumps(d, default=str)
        if len(text) > MAX_RESULT_CHARS:
            d["data"] = {"_truncated_preview": json.dumps(d["data"], default=str)[: MAX_RESULT_CHARS // 2]}
            d["truncated"] = True
            d["notes"] = d["notes"] + ["result too large: narrow the window/scope or aggregate"]
        return d


def ok(source: str, data: Any, tr: Optional[TimeRange] = None, truncated: bool = False, notes: Optional[list] = None) -> dict:
    return ToolResult(True, source, data, None, tr.as_dict() if tr else None, truncated, notes or []).as_dict()


def fail(source: str, err: ToolError, tr: Optional[TimeRange] = None) -> dict:
    return ToolResult(False, source, None, {"code": err.code, "message": err.message, "retryable": err.retryable},
                      tr.as_dict() if tr else None).as_dict()


def is_tbd(value: Any) -> bool:
    return value is None or (isinstance(value, str) and (not value.strip() or "TBD" in value or "REPLACE" in value))
