"""Tests for audit logging."""
import json
import logging

import pytest

from src.audit import log_tool_call


def test_audit_log_emits(caplog: "pytest.LogCaptureFixture") -> None:
    with caplog.at_level(logging.INFO, logger="mcp.audit"):
        log_tool_call("echo_tool", "client1", True, 12.5)
    assert len(caplog.records) == 1
    entry = json.loads(caplog.records[0].message)
    assert entry["tool"] == "echo_tool"
    assert entry["client"] == "client1"
    assert entry["success"] is True
    assert entry["duration_ms"] == 12.5


def test_audit_log_failure(caplog: "pytest.LogCaptureFixture") -> None:
    with caplog.at_level(logging.INFO, logger="mcp.audit"):
        log_tool_call("dangerous_tool", "bad_client", False, 0.1)
    entry = json.loads(caplog.records[0].message)
    assert entry["success"] is False
