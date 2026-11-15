---
name: config-change
description: "Customer or team asks to update a rule or configuration: review the request read-only before the change, and verify hermeticity/coupling after it."
---

# Configuration change

You never apply changes. You make them safer.

## Before (review)
1. Extract: which rule/config, requested change, reason, requested time.
2. Fetch current definition (`get_rule`) and recent changes (`get_rule_changes`).
3. Check: overlaps/conflicts with other rules, scope (which servers/topics/enrichment are affected), syntax/validation (`validate_rule_change` if available).
4. Baseline: current hermeticity and coupling of affected rules over the last 7 days.
5. Output: summary, risks, affected rules, a verification plan. Ask for missing details instead of assuming.

## After (verify)
1. Confirm the change landed (`get_rule_changes`) and when.
2. Compare hermeticity/coupling of the changed rule and of overlapping rules: 30–60 min after vs baseline.
3. Result: OK / DEGRADED (with `pipeline-walk` if needed). Comment in Jira via `jira-operations`.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
