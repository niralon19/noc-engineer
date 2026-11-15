---
name: coatr
description: "Domain knowledge for application and database alerts (COATR): errors, latency, failures in application or DB layers."
---

# Application & DB (COATR)

Use `platform-operations` for cluster-level causes and `pipeline-walk` when the app is one hop of the data path.

## Candidate locations
1. Dependency down/slow (DB, upstream API, network to dependency)
2. Recent deploy or config change
3. Resource exhaustion (CPU, memory, connections, disk)
4. Specific endpoint/query rather than the whole service
5. Bad input / traffic pattern from a specific client

## Decisive checks
- Error/latency split by endpoint and by instance.
- Logs around the onset: first new error signature.
- DB: slow queries, locks, connection pool, replication lag (read-only queries only).
- Deployment history in the window.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- Metrics and their meaning: TBD
- Normal ranges / known seasonality: TBD
- Known recurring causes: TBD
- Owners / escalation: TBD
