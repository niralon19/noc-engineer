---
name: network-engineering
description: "DNS, IP/CIDR, ASN/provider/RIPE, routing, connectivity and firewall checks. Use when a symptom may be in the network path or addressing."
---

# Network engineering

## Candidate locations
1. DNS: resolution failure, wrong record, TTL/propagation
2. Addressing: IP/CIDR ownership, ASN/provider mapping, RIPE data
3. Routing: prefix moved, path change, provider withdrawal
4. Connectivity: reachability, packet loss, latency on a specific path
5. Firewall/ACL: traffic blocked by policy

## Rules
- Identify source, destination, protocol, port, direction and time window before checking.
- Distinguish observed traffic from configured policy.
- Support IPv4 and IPv6. Check CIDR containment explicitly; do not guess ownership.
- Read-only: never change firewall, routing or DNS.

## Environment knowledge
<!-- Filled from the team's real procedures. Do not invent. -->
- TBD
