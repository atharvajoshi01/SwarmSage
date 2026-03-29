"""
Tests for app.services.text_processor module.
"""

import pytest
from app.services.text_processor import TextProcessor


class TestTextProcessor:
    """Tests for the TextProcessor class."""

    def test_extract_from_files(self, sample_txt_file):
        text = TextProcessor.extract_from_files([sample_txt_file])
        assert "Dr. Alice Chen" in text

    def test_split_text_delegates(self):
        text = "Hello world. " * 100
        chunks = TextProcessor.split_text(text, chunk_size=100, overlap=10)
        assert len(chunks) >= 2
        for chunk in chunks:
            assert len(chunk) > 0

    def test_preprocess_text_normalizes_newlines(self):
        text = "line1\r\nline2\rline3\nline4"
        result = TextProcessor.preprocess_text(text)
        assert "\r" not in result
        assert "line1" in result
        assert "line4" in result

    def test_preprocess_text_removes_excess_whitespace(self):
        text = "line1\n\n\n\n\nline2"
        result = TextProcessor.preprocess_text(text)
        # Should have at most two consecutive newlines
        assert "\n\n\n" not in result
        assert "line1" in result
        assert "line2" in result

    def test_preprocess_text_strips_lines(self):
        text = "  hello  \n  world  "
        result = TextProcessor.preprocess_text(text)
        assert result == "hello\nworld"

    def test_preprocess_text_empty(self):
        assert TextProcessor.preprocess_text("") == ""
        assert TextProcessor.preprocess_text("   ") == ""

    def test_get_text_stats(self):
        text = "Hello world\nSecond line\nThird line"
        stats = TextProcessor.get_text_stats(text)
        assert stats["total_chars"] == len(text)
        assert stats["total_lines"] == 3
        assert stats["total_words"] == 6

    def test_get_text_stats_single_line(self):
        text = "one two three"
        stats = TextProcessor.get_text_stats(text)
        assert stats["total_lines"] == 1
        assert stats["total_words"] == 3

    def test_get_text_stats_empty(self):
        stats = TextProcessor.get_text_stats("")
        assert stats["total_chars"] == 0
        assert stats["total_words"] == 0
