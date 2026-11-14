# noc-mcp/security
LLM/DEVELOPER: implement per-tool permission checks (read / write-limited / blocked), audit log for every write (who, tool, args hash, result), rate limiting, secret redaction in logs, and an allowlist loader (deny by default). Blocked forever: restart, scale, block IP, firewall change, arbitrary command execution.
