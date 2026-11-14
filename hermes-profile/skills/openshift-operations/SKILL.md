---
name: openshift-operations
description: OpenShift/Kubernetes and service operations: pods, deployments, rollouts, resources, restarts. Use to confirm or rule out a platform or deploy cause.
---

# OpenShift & service operations

## Candidate locations
1. Recent deploy / config change in the window (check rollout history first: it is the cheapest decisive check)
2. Pods: crash loops, restarts, OOMKilled, pending/unschedulable
3. Resources: CPU throttling, memory pressure, PVC/disk full, connection pool limits
4. Node or network-policy issue affecting several workloads
5. Dependency service in the cluster unhealthy

## Rules
- Separate desired state (spec) from observed state (status/events).
- Correlate the rollout time with the metric onset; a deploy after the onset is not the cause.
- Read-only. Restart, scale, rollback or deploy are recommendations for a human, never actions.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
