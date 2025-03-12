"""
Tests for the ArticleScraper class.
"""

from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from wizard.core.scraper import Article, ArticleScraper


class TestArticleScraper:
    """Test cases for ArticleScraper class."""

    def test_init(self):
        """Test initializing the scraper."""
        scraper = ArticleScraper(max_workers=5, request_delay=1.5, max_pages=10)
        assert scraper.max_workers == 5
        assert scraper.request_delay == 1.5
        assert scraper.max_pages == 10

    def test_construct_search_url_simple(self):
        """Test constructing a simple search URL."""
        scraper = ArticleScraper()
        url = scraper._construct_search_url("climate change", advanced=False, page=2)

        assert "climate%20change" in url
        assert "page=2" in url
        assert "mode=advanced" not in url

    def test_construct_search_url_advanced(self):
        """Test constructing an advanced search URL."""
        scraper = ArticleScraper()
        url = scraper._construct_search_url('climate AND "neural networks"', advanced=True, page=1)

        assert "all:contains" in url
        assert "page=1" in url
        assert "mode=advanced" in url

    def test_extract_doi(self):
        """Test extracting DOI from URLs."""
        scraper = ArticleScraper()

        # Test standard DOI URL
        doi = scraper._extract_doi("https://doi.org/10.1234/journal.2023.001")
        assert doi == "10.1234/journal.2023.001"

        # Test DOI in query parameter
        doi = scraper._extract_doi("https://example.com/article?doi=10.5678/journal.2022.042")
        assert doi == "10.5678/journal.2022.042"

        # Test DOI in path
        doi = scraper._extract_doi("https://journal.org/doi/10.9012/article.2021.015")
        assert doi == "10.9012/article.2021.015"

        # Test URL without DOI
        doi = scraper._extract_doi("https://example.com/article123")
        assert doi is None

    def test_extract_article_id_from_url(self):
        """Test extracting article ID from URL."""
        scraper = ArticleScraper()

        # Test with standard CAPES URL
        url = "https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=all&id=ABC123"
        article_id = scraper._extract_article_id_from_url(url)
        assert article_id == "ABC123"

        # Test with URL without ID
        url = "https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html"
        article_id = scraper._extract_article_id_from_url(url)
        assert article_id is None

    def test_get_total_pages(self, sample_html_search_results):
        """Test extracting total pages from search results."""
        scraper = ArticleScraper()

        # Create BeautifulSoup object from sample HTML
        soup = BeautifulSoup(sample_html_search_results, "html.parser")

        # Mock the pagination element
        pagination = soup.new_tag(
            "nav", **{"class": "br-pagination", "data-total": "120", "data-per-page": "30"}
        )
        soup.body.append(pagination)

        total_pages = scraper._get_total_pages(soup)
        assert total_pages == 4  # 120 items / 30 per page = 4 pages

    @patch("wizard.core.scraper.requests.Session")
    def test_search(self, mock_session_class, mock_scraper, sample_articles):
        """Test the search method."""
        # Setup mock responses
        mock_scraper.get_all_article_listings = MagicMock(
            return_value={"Climate AI": [{"article_id": "ABC123"}]}
        )
        mock_scraper.fetch_article_details = MagicMock(return_value=sample_articles)

        # Execute search
        search_dict = {"Climate AI": "machine learning AND climate change"}
        results = mock_scraper.search(search_dict, advanced=True)

        # Verify results
        assert mock_scraper.get_all_article_listings.called
        assert mock_scraper.fetch_article_details.called
        assert len(results) == 2
        assert results[0].title == "Machine Learning for Climate Change Research"
        assert results[1].title == "Neural Networks in Environmental Science"

    def test_search_with_callback(self, mock_scraper, sample_articles):
        """Test search with progress callback."""
        # Setup mock responses
        mock_scraper.get_all_article_listings = MagicMock(
            return_value={"Climate AI": [{"article_id": "ABC123"}]}
        )
        mock_scraper.fetch_article_details = MagicMock(return_value=sample_articles)

        # Setup callback tracker
        progress_values = []
        status_messages = []

        def callback(progress, status):
            progress_values.append(progress)
            status_messages.append(status)

        # Execute search
        search_dict = {"Climate AI": "machine learning AND climate change"}
        results = mock_scraper.search(search_dict, callback=callback)

        # Verify callb
