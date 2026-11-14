---
name: pipeline-walk
description: Localize a hermeticity, coupling, loss or load problem by walking the data path hop by hop and finding the first hop where counts diverge. Use in every alert, ticket or proactive investigation.
---

# Pipeline walk

The data path is long; a failure at any hop appears downstream as lost hermeticity or coupling. Find the FIRST hop where the data diverges.

1. **Scope.** Get the rule (`get_rule`) and its path (`get_rule_path`): which servers, topics, services and enrichment sources serve it. If no rule is involved, scope by server or topic.
2. **Window.** Onset time from the alert/ticket; compare onset-30m..now with the same window yesterday and last week.
3. **Bisect.** Call `get_hop_counts` for the middle hop first, then move up or down the path. At each hop compare IN vs OUT and vs baseline:
   - IN normal, OUT low -> the problem is IN this hop.
   - IN already low -> the problem is upstream; move up.
   - Both normal -> the problem is downstream; move down.
4. **Partial vs total.** If only some servers/partitions/pods diverge, the hop is right but the scope is those instances; name them.
5. **Then go deep** on the guilty hop with the matching supporting skill: `capture-servers` (hops 1–3), `kafka-pipeline` (4), `platform-operations` (5), `coupling` / `enrichment-quality` (6), `traffic-hermetic` + `change-correlation` (7), `observability-queries` for storage and data trust.
6. **Report** the hop id as `suspected_location.hop`, the instances, and the hops verified healthy as `ruled_out`.

Rules: counts from different hops must use the same window and the same scope. A hop with no data is `missing_data`, not "healthy".
