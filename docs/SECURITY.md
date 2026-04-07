# Security Threat Model

This document describes the threat model for `secure-mcp-boilerplate` and the mitigations implemented.

## Threat Matrix

| # | Attack Vector | Threat | Mitigation | Status |
|---|---------------|--------|------------|--------|
| 1 | **Stolen / forged JWT** | Attacker calls privileged MCP tools with a crafted or leaked token | HMAC-SHA256 signature verification via `hmac.compare_digest`; empty-secret guard (fail-closed); configurable secret via env var `MCP_OAUTH_SECRET` | ✅ Implemented in `src/auth.py` |
| 2 | **Rate limit / DoS** | Malicious or misconfigured client floods the server, exhausting compute or third-party API quotas | Per-client token-bucket rate limiter (`src/rate_limiter.py`); `MAX_CLIENTS=10_000` with FIFO eviction prevents unbounded memory growth; configurable `max_requests` / `window_seconds` | ✅ Implemented in `src/rate_limiter.py` |
| 3 | **Invisible breach / audit gap** | Tools are called without trace — no forensics, no incident response | Structured JSON audit log for every tool call: timestamp, client\_id, tool name, args hash, result status; written to `audit.log` via `structlog` | ✅ Implemented in `src/audit.py` |
| 4 | **Prompt injection via MCP tools** | AI agent relays attacker-crafted content that causes the MCP server to execute unintended actions | Tool arguments are not evaluated or executed; server only dispatches to pre-registered tool handlers; no `eval()` or shell execution in the tool dispatch path | ✅ By design in `src/server.py` |
| 5 | **Secret exposure in config / logs** | OAuth secret or API keys leak into log output or error messages | `Config.__repr__` masks the secret (`***`); secret loaded exclusively from environment variable, never hard-coded; empty-string default fails closed (no requests accepted) | ✅ Implemented in `src/config.py` |
| 6 | **Memory exhaustion via client table** | Unbounded number of unique client IDs fills the rate-limiter dict | `RateLimiter` caps tracked clients at `MAX_CLIENTS=10_000`; oldest entry evicted (FIFO) when limit is reached | ✅ Implemented in `src/rate_limiter.py` |

## Out-of-Scope Threats

The following are **not** mitigated by this boilerplate and require infrastructure-level controls:

- **Network-level DDoS** — use a reverse proxy (nginx, Cloudflare) in front of the MCP server.
- **Compromised AI model** — the server cannot verify the intent of the agent calling it; access control is token-based only.
- **Side-channel attacks** — timing attacks on JWT verification are mitigated by `hmac.compare_digest`, but hardware-level side channels are out of scope.
- **Dependency supply chain** — pin dependencies and use `pip-audit` / `safety` in CI for ongoing vulnerability scanning.

## Security Checklist for Deployers

- [ ] Set `MCP_OAUTH_SECRET` to a cryptographically random value (≥ 32 bytes)
- [ ] Run behind TLS termination (never expose raw HTTP to the internet)
- [ ] Set `MAX_REQUESTS` and `WINDOW_SECONDS` appropriate for your use case
- [ ] Enable log rotation on `audit.log` to prevent disk exhaustion
- [ ] Restrict network access to the MCP port using firewall rules
- [ ] Run `pip-audit` in CI to catch known CVEs in dependencies
