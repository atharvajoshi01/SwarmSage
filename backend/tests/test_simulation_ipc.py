"""
Tests for app.services.simulation_ipc module.
"""

import json
import pytest

from app.services.simulation_ipc import (
    IPCCommand,
    IPCResponse,
    CommandType,
    CommandStatus,
)


class TestCommandType:
    """Tests for CommandType enum."""

    def test_interview_value(self):
        assert CommandType.INTERVIEW == "interview"

    def test_batch_interview_value(self):
        assert CommandType.BATCH_INTERVIEW == "batch_interview"

    def test_close_env_value(self):
        assert CommandType.CLOSE_ENV == "close_env"


class TestCommandStatus:
    """Tests for CommandStatus enum."""

    def test_values(self):
        assert CommandStatus.PENDING == "pending"
        assert CommandStatus.PROCESSING == "processing"
        assert CommandStatus.COMPLETED == "completed"
        assert CommandStatus.FAILED == "failed"


class TestIPCCommand:
    """Tests for IPCCommand dataclass."""

    def test_creation(self):
        cmd = IPCCommand(
            command_id="cmd-1",
            command_type=CommandType.INTERVIEW,
            args={"agent_id": "a1"},
        )
        assert cmd.command_id == "cmd-1"
        assert cmd.command_type == CommandType.INTERVIEW
        assert cmd.args == {"agent_id": "a1"}

    def test_has_timestamp(self):
        cmd = IPCCommand(
            command_id="cmd-2",
            command_type=CommandType.BATCH_INTERVIEW,
            args={},
        )
        assert cmd.timestamp is not None

    def test_serialization(self):
        cmd = IPCCommand(
            command_id="cmd-3",
            command_type=CommandType.CLOSE_ENV,
            args={},
        )
        d = {
            "command_id": cmd.command_id,
            "command_type": cmd.command_type,
            "args": cmd.args,
        }
        serialized = json.dumps(d)
        assert "close_env" in serialized


class TestIPCResponse:
    """Tests for IPCResponse dataclass."""

    def test_creation(self):
        resp = IPCResponse(
            command_id="cmd-1",
            status=CommandStatus.COMPLETED,
            result={"message": "done"},
        )
        assert resp.status == CommandStatus.COMPLETED
        assert resp.result == {"message": "done"}

    def test_error_response(self):
        resp = IPCResponse(
            command_id="cmd-2",
            status=CommandStatus.FAILED,
            error="something went wrong",
        )
        assert resp.status == CommandStatus.FAILED
        assert resp.error == "something went wrong"

    def test_has_timestamp(self):
        resp = IPCResponse(
            command_id="cmd-3",
            status=CommandStatus.PENDING,
        )
        assert resp.timestamp is not None
