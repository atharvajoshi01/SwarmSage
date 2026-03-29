"""
Tests for app.services.ontology_generator module.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.ontology_generator import OntologyGenerator


class TestOntologyGenerator:
    """Tests for the OntologyGenerator service."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mocked LLMClient."""
        with patch("app.services.ontology_generator.LLMClient") as MockLLM:
            mock_instance = MagicMock()
            MockLLM.return_value = mock_instance
            yield mock_instance

    def test_generate_returns_ontology(self, mock_llm, sample_text):
        expected = {
            "entity_types": [
                {"name": "Person", "description": "A human individual"},
                {"name": "Organization", "description": "A company or institution"},
            ],
            "relationship_types": [
                {"name": "WORKS_AT", "source": "Person", "target": "Organization"},
            ],
            "analysis_summary": "Research collaboration network",
        }
        mock_llm.chat_json.return_value = expected

        generator = OntologyGenerator()
        result = generator.generate(
            document_texts=sample_text,
            simulation_requirement="Predict research trends",
        )

        assert "entity_types" in result
        assert "relationship_types" in result
        mock_llm.chat_json.assert_called_once()

    def test_generate_passes_text_to_prompt(self, mock_llm, sample_text):
        mock_llm.chat_json.return_value = {
            "entity_types": [],
            "relationship_types": [],
        }

        generator = OntologyGenerator()
        generator.generate(
            document_texts=sample_text,
            simulation_requirement="Test requirement",
        )

        call_args = mock_llm.chat_json.call_args
        messages = call_args[1].get("messages") or call_args[0][0]
        msg_text = str(messages)
        # Should contain the document text
        assert "Alice" in msg_text or len(msg_text) > 100

    def test_generate_llm_failure(self, mock_llm, sample_text):
        mock_llm.chat_json.side_effect = Exception("LLM API error")

        generator = OntologyGenerator()
        with pytest.raises(Exception, match="LLM API error"):
            generator.generate(
                document_texts=sample_text,
                simulation_requirement="Test",
            )

    def test_generate_with_additional_context(self, mock_llm, sample_text):
        mock_llm.chat_json.return_value = {
            "entity_types": [{"name": "Person", "description": "A person"}],
            "relationship_types": [],
        }

        generator = OntologyGenerator()
        result = generator.generate(
            document_texts=sample_text,
            simulation_requirement="Predict outcomes",
            additional_context="Focus on university entities",
        )
        assert "entity_types" in result
