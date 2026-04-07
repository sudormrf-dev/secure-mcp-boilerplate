"""Tests for server config."""
import pytest

from src.config import Config


def test_config_defaults() -> None:
    cfg = Config()
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 8000
    assert cfg.rate_limit_capacity == 10.0


def test_config_from_env(monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setenv("MCP_PORT", "9000")
    monkeypatch.setenv("MCP_HOST", "0.0.0.0")
    cfg = Config.from_env()
    assert cfg.port == 9000
    assert cfg.host == "0.0.0.0"
