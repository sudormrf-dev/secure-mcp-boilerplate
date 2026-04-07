# secure-mcp-boilerplate

> **Your MCP server is one stolen token away from disaster.**

This repository provides a production-ready boilerplate for building secure
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers in
Python. It ships with OAuth 2.1 token validation, per-client token-bucket rate
limiting, structured audit logging, and a clean configuration system — so you
can focus on writing tools instead of reinventing security primitives.

---

## Why MCP security matters

MCP servers expose tools and resources that AI agents call autonomously. A
misconfigured server can allow:

- **Token theft** — unauthenticated callers invoking privileged tools.
- **Abuse / DoS** — unbounded request rates exhausting compute or third-party
  API quotas.
- **Invisible breaches** — no audit trail means you will never know which tool
  was called, by whom, and when.

This boilerplate addresses all three threat vectors out of the box.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MCP Client (AI agent)              │
└──────────────────────────┬──────────────────────────┘
                           │ Bearer token
                           ▼
┌─────────────────────────────────────────────────────┐
│                  FastMCP server                      │
│                                                      │
│  ┌────────────┐   ┌──────────────┐   ┌───────────┐  │
│  │  src/auth  │──▶│src/rate_limit│──▶│ src/audit │  │
│  │ (HMAC val) │   │ (TokenBucket)│   │  (logger) │  │
│  └────────────┘   └──────────────┘   └───────────┘  │
│                                                      │
│  Tools: echo_tool, get_system_info                   │
│  Resources: config://server                          │
└─────────────────────────────────────────────────────┘
```

---

## Quick start

```bash
git clone https://github.com/your-org/secure-mcp-boilerplate
cd secure-mcp-boilerplate

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -e ".[dev]"

# Copy and edit environment variables
cp .env.example .env
# Set MCP_OAUTH_SECRET to a strong random value before going to production!

python -m src.server
```

The server starts on `http://127.0.0.1:8000` by default.

---

## Configuration environment variables

| Variable | Default | Description |
|---|---|---|
| `MCP_HOST` | `127.0.0.1` | Bind address |
| `MCP_PORT` | `8000` | Bind port |
| `MCP_OAUTH_SECRET` | `""` (empty — server rejects all requests until set) | HMAC secret for token validation |
| `MCP_RATE_CAPACITY` | `10` | Max burst tokens per client |
| `MCP_RATE_REFILL` | `1` | Token refill rate (tokens/second) |
| `MCP_LOG_LEVEL` | `INFO` | Logging verbosity |

**Never commit a real `MCP_OAUTH_SECRET` to version control.** Use a secrets
manager (AWS Secrets Manager, HashiCorp Vault, GitHub Secrets) in production.

---

## Rate limiting

The rate limiter uses the **token bucket** algorithm (`src/rate_limiter.py`).
Each client gets an independent bucket with:

- A **capacity** — maximum burst size (default 10 requests).
- A **refill rate** — tokens added per second (default 1/s).

When a client's bucket is empty, the tool returns immediately with a
`"Rate limit exceeded."` response and the call is logged as a failure.

```python
from src.rate_limiter import RateLimiter

rl = RateLimiter(capacity=10.0, refill_rate=1.0)
if rl.is_allowed("client-42"):
    # process request
    ...
```

To change limits per-client or per-tool, extend `RateLimiter` with a
`capacity_for(client_id, tool_name)` method.

---

## OAuth 2.1 token validation

`src/auth.py` provides a lightweight HMAC-based token scheme suitable for
internal services and demos. Tokens have the format:

```
{sub}:{scopes}:{exp}.{hmac_sha256_signature}
```

Example:

```python
import hashlib, hmac

secret = "my-secret"
payload = "alice:read,write:9999999999"
sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
token = f"{payload}.{sig}"
```

Validate with:

```python
from src.auth import validate_bearer_token

claims = validate_bearer_token(token, secret)
if claims is None:
    raise PermissionError("Invalid token")
print(claims.sub, claims.scopes, claims.exp)
```

**Production recommendation:** Replace the HMAC scheme with a proper JWT
library (e.g. [`python-jose`](https://python-jose.readthedocs.io/)) and an
OAuth 2.1 authorization server (e.g. Keycloak, Auth0, Okta).

---

## Audit logging

Every tool call is recorded to `mcp.audit` logger (`src/audit.py`):

```json
{
  "timestamp": "2026-04-07T14:23:01.123456+00:00",
  "tool": "echo_tool",
  "client": "client-42",
  "success": true,
  "duration_ms": 0.87
}
```

Wire the `mcp.audit` logger to your SIEM, CloudWatch, or ELK stack by
configuring a standard Python `logging.Handler`.

---

## Running with Docker

```bash
# Build and start
docker compose -f docker/docker-compose.yml up --build

# Pass a production secret
MCP_OAUTH_SECRET=my-real-secret docker compose -f docker/docker-compose.yml up
```

The `docker/Dockerfile` uses `python:3.11-slim` and installs only the runtime
dependencies, keeping the image around ~350 MB (python:3.11-slim base + runtime deps).

---

## Running tests

```bash
pytest tests/ -v
```

Lint:

```bash
ruff check src/ tests/
```

Type check:

```bash
mypy src/ --ignore-missing-imports
```

---

## Project structure

```
secure-mcp-boilerplate/
├── src/
│   ├── __init__.py          # Package marker
│   ├── auth.py              # HMAC-based bearer token validation
│   ├── audit.py             # Structured JSON audit logging
│   ├── config.py            # Dataclass configuration with env var overrides
│   ├── rate_limiter.py      # Token bucket rate limiter (per-client)
│   └── server.py            # FastMCP server with tool/resource definitions
├── tests/
│   ├── test_auth.py         # Token validation tests (valid, invalid, malformed)
│   ├── test_audit.py        # Audit log emission tests
│   ├── test_config.py       # Config defaults and env override tests
│   └── test_rate_limiter.py # Token bucket and per-client isolation tests
├── docker/
│   ├── Dockerfile           # Production image (python:3.11-slim, non-root user)
│   └── docker-compose.yml   # Single-service compose for local development
├── .github/workflows/
│   └── ci.yml               # GitHub Actions: lint, type-check, test
├── pyproject.toml           # PEP 621 metadata, dependencies, tool config
├── .env.example             # Template for local environment variables
├── CONTRIBUTING.md          # Contribution guidelines
└── LICENSE                  # MIT license
```

---

## Security checklist

Before deploying to production, review the following items:

- [ ] Replace the default `MCP_OAUTH_SECRET` with a cryptographically random
  value of at least 32 bytes.
- [ ] Switch from the demo HMAC token scheme to a standards-compliant JWT
  library with proper key rotation.
- [ ] Enable TLS termination (via a reverse proxy such as nginx or Caddy, or
  through a cloud load balancer).
- [ ] Restrict network access to the MCP port using firewall rules or security
  groups so only authorized AI agents can connect.
- [ ] Connect the `mcp.audit` logger to a centralized log aggregation service
  (e.g. CloudWatch, Datadog, ELK) for alerting on suspicious patterns.
- [ ] Review rate-limit values (`MCP_RATE_CAPACITY`, `MCP_RATE_REFILL`) based
  on your expected traffic and adjust per-client or per-tool as needed.
- [ ] Run the Docker container as a non-root user (the provided Dockerfile
  already creates and switches to a dedicated `mcp` user).
- [ ] **Prompt injection via MCP tools** — AI agents may relay attacker-crafted
  input as tool arguments. Validate and sanitize all tool inputs server-side.
  Never pass tool arguments directly to shell commands, SQL queries, or file
  system operations without strict validation.
- [ ] **mTLS for enterprise deployments** — For zero-trust environments, enable
  mutual TLS (mTLS) between MCP clients and the server so both sides
  authenticate with certificates. Configure this at the reverse proxy or load
  balancer level.

---

## Extending the boilerplate

**Adding a new tool:** Define an async function decorated with `@app.tool()` in
`src/server.py`. Follow the existing pattern of checking rate limits, measuring
duration, and calling `log_tool_call` for audit compliance.

**Adding a new resource:** Use `@app.resource("your://uri")` to expose
read-only configuration or metadata to MCP clients.

**Custom rate-limit policies:** Subclass `RateLimiter` and override bucket
creation to assign different capacities based on client identity or tool name.

**Persistent audit storage:** Replace the stdlib `logging` handler attached to
`mcp.audit` with a handler that writes to a database, message queue, or cloud
logging API.

---

## Related repositories

- **[playwright-stealth-agents](https://github.com/your-org/playwright-stealth-agents)**
  — Browser automation agents that work alongside MCP servers for web tasks.
- **[n8n-enterprise-patterns](https://github.com/your-org/n8n-enterprise-patterns)**
  — Production n8n workflow patterns including MCP tool integrations.

---

## License

MIT — see [LICENSE](LICENSE).
