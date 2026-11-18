---
name: noc-environment
description: "The NOC data path and how to locate a problem on it. Load for every investigation or technical question."
---

# NOC environment

## Data path
Servers receive traffic -> capture applications on the servers -> Kafka -> processing on Kubernetes (Rancher, OpenShift; deployed by Argo CD) -> internal enrichment -> rule matching (rule & configuration management system) -> storage (Postgres, ECK).

Customer problems usually surface as a rule's hermeticity or coupling degrading, but the cause can be any hop on that path: a rule or configuration change, maintenance or an upgrade, packet loss, or load.

## How to locate a problem
1. Onset: when did the symptom start? Use the metric itself, not the alert time.
2. What changed around the onset: deployments, rule/config changes, maintenance.
3. Walk the path from the start and find the FIRST hop where the data diverges from last week / the previous window. Everything after it is a consequence.
4. At that hop, list candidate causes and test each one. Rule out the others with evidence.
5. Scope: which servers, partitions, pods, rules, customers. Is anything else affected?

## Environment knowledge
TBD. Hop ids, the metric for each hop, and known failure patterns are added here by the NOC team. Until then, say which hop you could not measure instead of guessing a metric name.
