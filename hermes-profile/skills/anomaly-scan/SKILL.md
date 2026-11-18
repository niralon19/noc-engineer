---
name: anomaly-scan
description: "Turn new anomaly findings (metric now vs same time last week) into a short message for the team channel."
---

# Anomaly scan

The cron script already compared every configured metric with the same time last week and passed you only NEW findings.

1. If the script output is empty, answer exactly `[SILENT]`.
2. If the output has only `errors` and no findings, answer `[SILENT]`.
3. Group findings that are likely the same event (same time, related servers/rules, port in and port out together).
4. For the most significant group, run 1-3 quick checks with `noc-tools` (the window before onset, neighbours, other hops) to say WHERE it is. Do not run a full investigation.
5. Message format (Slack, short):
   - first line: what, where, since when (e.g. "Port-in rate dropped 70% on 3 servers since 10:35")
   - affected entities (at most 5, then "+N")
   - now vs last week numbers
   - one line: likely location or "not located yet" plus the next check
