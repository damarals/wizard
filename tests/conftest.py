"""
Pytest fixtures for CAPES Research Wizard tests.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from wizard.core.scraper import Article, ArticleScraper
from wizard.utils.config import Config


@pytest.fixture
def sample_html_search_results():
    """Load sample search results HTML from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "search_results.html"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_html_article_detail():
    """Load sample article detail HTML from fixtures."""
    fixture_path = Path(__file__).parent / "fixtures" / "article_detail.html"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def sample_articles():
    """Create sample articles for testing."""
    return [
        Article(
            title="Machine Learning for Climate Change Research",
            authors=["Smith, J.", "Johnson, A."],
            publication_date="2023",
            doi="10.1234/journal.2023.001",
            journal="Journal of Climate AI",
            abstract="This paper explores how machine learning can be used to analyze climate data.",
            search_term="Climate AI",
            article_id="ABC123",
            issn="1234-5678",
            volume="45",
            issue="2",
            pages="123-145",
            language="English",
            publisher="Science Publishers",
            topics=["Machine Learning", "Climate Change", "AI"],
            citation_count=15,
            reader_count=120,
            detail_url="https://example.com/articles/ABC123",
            is_open_access=True,
            is_peer_reviewed=True,
        ),
        Article(
            title="Neural Networks in Environmental Science",
            authors=["Brown, M.", "Davis, L."],
            publication_date="2022",
            doi="10.5678/env.2022.042",
            journal="Environmental Data Science",
            abstract="An overview of neural network applications in environmental monitoring.",
            search_term="Climate AI",
            article_id="DEF456",
            issn="2345-6789",
            volume="12",
            issue="3",
            pages="78-95",
            language="English",
            publisher="Green Science Press",
            topics=["Neural Networks", "Environmental Science", "Data Analysis"],
            citation_count=8,
            reader_count=65,
            detail_url="https://example.com/articles/DEF456",
            is_open_access=False,
            is_peer_reviewed=True,
        ),
    ]


@pytest.fixture
def mock_requests_session():
    """Create a mock requests session for testing."""
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.text = ""
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response
    return mock_session


@pytest.fixture
def mock_scraper(mock_requests_session):
    """Create a mock scraper with a mocked requests session."""
    scraper = ArticleScraper(max_workers=1, request_delay=0.01)
    scraper.session = mock_requests_session
    return scraper


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Config()
    config.data = {
        "max_workers": 2,
        "request_delay": 0.1,
        "max_pages": 3,
        "fetch_details": True,
        "use_advanced_search": True,
        "export_filename": "test_export.csv",
        "selected_export_fields": ["title", "authors", "doi"],
    }
    return config
