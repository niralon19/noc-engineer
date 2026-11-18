---
name: daily-summary
description: "09:00 summary of the last 24h of anomaly scans for the team channel."
---

# Daily anomaly summary

Input: the digest from the cron script (runs, findings grouped per check and series, errors).

Write one short Slack message:
1. Bottom line: "quiet night" or the number of distinct problems.
2. Top problems (at most 5): check, entity, how many times, first/last seen, worst now-vs-last-week ratio. Merge rows that are clearly the same event.
3. Still active? For the top 1-2 run one `noc-tools` query to say whether it is still happening.
4. Scan health: runs with errors, checks not configured. Say it if the scan itself was blind.

Do not repeat raw JSON. No recommendations unless something is still active.
