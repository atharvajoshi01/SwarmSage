"""
Tests for app.utils.zep_paging module.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from app.utils.zep_paging import (
    _fetch_page_with_retry,
    fetch_all_nodes,
    fetch_all_edges,
)


class TestFetchPageWithRetry:
    """Tests for _fetch_page_with_retry."""

    def test_success_first_try(self):
        api_call = MagicMock(return_value=[{"id": 1}])
        result = _fetch_page_with_retry(api_call, max_retries=3, retry_delay=0.01)
        assert result == [{"id": 1}]
        api_call.assert_called_once()

    def test_retries_on_connection_error(self):
        api_call = MagicMock(
            side_effect=[ConnectionError("fail"), [{"id": 1}]]
        )
        result = _fetch_page_with_retry(
            api_call, max_retries=3, retry_delay=0.01
        )
        assert result == [{"id": 1}]
        assert api_call.call_count == 2

    def test_raises_after_max_retries(self):
        api_call = MagicMock(side_effect=ConnectionError("always fails"))
        with pytest.raises(ConnectionError, match="always fails"):
            _fetch_page_with_retry(api_call, max_retries=2, retry_delay=0.01)
        assert api_call.call_count == 2

    def test_invalid_max_retries(self):
        with pytest.raises(ValueError, match="max_retries must be >= 1"):
            _fetch_page_with_retry(MagicMock(), max_retries=0)


class TestFetchAllNodes:
    """Tests for fetch_all_nodes."""

    def _make_node(self, uuid_val):
        node = MagicMock()
        node.uuid_ = uuid_val
        return node

    def test_single_page(self):
        client = MagicMock()
        nodes = [self._make_node(f"u{i}") for i in range(5)]
        client.graph.node.get_by_graph_id.return_value = nodes

        result = fetch_all_nodes(
            client, "graph-1", page_size=100, retry_delay=0.01
        )
        assert len(result) == 5

    def test_multiple_pages(self):
        client = MagicMock()
        page1 = [self._make_node(f"u{i}") for i in range(3)]
        page2 = [self._make_node(f"u{i+3}") for i in range(2)]

        client.graph.node.get_by_graph_id.side_effect = [page1, page2]

        result = fetch_all_nodes(
            client, "graph-2", page_size=3, retry_delay=0.01
        )
        assert len(result) == 5

    def test_max_items_limit(self):
        client = MagicMock()
        nodes = [self._make_node(f"u{i}") for i in range(10)]
        client.graph.node.get_by_graph_id.return_value = nodes

        result = fetch_all_nodes(
            client, "graph-3", page_size=100, max_items=5, retry_delay=0.01
        )
        assert len(result) == 5

    def test_empty_graph(self):
        client = MagicMock()
        client.graph.node.get_by_graph_id.return_value = []

        result = fetch_all_nodes(client, "empty-graph", retry_delay=0.01)
        assert result == []


class TestFetchAllEdges:
    """Tests for fetch_all_edges."""

    def _make_edge(self, uuid_val):
        edge = MagicMock()
        edge.uuid_ = uuid_val
        return edge

    def test_single_page(self):
        client = MagicMock()
        edges = [self._make_edge(f"e{i}") for i in range(3)]
        client.graph.edge.get_by_graph_id.return_value = edges

        result = fetch_all_edges(
            client, "graph-1", page_size=100, retry_delay=0.01
        )
        assert len(result) == 3

    def test_empty(self):
        client = MagicMock()
        client.graph.edge.get_by_graph_id.return_value = []

        result = fetch_all_edges(client, "empty", retry_delay=0.01)
        assert result == []
