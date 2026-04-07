"""Audit logging for MCP tool calls."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("mcp.audit")


def log_tool_call(
    tool_name: str, client_id: str, success: bool, duration_ms: float
) -> None:
    """Log a tool call to the audit trail."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "client": client_id,
        "success": success,
        "duration_ms": round(duration_ms, 2),
    }
    logger.info(json.dumps(entry))
