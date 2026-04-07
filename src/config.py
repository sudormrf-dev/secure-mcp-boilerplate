"""Server configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Server configuration with environment variable overrides."""

    host: str = "127.0.0.1"
    port: int = 8000
    rate_limit_capacity: float = 10.0
    rate_limit_refill: float = 1.0
    oauth_secret: str = ""  # Must be set via MCP_OAUTH_SECRET env var
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> Config:
        """Create a Config instance from environment variables."""
        return cls(
            host=os.getenv("MCP_HOST", "127.0.0.1"),
            port=int(os.getenv("MCP_PORT", "8000")),
            rate_limit_capacity=float(os.getenv("MCP_RATE_CAPACITY", "10")),
            rate_limit_refill=float(os.getenv("MCP_RATE_REFILL", "1")),
            oauth_secret=os.getenv("MCP_OAUTH_SECRET", ""),
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO"),
        )
