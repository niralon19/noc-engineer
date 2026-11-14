"""

REQUIRES FROM NIR: O1, O2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file noc-mcp/tools/network.py`; if BLOCKED, ask Nir. Never invent.
noc-mcp tools: network.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - resolve_dns(name, record_type, resolver=None)(...)
  - lookup_ip(ip) -> owner/ASN/provider/location(...)
  - query_ip_ranges(asn|provider|cidr)(...)
  - lookup_asn(asn)(...)
  - check_connectivity(src, dst, port, proto) with strict timeout(...)
  - inspect_firewall_rules(device, filter) READ-ONLY(...)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Distinguish observed state from configured policy. Support IPv4 and IPv6. Never change firewall/routing state.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
