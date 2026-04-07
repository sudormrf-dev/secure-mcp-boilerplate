"""Tests for OAuth token validation."""
import hashlib
import hmac


from src.auth import validate_bearer_token


def _make_token(sub: str, scopes: str, exp: int, secret: str) -> str:
    payload = f"{sub}:{scopes}:{exp}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def test_valid_token() -> None:
    token = _make_token("user1", "read,write", 9999999999, "secret")
    claims = validate_bearer_token(token, "secret")
    assert claims is not None
    assert claims.sub == "user1"
    assert "read" in claims.scopes


def test_invalid_signature() -> None:
    token = _make_token("user1", "read", 9999999999, "secret")
    result = validate_bearer_token(token, "wrong-secret")
    assert result is None


def test_malformed_token() -> None:
    assert validate_bearer_token("notavalidtoken", "secret") is None
    assert validate_bearer_token("", "secret") is None


def test_empty_secret_rejected() -> None:
    """An empty secret must always reject tokens to prevent misconfiguration."""
    token = _make_token("user1", "read", 9999999999, "")
    assert validate_bearer_token(token, "") is None
