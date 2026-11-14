---
name: oncall-report
description: Produce the morning report for the on-call engineer: last 24h incidents, open issues, recurring problems, risks and what needs action today.
---

# On-call morning report

Audience: the on-call engineer starting the shift. Make it scannable in 2 minutes.

Sections, in order:
1. **Needs action today:** open Jira items by priority, SLA at risk, stuck investigations.
2. **Last 24h incidents:** one line each: headline, location, status (CONFIRMED / SUSPECTED), Jira key.
3. **Recurring:** same fingerprint or entity 3+ times in 7 days.
4. **Early warnings:** proactive findings that did not raise alerts yet.
5. **Data/tool health:** systems the agent could not query; stale data.

Rules: VERIFIED and SUSPECTED must be clearly separated. Every item has a Jira key, investigation id or query reference. No changes to Jira or production. If a section is empty, write "none".

Use `jira-operations` for all Jira reads and writes.
