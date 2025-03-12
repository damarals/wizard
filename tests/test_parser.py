"""
Tests for the HTML parser functionality.
"""

from unittest.mock import MagicMock

import pytest

from wizard.core.parser import CAPESParser


class TestCAPESParser:
    """Test cases for CAPESParser class."""

    def test_parse_search_results(self, sample_html_search_results):
        """Test parsing search results HTML."""
        result = CAPESParser.parse_search_results(sample_html_search_results)

        # Check structure
        assert "articles" in result
        assert "pagination" in result

        # Check pagination data
        assert "current_page" in result["pagination"]
        assert "total_pages" in result["pagination"]
        assert "total_items" in result["pagination"]

        # Check article data (if there are any articles in the sample)
        if result["articles"]:
            article = result["articles"][0]
            assert "title" in article
            assert "article_id" in article
            # Other fields are optional, so we don't assert them

    def test_parse_article_detail(self, sample_html_article_detail):
        """Test parsing article detail HTML."""
        metadata = CAPESParser.parse_article_detail(sample_html_article_detail)

        # Check common metadata fields
        assert "title" in metadata

        # Check optional fields that may be present
        optional_fields = [
            "abstract",
            "issn",
            "volume",
            "issue",
            "language",
            "topics",
            "publisher",
            "is_open_access",
            "is_peer_reviewed",
            "citation_count",
            "reader_count",
            "authors",
            "doi",
            "publication_date",
            "journal",
        ]

        # Assert that at least some of the optional fields are present
        # (We don't need all of them to be present in the sample)
        has_some_optional_fields = any(field in metadata for field in optional_fields)
        assert has_some_optional_fields, "No optional metadata fields were found"
