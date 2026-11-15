---
name: platform-operations
description: "Kubernetes platform: Rancher and OpenShift clusters, Argo CD, pods, rollouts, resources, Postgres and ECK health. Use to confirm or rule out a platform or deploy cause."
---

# Platform operations (Rancher, OpenShift, Argo CD)

## Candidate locations (hops stream_processing, storage_*)
1. Argo sync or rollout in the window (cheapest decisive check), including drift/OutOfSync and failed syncs
2. Pods: CrashLoop, restarts, OOMKilled, pending/unschedulable, readiness failing
3. Resources: CPU throttling, memory pressure, PVC/disk, connection pools
4. Node/network-policy problem affecting several workloads in one cluster
5. Postgres: connections, locks, slow queries, replication lag, disk
6. ECK: cluster health (yellow/red), rejected writes, ILM/rollover, disk watermarks

## Rules
- Know which cluster (Rancher or OpenShift) runs each service on the rule's path (`get_rule_path`).
- Separate desired state (Git/Argo, spec) from observed state (status/events).
- A rollout after the onset is not the cause.
- Read-only. Restart, scale, rollback, sync are recommendations for a human.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
