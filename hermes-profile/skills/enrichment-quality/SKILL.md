---
name: enrichment-quality
description: Validate ASN, provider, country, location and connection-type enrichment (RIPE-based). Use when an alert or ticket may be explained by wrong or stale enrichment, or when asked about enrichment data.
---

# Enrichment quality

Wrong enrichment can look like a real incident: traffic "moving" to another provider or country, a sudden drop for one ASN, or a customer attributed to the wrong provider.

## Candidate locations
1. Stale source: the RIPE/provider data was not refreshed (check last sync time and the enrichment-audit results)
2. Mapping error: CIDR mapped to the wrong ASN/provider (containment, overlapping prefixes, longest-prefix match)
3. Recent source change: a prefix really moved (new allocation, transfer, re-announcement)
4. Pipeline gap: enrichment missing for part of the data (nulls, "unknown" provider growing)
5. Real network change, enrichment correct (hand back to `traffic-hermetic` / `network-engineering`)

## Decisive checks
- Did the "change" start exactly at an enrichment sync time? Then suspect the data, not the network.
- Compare raw IP/prefix traffic with the enriched aggregates: if raw traffic is stable but per-provider/country totals moved, it is enrichment.
- Validate the specific CIDR against the source: containment, address family (IPv4/IPv6), ASN, provider, freshness.
- Keep conflicting candidates with their source; never fabricate a value or pick one silently.

## Rules
- Read-only: report corrections as recommendations; never change the provider table or sync.
- State provenance and age for every enrichment value cited.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
