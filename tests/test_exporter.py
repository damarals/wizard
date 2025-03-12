"""
Tests for the article exporter functionality.
"""

import csv
import os
from tempfile import TemporaryDirectory

from wizard.core.exporter import export_articles, get_available_fields


class TestExporter:
    """Test cases for article exporter."""

    def test_export_articles(self, sample_articles):
        """Test exporting articles to CSV."""
        with TemporaryDirectory() as temp_dir:
            # Export to temporary file
            output_file = os.path.join(temp_dir, "test_export.csv")
            result = export_articles(sample_articles, output_file)

            # Check result is the output file path
            assert result == output_file

            # Check file exists
            assert os.path.exists(output_file)

            # Check file contents
            with open(output_file, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader)

                # Check header includes required fields
                assert "title" in header
                assert "authors" in header
                assert "doi" in header

                # Read first row
                first_row = next(reader)

                # Get column indices
                title_idx = header.index("title")
                authors_idx = header.index("authors")

                # Check values in first row
                assert first_row[title_idx] == sample_articles[0].title
                assert first_row[authors_idx] == ";".join(sample_articles[0].authors)

    def test_export_articles_with_selected_fields(self, sample_articles):
        """Test exporting only selected fields to CSV."""
        with TemporaryDirectory() as temp_dir:
            # Export to temporary file with selected fields
            output_file = os.path.join(temp_dir, "test_export_selected.csv")
            fields = ["title", "doi", "is_open_access"]
            _ = export_articles(sample_articles, output_file, fields)

            # Check file exists
            assert os.path.exists(output_file)

            # Check file contents
            with open(output_file, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                header = next(reader)

                # Check header has only selected fields
                assert header == fields

                # Check number of rows
                rows = list(reader)
                assert len(rows) == len(sample_articles)

    def test_export_articles_empty_list(self):
        """Test exporting an empty list of articles."""
        with TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "empty_export.csv")
            result = export_articles([], output_file)

            # Should return empty string for empty input
            assert result == ""

            # File should not be created
            assert not os.path.exists(output_file)

    def test_get_available_fields(self):
        """Test getting list of available fields for export."""
        fields = get_available_fields()

        # Check structure
        assert isinstance(fields, list)
        assert len(fields) > 0

        # Check field structure
        for field in fields:
            assert "name" in field
            assert "description" in field
            assert "default_enabled" in field

        # Check essential fields are present
        field_names = [f["name"] for f in fields]
        essential_fields = ["title", "authors", "doi", "abstract"]
        for field in essential_fields:
            assert field in field_names
