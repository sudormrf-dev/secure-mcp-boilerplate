"""OAuth 2.1 token validation utilities."""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass


@dataclass
class TokenClaims:
    """Decoded claims from a validated bearer token."""

    sub: str
    scopes: list[str]
    exp: int


def validate_bearer_token(token: str, secret: str) -> TokenClaims | None:
    """Validate a bearer token using HMAC-SHA256.

    Returns claims if the token is valid, or None if validation fails.
    Uses ``hmac.compare_digest`` for timing-safe signature comparison.
    """
    if not token or not secret:
        return None
    # Simple HMAC validation for demo — use JWT in production
    parts = token.split(".")
    if len(parts) != 2:  # noqa: PLR2004
        return None
    payload, signature = parts
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    # Parse simple payload: "sub:scopes:exp"
    try:
        sub, scopes_str, exp_str = payload.split(":")
        return TokenClaims(sub=sub, scopes=scopes_str.split(","), exp=int(exp_str))
    except ValueError:
        return None
