"""
Tests for app.services.simulation_manager module.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.simulation_manager import (
    SimulationManager,
    SimulationState,
    SimulationStatus,
)


class TestSimulationStatus:
    """Tests for SimulationStatus enum."""

    def test_values(self):
        assert SimulationStatus.CREATED == "created"
        assert SimulationStatus.PREPARING == "preparing"
        assert SimulationStatus.READY == "ready"
        assert SimulationStatus.RUNNING == "running"
        assert SimulationStatus.COMPLETED == "completed"
        assert SimulationStatus.FAILED == "failed"
        assert SimulationStatus.STOPPED == "stopped"
        assert SimulationStatus.PAUSED == "paused"


class TestSimulationState:
    """Tests for SimulationState dataclass."""

    def test_creation(self):
        state = SimulationState(
            simulation_id="sim_123",
            project_id="proj_456",
            graph_id="g_789",
            status=SimulationStatus.CREATED,
        )
        assert state.simulation_id == "sim_123"
        assert state.project_id == "proj_456"
        assert state.graph_id == "g_789"
        assert state.status == SimulationStatus.CREATED

    def test_defaults(self):
        state = SimulationState(
            simulation_id="sim_1",
            project_id="proj_1",
            graph_id="g_1",
            status=SimulationStatus.CREATED,
        )
        assert state.entities_count == 0
        assert state.profiles_count == 0
        assert state.config_generated is False
        assert state.current_round == 0
        assert state.error is None

    def test_enable_platforms(self):
        state = SimulationState(
            simulation_id="sim_1",
            project_id="proj_1",
            graph_id="g_1",
            enable_twitter=True,
            enable_reddit=False,
            status=SimulationStatus.CREATED,
        )
        assert state.enable_twitter is True
        assert state.enable_reddit is False
