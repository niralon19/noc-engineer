---
name: change-correlation
description: "Find what changed around the onset: rule/configuration changes, Argo syncs, deployments, server maintenance/upgrades. Run first in every investigation."
---

# Change correlation (step 0)

Most problems here follow a change. Before anything else, list changes in onset-2h..onset+15m:
1. Rule & configuration management system: `get_rule_changes` (the rule itself, overlapping rules, global config).
2. Argo CD: `get_argo_sync_history` (apps on the path of the rule).
3. Kubernetes rollouts: `get_deployment_history` (Rancher and OpenShift).
4. Server maintenance / upgrades: `get_maintenance_windows` and server version changes.
5. Enrichment source updates: last sync of internal enrichment and ASN/provider data.

For each change: time, scope (which rule/servers/services), and whether its timing and scope match the symptom. A change that starts AFTER the onset or touches a different scope is ruled out. A matching change is a candidate to TEST, not a conclusion. If a server was in a maintenance window, say so first: the alert may be expected.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
