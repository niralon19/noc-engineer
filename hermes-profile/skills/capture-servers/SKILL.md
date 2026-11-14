---
name: capture-servers
description: Monitored servers receiving traffic: maintenance/upgrades, packet loss, traffic load, NIC/kernel/application drops, load balance between servers.
---

# Capture servers

## Candidate locations (hops ingress_traffic, server_nic, capture_app)
1. Server in maintenance/upgrade (expected drop; check first)
2. Incoming traffic itself changed (upstream, tap/mirror, routing) - compare all servers of the same feed
3. NIC: rx_dropped/rx_missed, ring buffer overflow, link saturation, link flaps
4. Kernel/host: softirq/CPU saturation, NUMA/IRQ affinity, memory pressure
5. Capture application: drops counter, crash/restart, version after upgrade, config
6. Imbalance: one server overloaded while peers are idle

## Decisive checks
- Peer comparison: same metric on all servers of the feed. One server = local; all servers = upstream or shared.
- Drop accounting: traffic in at NIC vs packets processed by the app vs records produced to Kafka.
- Load: interface utilization and CPU at peak vs capacity; is the drop correlated with load peaks?
- Upgrade: version/uptime change at onset.

Read-only: reboot, restart or traffic re-balance are recommendations for a human.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
