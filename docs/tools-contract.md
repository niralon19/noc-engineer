# Tools contract

Implemented tools, arguments and config: `noc-mcp/README.md` (run `python noc-mcp/server.py --list`).
Envelope: `ok, data, error{code,message,retryable}, source, queried_at, time_range, truncated, notes`.

Error codes the agent must understand:
| code | meaning | what the agent does |
|---|---|---|
| `not_configured` | backend/query is TBD | record in `missing_data`; never treat as healthy |
| `hop_not_instrumented` | hop has no queries | `missing_data`; skip to the next hop in pipeline-walk |
| `bad_argument` | wrong hop/cluster/time | fix the call |
| `not_found` | rule/issue/app missing | say so |
| `backend_timeout`, `backend_unreachable` (retryable) | transient | retry once, else `INVESTIGATION_INCOMPLETE` |
| `backend_auth`, `backend_error`, `bad_query` | config/query problem | report, do not guess |
| `permission_denied` | write disabled | return the result instead of posting |
| `validation_failed` | investigation breaks the contract | fix the JSON and retry |

Planned (contract only, not implemented yet): network, enrichment, data-quality and platform tools listed in `noc-mcp/config/tool-contracts.yaml` outside `implemented:`.
