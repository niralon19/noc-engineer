---
name: traffic-hermetic
description: Domain knowledge for traffic integrity / hermeticity alerts: traffic volume, drops, imbalance between paths or providers.
---

# Traffic & hermeticity

## Candidate locations (check in this order)
1. Measurement/pipeline: is the data itself complete and fresh? (collector, exporter, missing series)
2. Single link/interface or provider path
3. Provider / upstream (several links of the same provider)
4. Routing change (prefix moved to another path)
5. Source side: customer or service actually sent less traffic
6. Enrichment: provider/ASN/country attribution changed, not the traffic (load `enrichment-quality`)

## Decisive checks
- Compare the affected entity with its peers in the same window.
- Compare in vs out and path A vs path B; hermeticity breaks show as an imbalance.
- Overlay the onset time with routing/config changes.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- Metrics and their meaning: TBD
- Normal ranges / known seasonality: TBD
- Known recurring causes: TBD
- Owners / escalation: TBD
