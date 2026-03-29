"""
Tests for app.config module.
"""

import os
import pytest
from unittest.mock import patch

from app.config import Config


class TestConfig:
    """Tests for the Config class."""

    def test_default_values(self):
        assert Config.JSON_AS_ASCII is False
        assert Config.DEFAULT_CHUNK_SIZE == 500
        assert Config.DEFAULT_CHUNK_OVERLAP == 50
        assert Config.MAX_CONTENT_LENGTH == 50 * 1024 * 1024
        assert "pdf" in Config.ALLOWED_EXTENSIONS
        assert "md" in Config.ALLOWED_EXTENSIONS
        assert "txt" in Config.ALLOWED_EXTENSIONS

    def test_oasis_actions(self):
        assert "CREATE_POST" in Config.OASIS_TWITTER_ACTIONS
        assert "LIKE_POST" in Config.OASIS_TWITTER_ACTIONS
        assert "CREATE_POST" in Config.OASIS_REDDIT_ACTIONS
        assert "CREATE_COMMENT" in Config.OASIS_REDDIT_ACTIONS

    def test_validate_with_keys(self):
        # Keys are set in conftest.py via env vars
        errors = Config.validate()
        assert errors == []

    def test_validate_missing_llm_key(self):
        original = Config.LLM_API_KEY
        try:
            Config.LLM_API_KEY = None
            errors = Config.validate()
            assert any("LLM_API_KEY" in e for e in errors)
        finally:
            Config.LLM_API_KEY = original

    def test_validate_missing_zep_key(self):
        original = Config.ZEP_API_KEY
        try:
            Config.ZEP_API_KEY = None
            errors = Config.validate()
            assert any("ZEP_API_KEY" in e for e in errors)
        finally:
            Config.ZEP_API_KEY = original

    def test_validate_missing_both(self):
        orig_llm = Config.LLM_API_KEY
        orig_zep = Config.ZEP_API_KEY
        try:
            Config.LLM_API_KEY = None
            Config.ZEP_API_KEY = None
            errors = Config.validate()
            assert len(errors) == 2
        finally:
            Config.LLM_API_KEY = orig_llm
            Config.ZEP_API_KEY = orig_zep

    def test_report_agent_defaults(self):
        assert Config.REPORT_AGENT_MAX_TOOL_CALLS >= 1
        assert Config.REPORT_AGENT_MAX_REFLECTION_ROUNDS >= 1
        assert 0 <= Config.REPORT_AGENT_TEMPERATURE <= 1.0

    def test_secret_key_default(self):
        assert Config.SECRET_KEY == "swarmsage-secret-key"
