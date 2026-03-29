"""
Tests for app.services.graph_builder module.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.graph_builder import GraphBuilderService


class TestGraphBuilderService:
    """Tests for the GraphBuilderService."""

    @pytest.fixture
    def mock_zep(self):
        """Create a mocked Zep client."""
        with patch("app.services.graph_builder.Zep") as MockZep:
            mock_instance = MagicMock()
            MockZep.return_value = mock_instance
            yield mock_instance

    def test_init(self, mock_zep):
        service = GraphBuilderService()
        assert service is not None

    def test_create_graph(self, mock_zep):
        service = GraphBuilderService()
        graph_id = service.create_graph("test_graph")
        assert graph_id is not None

    def test_set_ontology(self, mock_zep, sample_ontology):
        service = GraphBuilderService()
        # set_ontology should not raise
        service.set_ontology("graph-123", sample_ontology)

    def test_get_graph_data(self, mock_zep):
        mock_zep.graph.node.get_by_graph_id.return_value = []
        mock_zep.graph.edge.get_by_graph_id.return_value = []
        service = GraphBuilderService()
        data = service.get_graph_data("graph-123")
        assert isinstance(data, dict)

    def test_delete_graph(self, mock_zep):
        service = GraphBuilderService()
        service.delete_graph("graph-123")
        mock_zep.graph.delete.assert_called_once_with(graph_id="graph-123")

    def test_methods_exist(self):
        assert hasattr(GraphBuilderService, "create_graph")
        assert hasattr(GraphBuilderService, "add_text_batches")
        assert hasattr(GraphBuilderService, "build_graph_async")
        assert hasattr(GraphBuilderService, "set_ontology")
        assert hasattr(GraphBuilderService, "get_graph_data")
        assert hasattr(GraphBuilderService, "delete_graph")
