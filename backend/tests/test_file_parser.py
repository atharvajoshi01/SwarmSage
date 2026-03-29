"""
Tests for app.utils.file_parser module.
"""

import os
import pytest
from app.utils.file_parser import FileParser, split_text_into_chunks, _read_text_with_fallback


class TestFileParser:
    """Tests for the FileParser class."""

    def test_extract_text_txt(self, sample_txt_file):
        text = FileParser.extract_text(sample_txt_file)
        assert "Dr. Alice Chen" in text
        assert "Stanford University" in text

    def test_extract_text_md(self, sample_md_file):
        text = FileParser.extract_text(sample_md_file)
        assert "Research Report" in text
        assert "Key Findings" in text

    def test_extract_text_unsupported_extension(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.xyz")
        with open(path, "w") as f:
            f.write("content")
        with pytest.raises(ValueError, match="不支持的文件格式"):
            FileParser.extract_text(path)

    def test_extract_text_missing_file(self):
        with pytest.raises(FileNotFoundError):
            FileParser.extract_text("/nonexistent/file.txt")

    def test_extract_from_multiple(self, sample_txt_file, sample_md_file):
        text = FileParser.extract_from_multiple([sample_txt_file, sample_md_file])
        assert "文档 1:" in text or "sample.txt" in text
        assert "文档 2:" in text or "sample.md" in text
        assert "Dr. Alice Chen" in text
        assert "Research Report" in text

    def test_extract_from_multiple_with_bad_file(self, sample_txt_file):
        text = FileParser.extract_from_multiple([sample_txt_file, "/nonexistent.txt"])
        assert "Dr. Alice Chen" in text
        assert "提取失败" in text

    def test_supported_extensions(self):
        assert ".pdf" in FileParser.SUPPORTED_EXTENSIONS
        assert ".md" in FileParser.SUPPORTED_EXTENSIONS
        assert ".txt" in FileParser.SUPPORTED_EXTENSIONS
        assert ".markdown" in FileParser.SUPPORTED_EXTENSIONS


class TestReadTextWithFallback:
    """Tests for encoding detection fallback."""

    def test_utf8_file(self, tmp_dir):
        path = os.path.join(tmp_dir, "utf8.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Hello world! Unicode: cafe\u0301")
        result = _read_text_with_fallback(path)
        assert "Hello world!" in result

    def test_non_utf8_file(self, tmp_dir):
        path = os.path.join(tmp_dir, "latin1.txt")
        with open(path, "wb") as f:
            # Write bytes that are invalid UTF-8 but valid in other encodings
            f.write(b"caf\xe9 au lait is a drink")
        result = _read_text_with_fallback(path)
        # Should read without raising, with some form of the content
        assert "caf" in result
        assert "drink" in result


class TestSplitTextIntoChunks:
    """Tests for the split_text_into_chunks function."""

    def test_empty_text(self):
        assert split_text_into_chunks("") == []
        assert split_text_into_chunks("   ") == []

    def test_text_smaller_than_chunk_size(self):
        text = "Short text."
        chunks = split_text_into_chunks(text, chunk_size=500)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_text_larger_than_chunk_size(self):
        text = "A" * 1200
        chunks = split_text_into_chunks(text, chunk_size=500, overlap=50)
        assert len(chunks) >= 2
        # Each chunk should not exceed chunk_size significantly
        for chunk in chunks:
            assert len(chunk) <= 600  # some flexibility for boundary finding

    def test_overlap_behavior(self):
        # Create text with clear boundaries
        text = "Sentence one. " * 50 + "Sentence two. " * 50
        chunks = split_text_into_chunks(text, chunk_size=200, overlap=50)
        assert len(chunks) >= 2
        # Verify chunks are non-empty
        for chunk in chunks:
            assert len(chunk) > 0

    def test_sentence_boundary_splitting(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = split_text_into_chunks(text, chunk_size=40, overlap=5)
        # Should try to split at sentence boundaries
        assert len(chunks) >= 2

    def test_single_chunk_for_small_text(self):
        text = "Just a small piece of text."
        chunks = split_text_into_chunks(text, chunk_size=1000)
        assert len(chunks) == 1
        assert chunks[0] == text
