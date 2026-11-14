---
name: traffic-hermetic
description: Rule hermeticity problems: a rule does not capture all the traffic it should (or captures traffic it should not).
---

# Hermeticity

Hermeticity = the rule captures all and only the traffic it is meant to capture. Most often the cause is upstream loss or a change.

## Candidate locations
1. Rule or configuration change (`change-correlation`): definition, scope, overlapping/conflicting rule, global config
2. Data loss on the path (`pipeline-walk`): servers, NIC, capture app, Kafka, processing
3. Traffic itself changed: the customer's traffic moved (new IPs/prefixes, provider, path)
4. Enrichment attribution changed so the rule no longer matches (`enrichment-quality`)
5. Measurement: the hermeticity KPI pipeline itself is stale or incomplete (`observability-queries`)

## Decisive checks
- Expected vs matched traffic for the rule, split by server and by sub-scope (prefix, provider).
- If expected traffic also dropped, it is upstream, not the rule.
- If expected is stable and matched dropped at a rule change time, it is the rule/config.
- Compare with other rules on the same servers: all affected = path; one rule = rule/config/traffic.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
