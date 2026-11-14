"""What changed: Argo CD syncs, Kubernetes rollouts (Rancher + OpenShift), maintenance windows. Read-only."""
from __future__ import annotations

import re
from typing import Optional

from clients.argo import Argo
from clients.grafana import Grafana
from clients.jira import Jira
from clients.kubernetes import Kube
from clients.rules import Rules
from context import get_context
from schemas.common import ToolError, iso, is_tbd, not_configured, ok, parse_time, window
from tools._base import as_list, tool


def _in(ts: Optional[str], tr) -> bool:
    if not ts:
        return False
    t = parse_time(ts, tr.end)
    return tr.start <= t <= tr.end


@tool("argocd")
def get_argo_sync_history(apps: Optional[list[str]] = None, rule_id: Optional[str] = None,
                          start: Optional[str] = None, end: Optional[str] = None) -> dict:
    """Argo CD deployments (sync history) in the window for the given applications, or for the apps serving rule_id.
    Also returns current sync/health status and the last operation. Default window: last 24h."""
    ctx = get_context()
    tr = window(start, end, default_minutes=24 * 60)
    names = as_list(apps)
    if not names and rule_id:
        names = as_list((Rules(ctx).path(rule_id) or {}).get("argo_apps"))
    if not names:
        raise ToolError("bad_argument", "pass apps, or a rule_id whose path lists argo_apps")
    argo = Argo(ctx)
    result, errors = [], {}
    for name in names[:20]:
        try:
            app = argo.application(name)
        except ToolError as e:
            errors[name] = e.code
            continue
        st = app.get("status", {})
        op = st.get("operationState") or {}
        result.append({
            "app": name,
            "deploys_in_window": [{"deployed_at": h.get("deployedAt"), "started_at": h.get("deployStartedAt"),
                                   "revision": h.get("revision"), "id": h.get("id")}
                                  for h in st.get("history", []) if _in(h.get("deployedAt"), tr)],
            "sync_status": (st.get("sync") or {}).get("status"),
            "health": (st.get("health") or {}).get("status"),
            "last_operation": {"phase": op.get("phase"), "finished_at": op.get("finishedAt"), "message": (op.get("message") or "")[:300]},
        })
    notes = [f"failed apps: {errors}"] if errors else []
    return ok("argocd", {"apps": result}, tr, notes=notes)


@tool("kubernetes")
def get_deployment_history(cluster: str, namespace: Optional[str] = None, service: Optional[str] = None,
                           start: Optional[str] = None, end: Optional[str] = None) -> dict:
    """Kubernetes rollouts (new ReplicaSets) in the window on cluster 'openshift' or 'rancher', optionally filtered by
    namespace and service (deployment name substring). Returns deployment, revision, time, images. Default window: 24h."""
    ctx = get_context()
    tr = window(start, end, default_minutes=24 * 60)
    items = Kube(ctx, cluster).replicasets(namespace)
    rollouts = []
    for rs in items:
        md = rs.get("metadata", {})
        owner = next((o.get("name") for o in md.get("ownerReferences", []) if o.get("kind") == "Deployment"), md.get("name"))
        if service and service not in (owner or ""):
            continue
        if not _in(md.get("creationTimestamp"), tr):
            continue
        spec = (rs.get("spec") or {}).get("template", {}).get("spec", {})
        rollouts.append({"deployment": owner, "namespace": md.get("namespace"), "created_at": md.get("creationTimestamp"),
                         "revision": (md.get("annotations") or {}).get("deployment.kubernetes.io/revision"),
                         "images": [c.get("image") for c in spec.get("containers", [])],
                         "ready_replicas": (rs.get("status") or {}).get("readyReplicas", 0)})
    rollouts.sort(key=lambda r: r["created_at"])
    return ok(f"kubernetes:{cluster}", {"cluster": cluster, "rollouts": rollouts[:50]}, tr, truncated=len(rollouts) > 50)


@tool("maintenance")
def get_maintenance_windows(servers: Optional[list[str]] = None, start: Optional[str] = None,
                            end: Optional[str] = None) -> dict:
    """Planned maintenance / upgrades overlapping the window, optionally only those touching the given servers.
    Check this before calling a server drop an incident. Default window: last 24h."""
    ctx = get_context()
    tr = window(start, end, default_minutes=24 * 60)
    cfg = ctx.section("maintenance")
    src = cfg.get("source")
    wanted = as_list(servers)
    if src == "grafana_silences":
        out = []
        for s in Grafana(ctx).silences():
            st, en = s.get("startsAt"), s.get("endsAt")
            if not st or not en or parse_time(en, tr.end) < tr.start or parse_time(st, tr.end) > tr.end:
                continue
            matchers = s.get("matchers") or []
            if wanted and not any(_matches(m, w) for m in matchers for w in wanted):
                continue
            out.append({"starts_at": st, "ends_at": en, "comment": (s.get("comment") or "")[:200],
                        "created_by": s.get("createdBy"), "state": (s.get("status") or {}).get("state"),
                        "matchers": [{"name": m.get("name"), "value": m.get("value"), "regex": m.get("isRegex")} for m in matchers]})
        return ok("grafana_silences", {"windows": out}, tr)
    if src == "jira":
        tmpl = cfg.get("jira_jql")
        if is_tbd(tmpl):
            raise not_configured("maintenance.jira_jql")
        jql = tmpl.replace("{start}", tr.start.strftime("%Y-%m-%d %H:%M")).replace("{end}", tr.end.strftime("%Y-%m-%d %H:%M"))
        body = Jira(ctx).search(jql, "summary,status,description", 50)
        issues = [{"key": i["key"], "summary": i["fields"].get("summary"), "status": (i["fields"].get("status") or {}).get("name")}
                  for i in (body or {}).get("issues", [])]
        if wanted:
            issues = [i for i in issues if any(w.lower() in (i["summary"] or "").lower() for w in wanted)] or issues
        return ok("jira", {"windows": issues, "jql": jql}, tr)
    raise not_configured("maintenance.source (grafana_silences | jira)")


def _matches(matcher: dict, server: str) -> bool:
    v = str(matcher.get("value", ""))
    if matcher.get("isRegex"):
        try:
            return re.fullmatch(v, server) is not None
        except re.error:
            return False
    return v == server or server in v
