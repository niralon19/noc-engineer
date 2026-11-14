"""

REQUIRES FROM NIR: M2 (docs/OPEN-QUESTIONS.md). Before implementing/filling run `python3 scripts/open_items.py --file noc-mcp/tools/enrichment.py`; if BLOCKED, ask Nir. Never invent.
noc-mcp tools: enrichment.

FOR THE LLM / DEVELOPER OPENING THIS FILE
What to implement:
  - audit_enrichment(dataset)(...)
  - validate_asn(asn, cidr)(...)
  - validate_provider(provider, asn)(...)
  - validate_ripe_data(cidr)(...)

Rules for every tool in noc-mcp (see docs/tools-contract.md):
  - Return the ToolResult envelope from schemas/common.py: ok, data, error, source, queried_at (UTC ISO), time_range, truncated.
  - Never raise to the caller; map failures to an explicit error {code, message, retryable}.
  - Every outbound call has a timeout and bounded result size (aggregate or paginate; the environment has ~100K series, never one request per series).
  - Read-only unless the module says otherwise. Writes require a permission check (security/) and an audit record.
  - No arbitrary command execution on production hosts, ever.
  - Tool names must match noc-mcp/config/tool-contracts.yaml; if you rename one, update tool-contracts.yaml and tools.include in hermes-profile/config.yaml too.

Validate CIDR containment, address family, ASN/provider mapping, provenance and freshness. Keep conflicting candidates and their confidence; never fabricate values. Relates to the ASN/provider sync pipeline.

Acceptance: unit tests in the matching tests/ folder pass with mocked backends; no network in tests.
"""
