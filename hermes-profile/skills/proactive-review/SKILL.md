---
name: proactive-review
description: "Review findings from the deterministic anomaly engine (deviation from baseline, slow drift, degradation below alert threshold) and decide if they matter."
---

# Proactive review

Input: findings produced by the anomaly scan script, primarily per-rule hermeticity/coupling drops vs baseline, plus hop-level divergences (server drops, Kafka lag). You do not scan metrics yourself.

1. If the input says there are no findings, respond exactly `[SILENT]`.
2. Group findings that share a hop, server, topic, rule or start time; several rules dropping together usually means one shared hop. Check `change-correlation` and maintenance windows before calling anything a problem.
3. For each group decide: noise (known pattern, maintenance, seasonality), watch (trend worth tracking), or investigate.
4. For "investigate": Follow the investigation protocol and output contract from the `alert-investigation` skill. Keep it short; the goal is to catch degradation before an alert fires.
5. Never open Jira from this route. Report to the team channel: what, where, since when, why it matters, suggested owner. Mark everything as SUSPECTED unless confirmed.
