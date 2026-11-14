---
name: kafka-pipeline
description: Kafka in the data path: producer rate, consumer lag, partitions, rebalances, retention. Use when data is lost or delayed between servers and processing.
---

# Kafka pipeline

## Candidate locations (hop kafka_ingest)
1. Producers (servers) stopped/slowed producing to the topic
2. Consumer lag growing: consumer too slow, stuck partition, rebalance loop
3. Partition skew: one partition hot or without a consumer
4. Broker issue: under-replicated partitions, disk, ISR shrink
5. Retention/size: data expired before it was consumed (real loss)

## Decisive checks
- Produce rate vs consume rate for the topic in the window; lag per partition, not only total.
- Consumer group: members count and rebalances around onset (often a rollout).
- Lag growing then data missing later = retention loss; say so explicitly.
- Delay is not loss: if lag recovers and counts catch up, report delay with duration.

Read-only: no offset resets, no consumer restarts.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
