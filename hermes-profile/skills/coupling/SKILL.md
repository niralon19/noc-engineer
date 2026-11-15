---
name: coupling
description: "Rule coupling problems: records of a rule are not coupled/linked with the organization's internal enrichment as expected."
---

# Coupling

Coupling = records of a rule matched with internal organizational enrichment. A drop means records arrive but are not coupled, or arrive incomplete.

## Candidate locations
1. Upstream data loss (coupling ratio looks low because input changed): run `pipeline-walk` first
2. Internal enrichment source stale, missing or partially loaded (freshness, row counts, last sync)
3. Join key changed: format/field change in records or in enrichment (after a deploy or config change)
4. Rule/config change altering which records are eligible for coupling
5. Enrichment service on the platform unhealthy (`platform-operations`)
6. ASN/provider attribution wrong (`enrichment-quality`)

## Decisive checks
- Check numerator (coupled) and denominator (eligible) separately; which one moved?
- Coupling per rule, per server and per enrichment source; one source failing points at it.
- Enrichment freshness vs onset: a sync at onset time is a strong candidate.
- Sample-level check: fetch a few uncoupled records and verify why the key did not match (read-only query).

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
