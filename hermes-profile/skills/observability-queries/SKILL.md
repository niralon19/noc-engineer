---
name: observability-queries
description: How to query Prometheus/Thanos/Grafana/Loki/ELK correctly and decide whether data is trustworthy. Use whenever you query metrics or logs.
---

# Observability queries

## Trust the data first
- Check freshness: last sample time vs now. Stale or missing series = telemetry problem, not a service problem. Report it as such.
- Check coverage: did all expected entities return series? A drop in series count looks like a traffic drop.
- Check units and labels before comparing values; never mix rates and counters.

## Query correctly
- Counters: use `rate()`/`increase()` over a window >= 4x the scrape interval. Never compare raw counters.
- Use Thanos for windows longer than local retention; Prometheus for the last hours.
- Always aggregate (`sum by`, `topk`) before returning; never pull thousands of raw series.
- Compare with a baseline: same window yesterday and last week (`offset 1d`, `offset 7d`).
- Logs: bound by time and service; look for the FIRST new error signature after onset, not the most frequent one.

## Cite
Every evidence item: the exact query, time range, and what you observed.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
