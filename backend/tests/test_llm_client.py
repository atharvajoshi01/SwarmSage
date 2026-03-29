"""
Tests for app.utils.llm_client module.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from app.utils.llm_client import LLMClient


class TestLLMClientInit:
    """Tests for LLMClient initialization."""

    def test_init_uses_defaults(self):
        client = LLMClient()
        assert client.api_key == "test-key-not-real"
        assert client.model == "gpt-4o-mini"

    def test_init_custom_params(self):
        client = LLMClient(
            api_key="custom-key",
            base_url="https://custom.api/v1",
            model="gpt-4",
        )
        assert client.api_key == "custom-key"
        assert client.base_url == "https://custom.api/v1"
        assert client.model == "gpt-4"

    def test_init_no_api_key_raises(self):
        with patch("app.utils.llm_client.Config") as mock_config:
            mock_config.LLM_API_KEY = None
            mock_config.LLM_BASE_URL = "https://api.openai.com/v1"
            mock_config.LLM_MODEL_NAME = "gpt-4o-mini"
            with pytest.raises(ValueError, match="LLM_API_KEY"):
                LLMClient(api_key=None)


class TestLLMClientChat:
    """Tests for LLMClient.chat method."""

    def _make_client(self):
        client = LLMClient()
        client.client = MagicMock()
        return client

    def test_chat_returns_content(self):
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello, world!"
        client.client.chat.completions.create.return_value = mock_response

        result = client.chat([{"role": "user", "content": "Hi"}])
        assert result == "Hello, world!"

    def test_chat_strips_think_tags(self):
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            "<think>Let me think about this...</think>The answer is 42."
        )
        client.client.chat.completions.create.return_value = mock_response

        result = client.chat([{"role": "user", "content": "What is the answer?"}])
        assert result == "The answer is 42."
        assert "<think>" not in result

    def test_chat_passes_kwargs(self):
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "response"
        client.client.chat.completions.create.return_value = mock_response

        client.chat(
            [{"role": "user", "content": "test"}],
            temperature=0.5,
            max_tokens=100,
        )
        call_kwargs = client.client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 100


class TestLLMClientChatJSON:
    """Tests for LLMClient.chat_json method."""

    def _make_client(self):
        client = LLMClient()
        client.client = MagicMock()
        return client

    def test_chat_json_returns_parsed(self):
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value", "count": 42}'
        client.client.chat.completions.create.return_value = mock_response

        result = client.chat_json([{"role": "user", "content": "give json"}])
        assert result == {"key": "value", "count": 42}

    def test_chat_json_strips_markdown(self):
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '```json\n{"key": "value"}\n```'
        client.client.chat.completions.create.return_value = mock_response

        result = client.chat_json([{"role": "user", "content": "give json"}])
        assert result == {"key": "value"}

    def test_chat_json_invalid_raises(self):
        client = self._make_client()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not valid json {"
        client.client.chat.completions.create.return_value = mock_response

        with pytest.raises(ValueError, match="JSON格式无效"):
            client.chat_json([{"role": "user", "content": "give json"}])
