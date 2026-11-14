# Operational memory

PostgreSQL is the system of record for incident state, evidence references, investigation summaries, entity/service relationships and approved operational knowledge. Do not store credentials or unrestricted raw logs here. Use retention, provenance, access control and audit policies.

Memory is retrieved as context for Hermes; it is not a substitute for live telemetry. Mark stale knowledge and distinguish historical hypotheses from confirmed facts.
