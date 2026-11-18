"""Shared library for the noc-tools CLI and the cron scripts. Stdlib + PyYAML only (both ship with Hermes).

Config: $HERMES_HOME/noc.yaml (or NOC_CONFIG). ${VAR} / ${VAR:-default} are read from the environment, so secrets
stay in .env / the k8s Secret. A value that is empty, TBD or REPLACE means "not configured": callers get a
`not_configured` error and must ask the team, never guess.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

HERE = Path(__file__).resolve().parent
# skills/noc-tools/scripts/noclib.py -> HERMES_HOME is three levels up
HERMES_HOME = Path(os.environ.get("HERMES_HOME") or HERE.parents[2])
MAX_BODY = 5_000_000
_ENV = re.compile(r"\$\{([A-Z0-9_]+)(?::-([^}]*))?\}")


class NocError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


# ---------- config ----------

def _subst(obj: Any) -> Any:
    if isinstance(obj, str):
        return _ENV.sub(lambda m: os.environ.get(m.group(1), m.group(2) or ""), obj)
    if isinstance(obj, list):
        return [_subst(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _subst(v) for k, v in obj.items()}
    return obj


_CFG: Optional[dict] = None


def config() -> dict:
    global _CFG
    if _CFG is None:
        path = Path(os.environ.get("NOC_CONFIG") or HERMES_HOME / "noc.yaml")
        _CFG = _subst(yaml.safe_load(path.read_text()) or {}) if path.exists() else {}
    return _CFG


def set_config(cfg: Optional[dict]) -> None:
    """Tests only."""
    global _CFG
    _CFG = cfg


def section(name: str) -> dict:
    return config().get(name) or {}


def is_tbd(v: Any) -> bool:
    return v is None or (isinstance(v, str) and (not v.strip() or "TBD" in v or "REPLACE" in v))


def need(sec: str, key: str) -> Any:
    v = section(sec).get(key)
    if is_tbd(v):
        raise NocError("not_configured", f"{sec}.{key} is not configured in noc.yaml. Do not guess: say what is "
                                         f"missing and ask the NOC team owner (see OPEN-QUESTIONS.md).")
    return v


def data_dir() -> Path:
    d = HERMES_HOME / "data" / "noc"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- time ----------

_REL = re.compile(r"^(?:now)?\s*-\s*(\d+)\s*([smhdw])$")
_UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_time(v: Optional[str], default: datetime, ref: Optional[datetime] = None) -> datetime:
    """ISO-8601, 'now', '-2h', 'now-30m' or epoch seconds."""
    if v in (None, ""):
        return default
    ref = ref or now()
    v = str(v).strip()
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
        raise NocError("bad_argument", f"cannot parse time '{v}' (use ISO-8601, 'now' or '-2h')") from e
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def window(start: Optional[str], end: Optional[str], default_minutes: int = 60, max_days: int = 31):
    ref = now()
    e = parse_time(end, ref, ref)
    s = parse_time(start, e - timedelta(minutes=default_minutes), ref)
    if s >= e:
        raise NocError("bad_argument", "start must be before end")
    if e - s > timedelta(days=max_days):
        raise NocError("bad_argument", f"window longer than {max_days} days; narrow it")
    return s, e


# ---------- http ----------

class Http:
    """Tiny urllib client: timeouts, bounded body, typed errors, never logs secrets. Tests replace `HTTP`."""

    def request(self, method: str, url: str, params: Optional[dict] = None, body: Any = None,
                headers: Optional[dict] = None) -> Any:
        http = section("http")
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Accept": "application/json", **({"Content-Type": "application/json"} if data else {}),
                                              **(headers or {})})
        verify = http.get("verify_tls", True)
        ctx = ssl.create_default_context(cafile=verify) if isinstance(verify, str) and verify not in ("true", "True") \
            else ssl.create_default_context()
        if verify in (False, "false", "False"):
            ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
        host = url.split("/")[2] if "://" in url else url
        try:
            with urllib.request.urlopen(req, timeout=float(http.get("timeout_seconds", 20)), context=ctx) as r:
                raw = r.read(MAX_BODY + 1)
        except urllib.error.HTTPError as e:
            code = {401: "backend_auth", 403: "backend_auth", 404: "not_found"}.get(e.code, "backend_error")
            raise NocError(code, f"{host} returned {e.code}: {e.read(300).decode(errors='replace')}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise NocError("backend_unreachable", f"cannot reach {host}: {type(e).__name__}") from e
        if len(raw) > MAX_BODY:
            raise NocError("result_too_large", f"{host} returned more than {MAX_BODY} bytes; narrow the query")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except ValueError:
            return raw.decode(errors="replace")


HTTP = Http()


def bearer(token: Optional[str]) -> dict:
    return {"Authorization": f"Bearer {token}"} if token and not is_tbd(token) else {}


def basic(user: str, password: str) -> dict:
    return {"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()}


# ---------- backends (read-only, except the gated Jira comment) ----------

def _num(v: Any) -> Optional[float]:
    try:
        f = float(v)
        return None if f != f else f
    except (TypeError, ValueError):
        return None


def prom_instant(query: str, at: Optional[datetime] = None) -> list[dict]:
    url = need("prometheus", "url").rstrip("/")
    body = HTTP.request("GET", f"{url}/api/v1/query", {"query": query, "time": (at or now()).timestamp()},
                        headers=bearer(section("prometheus").get("token")))
    if not isinstance(body, dict) or body.get("status") != "success":
        raise NocError("bad_query", f"prometheus rejected the query: {body.get('error') if isinstance(body, dict) else body}")
    return [{"labels": r.get("metric", {}), "value": _num(r["value"][1])} for r in body["data"]["result"]]


def prom_range(query: str, start: datetime, end: datetime, step: Optional[int] = None) -> list[dict]:
    url = need("prometheus", "url").rstrip("/")
    step = step or max(15, int((end - start).total_seconds() // 120))
    body = HTTP.request("GET", f"{url}/api/v1/query_range",
                        {"query": query, "start": start.timestamp(), "end": end.timestamp(), "step": step},
                        headers=bearer(section("prometheus").get("token")))
    if not isinstance(body, dict) or body.get("status") != "success":
        raise NocError("bad_query", f"prometheus rejected the query: {body.get('error') if isinstance(body, dict) else body}")
    return [{"labels": r.get("metric", {}), "values": [[int(t), _num(v)] for t, v in r["values"]]}
            for r in body["data"]["result"]]


def series_key(labels: dict) -> str:
    return ",".join(f"{k}={v}" for k, v in sorted(labels.items()) if k != "__name__") or "total"


def es_search(index: str, query: str, start: datetime, end: datetime, size: int, group_by: Optional[str]) -> dict:
    es = section("elasticsearch")
    url = need("elasticsearch", "url").rstrip("/")
    ts = es.get("timestamp_field", "@timestamp")
    body: dict = {"size": size, "track_total_hits": True, "sort": [{ts: "asc"}],
                  "query": {"bool": {"filter": [{"range": {ts: {"gte": iso(start), "lte": iso(end)}}}],
                                     "must": [{"query_string": {"query": query or "*"}}]}}}
    if group_by:
        body["aggs"] = {"by": {"terms": {"field": group_by, "size": 20}, "aggs": {"first_seen": {"min": {"field": ts}}}}}
    headers = basic(es["user"], es.get("password", "")) if not is_tbd(es.get("user")) else {}
    return HTTP.request("POST", f"{url}/{index}/_search", body=body, headers=headers)


def grafana_alerts() -> list[dict]:
    url = need("grafana", "url").rstrip("/")
    return HTTP.request("GET", f"{url}/api/alertmanager/grafana/api/v2/alerts",
                        {"active": "true", "silenced": "false", "inhibited": "false"},
                        headers=bearer(section("grafana").get("token"))) or []


def _jira_base() -> tuple[str, dict]:
    j = section("jira")
    url = need("jira", "url").rstrip("/") + "/rest/api/2"
    headers = basic(j["user"], j.get("token", "")) if not is_tbd(j.get("user")) else bearer(j.get("token"))
    return url, headers


def jira_issue(key: str) -> dict:
    base, h = _jira_base()
    return HTTP.request("GET", f"{base}/issue/{key}",
                        {"fields": "summary,status,priority,assignee,created,updated,labels,description,components"}, headers=h)


def jira_search(jql: str, limit: int = 10, fields: str = "summary,status,priority,updated,labels") -> dict:
    base, h = _jira_base()
    return HTTP.request("POST", f"{base}/search", body={"jql": jql, "fields": fields.split(","), "maxResults": limit}, headers=h)


def jira_comments(key: str) -> list[dict]:
    base, h = _jira_base()
    return (HTTP.request("GET", f"{base}/issue/{key}/comment", {"maxResults": 100}, headers=h) or {}).get("comments", [])


def jira_add_comment(key: str, text: str) -> Any:
    base, h = _jira_base()
    return HTTP.request("POST", f"{base}/issue/{key}/comment", body={"body": text}, headers=h)


# ---------- misc ----------

def fingerprint(kind: str, *parts: str) -> str:
    """Stable identity from alert/ticket DATA only (never from model text)."""
    raw = "|".join([kind.strip().lower()] + [str(p).strip().lower() for p in parts])
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_state(name: str) -> dict:
    p = data_dir() / name
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except ValueError:
        return {}


def save_state(name: str, state: dict) -> None:
    p = data_dir() / name
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    tmp.replace(p)


def append_jsonl(name: str, rec: dict) -> None:
    with (data_dir() / name).open("a") as f:
        f.write(json.dumps(rec, default=str) + "\n")


def read_jsonl(name: str, since: Optional[datetime] = None) -> list[dict]:
    p = data_dir() / name
    out = []
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if since is None or parse_time(rec.get("at"), now()) >= since:
            out.append(rec)
    return out


def prune_jsonl(name: str, keep_days: int = 7) -> None:
    p = data_dir() / name
    if p.exists():
        keep = read_jsonl(name, now() - timedelta(days=keep_days))
        p.write_text("".join(json.dumps(r, default=str) + "\n" for r in keep))
