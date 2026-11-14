# MCP integration

Hermes connects to the **existing internal MCP server**. This repository does not implement a second MCP server. Configure the actual endpoint, transport, authentication and allowlisted tool names in the Hermes profile on the target host.

## Domains expected
- Monitoring: Prometheus, Grafana, Thanos, Loki/ECK
- Network: DNS, IPAM, RIPE/ASN, routing, firewall (read-only by default)
- ITSM: Jira issues, tasks, SLA and status
- Data: quality, enrichment and validation

`tool-contracts.yaml` is a discovery checklist, not a claim that these tools exist. At startup, enumerate tools and validate schemas. Fail closed for missing or changed tools.

> Note: if the existing internal MCP server is used, `noc-mcp/` holds only the contract and allowlist; the server code stays where it already lives.
