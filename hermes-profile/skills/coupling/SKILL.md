---
name: coupling
description: Domain knowledge for coupling / ratio alerts: ratios and percentages between related metrics drifting from normal.
---

# Coupling & ratios

## Candidate locations
1. Numerator vs denominator: which side of the ratio moved? (Always check both raw series.)
2. Data pipeline: one side stale or missing
3. A single entity skewing the aggregate
4. Real behavioral change in the system or traffic mix

## Decisive checks
- Plot numerator and denominator separately for the window.
- Break the ratio down by entity/provider to find the contributor.
- Distinguish a step change (config/deploy) from slow drift (capacity/trend).

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- Metrics and their meaning: TBD
- Normal ranges / known seasonality: TBD
- Known recurring causes: TBD
- Owners / escalation: TBD
