"""Secure MCP server."""
from __future__ import annotations

import platform
import time

import structlog

from src.audit import log_tool_call
from src.config import Config
from src.rate_limiter import RateLimiter

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise ImportError("mcp package is required: pip install mcp>=1.0.0") from exc

log = structlog.get_logger()

_config = Config.from_env()
_rate_limiter = RateLimiter(
    capacity=_config.rate_limit_capacity,
    refill_rate=_config.rate_limit_refill,
)

app = FastMCP("secure-mcp-boilerplate")


@app.tool()
async def echo_tool(message: str, client_id: str = "anonymous") -> str:
    """Echo a message back."""
    start = time.monotonic()
    allowed = _rate_limiter.is_allowed(client_id)
    if not allowed:
        duration_ms = (time.monotonic() - start) * 1000
        log_tool_call("echo_tool", client_id, False, duration_ms)
        return "Rate limit exceeded."
    result = f"Echo: {message}"
    duration_ms = (time.monotonic() - start) * 1000
    log_tool_call("echo_tool", client_id, True, duration_ms)
    log.info("echo_tool called", client_id=client_id, message=message)
    return result


@app.tool()
async def get_system_info(client_id: str = "anonymous") -> dict[str, str]:
    """Return basic system information."""
    start = time.monotonic()
    allowed = _rate_limiter.is_allowed(client_id)
    if not allowed:
        duration_ms = (time.monotonic() - start) * 1000
        log_tool_call("get_system_info", client_id, False, duration_ms)
        return {"error": "Rate limit exceeded."}
    info = {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
    }
    duration_ms = (time.monotonic() - start) * 1000
    log_tool_call("get_system_info", client_id, True, duration_ms)
    log.info("get_system_info called", client_id=client_id)
    return info


@app.resource("config://server")
async def server_config() -> str:
    """Expose non-sensitive server configuration."""
    cfg = Config.from_env()
    return (
        f"host={cfg.host}\n"
        f"port={cfg.port}\n"
        f"rate_limit_capacity={cfg.rate_limit_capacity}\n"
        f"rate_limit_refill={cfg.rate_limit_refill}\n"
        f"log_level={cfg.log_level}\n"
    )


if __name__ == "__main__":
    app.run(transport="sse")
