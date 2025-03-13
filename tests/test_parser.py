"""
Tests for the HTML parser functionality.
"""

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
        # We need to properly add a text-down-01 element to the sample HTML
        sample_html = sample_html_article_detail.replace(
            "<body>",
            '<body>\n<p class="text-down-01">2023 - Science Publishers | Journal of Climate AI</p>',
        )

        metadata = CAPESParser.parse_article_detail(sample_html)

        # Check common metadata fields
        assert "title" in metadata
        assert "abstract" in metadata

        # Check for extracted publication info
        assert metadata.get("publication_date") == "2023"
        assert metadata.get("journal") == "Journal of Climate AI"
        assert metadata.get("publisher") == "Science Publishers"

    def test_extract_publication_info(self):
        """Test extracting publication information from different formats."""
        test_cases = [
            # Format: Year - | Journal
            (
                "2021 - | Computers, materials & continua/Computers, materials & continua (Print)",
                {
                    "publication_date": "2021",
                    "publisher": None,
                    "journal": "Computers, materials & continua/Computers, materials & continua (Print)",
                },
            ),
            # Format: Year - Publisher | Journal
            (
                "2020 - Multidisciplinary Digital Publishing Institute | Energies",
                {
                    "publication_date": "2020",
                    "publisher": "Multidisciplinary Digital Publishing Institute",
                    "journal": "Energies",
                },
            ),
            # Format: Year - Publisher | Journal
            (
                "2013 - Springer Nature | Health Information Science and Systems",
                {
                    "publication_date": "2013",
                    "publisher": "Springer Nature",
                    "journal": "Health Information Science and Systems",
                },
            ),
            # Format: Year - | Journal
            (
                "2022 - | Balkan Journal of Electrical and Computer Engineering",
                {
                    "publication_date": "2022",
                    "publisher": None,
                    "journal": "Balkan Journal of Electrical and Computer Engineering",
                },
            ),
            # Format: Year - Publisher | Journal
            (
                "2021 - Elsevier BV | Science of Computer Programming",
                {
                    "publication_date": "2021",
                    "publisher": "Elsevier BV",
                    "journal": "Science of Computer Programming",
                },
            ),
            # Format from search results: Year | Journal
            ("2023 | Nature", {"publication_date": "2023", "publisher": None, "journal": "Nature"}),
            # Edge case: no publisher or journal
            ("2023 - ", {"publication_date": "2023", "publisher": None, "journal": None}),
        ]

        for text, expected in test_cases:
            result = CAPESParser.extract_publication_info(text)
            assert result == expected, f"Failed for input: '{text}'"
