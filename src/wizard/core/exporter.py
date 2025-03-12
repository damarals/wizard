"""
Exporter module for CAPES Research Wizard

This module provides functionality to export article data to CSV format.
"""

import csv
import os
from dataclasses import asdict
from typing import Dict, List, Optional

from wizard.core.scraper import Article
from wizard.utils.logger import get_logger

logger = get_logger(__name__)


def export_articles(
    articles: List[Article], filename: str, fields: Optional[List[str]] = None
) -> str:
    """
    Export articles to a CSV file.

    Args:
        articles: List of Article objects to export
        filename: Output filename
        fields: List of fields to include in the export (None for all fields)

    Returns:
        Path to the exported file
    """
    if not articles:
        logger.warning("No articles to export")
        return ""

    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(filename))
        os.makedirs(output_dir, exist_ok=True)

        # Convert Articles to dict for CSV export
        articles_data = []
        for article in articles:
            article_dict = asdict(article)

            # Convert authors list to a semicolon-separated string
            if article_dict.get("authors"):
                article_dict["authors"] = ";".join(article_dict["authors"])

            # Convert topics list to a semicolon-separated string
            if article_dict.get("topics") and isinstance(article_dict["topics"], list):
                article_dict["topics"] = ";".join(article_dict["topics"])

            articles_data.append(article_dict)

        # Determine fields to export
        if fields is None:
            # Default field order for better readability
            all_fields = {
                "search_term",
                "title",
                "authors",
                "publication_date",
                "journal",
                "volume",
                "issue",
                "pages",
                "doi",
                "abstract",
                "topics",
                "article_id",
                "issn",
                "language",
                "publisher",
                "is_open_access",
                "is_peer_reviewed",
                "citation_count",
                "reader_count",
                "detail_url",
            }

            # Add any fields that are in the data but not in all_fields
            for article in articles_data:
                all_fields.update(article.keys())

            export_fields = list(all_fields)
        else:
            export_fields = fields

        # Write CSV file
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=export_fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(articles_data)

        logger.info(f"Exported {len(articles)} articles to {filename}")
        return filename

    except Exception as e:
        logger.error(f"Error exporting articles: {e}", exc_info=True)
        return ""


def get_available_fields() -> List[Dict[str, str]]:
    """
    Get list of available fields for export.

    Returns:
        List of dictionaries with field information (name, description, default_enabled)
    """
    return [
        {"name": "title", "description": "Article title", "default_enabled": True},
        {"name": "authors", "description": "Article authors", "default_enabled": True},
        {"name": "publication_date", "description": "Publication date", "default_enabled": True},
        {"name": "journal", "description": "Journal name", "default_enabled": True},
        {"name": "doi", "description": "Digital Object Identifier", "default_enabled": True},
        {"name": "abstract", "description": "Article abstract", "default_enabled": True},
        {"name": "search_term", "description": "Search theme", "default_enabled": True},
        {"name": "topics", "description": "Article topics", "default_enabled": True},
        {"name": "citation_count", "description": "Citation count", "default_enabled": True},
        {"name": "is_open_access", "description": "Open access status", "default_enabled": True},
        {"name": "is_peer_reviewed", "description": "Peer review status", "default_enabled": True},
        {"name": "article_id", "description": "CAPES article ID", "default_enabled": False},
        {"name": "issn", "description": "Journal ISSN", "default_enabled": False},
        {"name": "volume", "description": "Journal volume", "default_enabled": False},
        {"name": "issue", "description": "Journal issue", "default_enabled": False},
        {"name": "pages", "description": "Page numbers", "default_enabled": False},
        {"name": "language", "description": "Article language", "default_enabled": False},
        {"name": "publisher", "description": "Publisher name", "default_enabled": False},
        {"name": "reader_count", "description": "Reader count", "default_enabled": False},
        {"name": "detail_url", "description": "Article detail URL", "default_enabled": False},
    ]
