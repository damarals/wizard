"""
HTML Parser for CAPES Periodicals Portal

This module provides functionality to parse HTML content from the CAPES Periodicals Portal,
extracting article metadata from search results and detail pages.
"""

import re
from typing import Any, Dict

from bs4 import BeautifulSoup

from wizard.utils.logger import get_logger

logger = get_logger(__name__)


class CAPESParser:
    """Parser for CAPES Periodicals Portal HTML content."""

    @staticmethod
    def parse_search_results(html_content: str) -> Dict[str, Any]:
        """
        Parse search results page to extract article listings and pagination info.

        Args:
            html_content: HTML content of the search results page

        Returns:
            Dictionary with parsed data including article listings and pagination info
        """
        soup = BeautifulSoup(html_content, "html.parser")
        result = {
            "articles": [],
            "pagination": {"current_page": 1, "total_pages": 1, "total_items": 0},
        }

        # Extract pagination info
        try:
            pagination_nav = soup.select_one("nav.br-pagination")
            if pagination_nav:
                total_items_attr = pagination_nav.get("data-total")
                per_page_attr = pagination_nav.get("data-per-page")
                current_page_attr = pagination_nav.get("data-current")

                if total_items_attr:
                    result["pagination"]["total_items"] = int(total_items_attr)

                if per_page_attr and total_items_attr:
                    per_page = int(per_page_attr)
                    total_items = int(total_items_attr)
                    if per_page > 0:
                        result["pagination"]["total_pages"] = (
                            total_items + per_page - 1
                        ) // per_page

                if current_page_attr:
                    result["pagination"]["current_page"] = int(current_page_attr)
        except Exception as e:
            logger.warning(f"Error parsing pagination info: {e}")

        # Extract article listings
        article_sections = soup.select("#resultados .result-busca")
        for section in article_sections:
            try:
                article_data = {}

                # Extract title and URL
                title_elem = section.select_one(".titulo-busca")
                if title_elem:
                    article_data["title"] = title_elem.text.strip()
                    url = title_elem.get("href", "")
                    if url:
                        if not url.startswith("http"):
                            url = f"https://www.periodicos.capes.gov.br{url}"
                        article_data["url"] = url

                        # Extract article ID from URL
                        id_match = re.search(r"id=([A-Z0-9]+)", url)
                        if id_match:
                            article_data["article_id"] = id_match.group(1)

                # Extract authors
                authors_elem = section.select_one(".autores-busca")
                if authors_elem:
                    article_data["authors"] = [a.strip() for a in authors_elem.text.split(";")]

                # Extract publication info
                pub_elem = section.select_one(".texto-vertical-busca")
                if pub_elem:
                    pub_text = pub_elem.text.strip()
                    pub_info = CAPESParser.extract_publication_info(pub_text)

                    if pub_info["publication_date"]:
                        article_data["publication_date"] = pub_info["publication_date"]

                    if pub_info["journal"]:
                        article_data["journal"] = pub_info["journal"]

                    if pub_info["publisher"]:
                        article_data["publisher"] = pub_info["publisher"]

                # Add to results if we have title and id
                if "title" in article_data and "article_id" in article_data:
                    result["articles"].append(article_data)

            except Exception as e:
                logger.error(f"Error parsing article listing: {e}")

        return result

    @staticmethod
    def parse_article_detail(html_content: str) -> Dict[str, Any]:
        """
        Parse article detail page to extract full metadata.

        Args:
            html_content: HTML content of the article detail page

        Returns:
            Dictionary with parsed article metadata
        """
        soup = BeautifulSoup(html_content, "html.parser")
        metadata = {}

        try:
            # Extract title - try multiple selectors for better robustness
            title_elem = soup.select_one("h1.title")  # Original selector from test
            if not title_elem:
                title_elem = soup.select_one("h2#item-titulo")  # Real site selector
            if title_elem:
                metadata["title"] = title_elem.text.strip()

            # Extract abstract
            abstract_elem = soup.select_one("#item-resumo")
            if abstract_elem:
                metadata["abstract"] = abstract_elem.text.strip()

            # Extract ISSN
            issn_elem = soup.find(string=re.compile(r"ISSN", re.IGNORECASE))
            if issn_elem and issn_elem.parent and issn_elem.parent.find_next_sibling():
                metadata["issn"] = issn_elem.parent.find_next_sibling().text.strip()

            # Extract volume, issue, language
            pub_info = soup.select_one("p.small.text-muted")
            if pub_info:
                text = pub_info.text

                # Extract volume
                volume_match = re.search(r"Volume:\s*([^;]+)", text)
                if volume_match:
                    metadata["volume"] = volume_match.group(1).strip()

                # Extract issue
                issue_match = re.search(r"Issue:\s*([^;]+)", text)
                if issue_match:
                    metadata["issue"] = issue_match.group(1).strip()

                # Extract language
                lang_match = re.search(r"Linguagem:\s*([^;]+)", text)
                if lang_match:
                    metadata["language"] = lang_match.group(1).strip()

            # Extract topics
            topics_elem = soup.find(string=re.compile(r"Tópico\(s\)", re.IGNORECASE))
            if topics_elem and topics_elem.parent and topics_elem.parent.find_next_sibling():
                topics_text = topics_elem.parent.find_next_sibling().text.strip()
                metadata["topics"] = [topic.strip() for topic in topics_text.split(",")]

            # Extract publisher, publication date, and journal from text-down-01
            pub_info_elem = soup.select_one(".text-down-01")
            if pub_info_elem:
                pub_text = pub_info_elem.text.strip()
                pub_info = CAPESParser.extract_publication_info(pub_text)

                if pub_info["publication_date"]:
                    metadata["publication_date"] = pub_info["publication_date"]

                if pub_info["journal"]:
                    metadata["journal"] = pub_info["journal"]

                if pub_info["publisher"]:
                    metadata["publisher"] = pub_info["publisher"]

            # Check if open access
            open_access_elem = soup.select_one(".text-green-cool-vivid-50")
            metadata["is_open_access"] = bool(open_access_elem)

            # Check if peer-reviewed
            peer_reviewed_elem = soup.select_one(".text-violet-50")
            metadata["is_peer_reviewed"] = bool(peer_reviewed_elem)

            # Extract authors
            authors = []
            author_elements = soup.select(".view-autor")
            for author_elem in author_elements:
                if author_elem.text.strip():
                    authors.append(author_elem.text.strip())
            if authors:
                metadata["authors"] = authors

            # Extract DOI from links
            link_elements = soup.select('a[href^="http"]')
            for link_elem in link_elements:
                link_url = link_elem.get("href", "")
                if link_url:
                    doi_match = re.search(
                        r"(?:doi\.org\/|doi=|\/doi\/)(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)",
                        link_url,
                        re.IGNORECASE,
                    )
                    if doi_match:
                        metadata["doi"] = doi_match.group(1)
                        break

        except Exception as e:
            logger.error(f"Error parsing article detail: {e}")

        return metadata

    @staticmethod
    def extract_publication_info(text):
        """
        Extract publication date, publisher, and journal from text-down-01 format text.

        Args:
            text: String in format "YEAR - [PUBLISHER] | JOURNAL" or "YEAR | JOURNAL"

        Returns:
            Dictionary with publication_date, publisher, and journal
        """
        info = {"publication_date": None, "publisher": None, "journal": None}

        if not text:
            return info

        # Strip any extra whitespace and join broken text
        text = " ".join(text.split())

        # First try to extract year from the beginning (simpler approach)
        year_match = re.match(r"^(\d{4})", text)
        if year_match:
            info["publication_date"] = year_match.group(1)

        # Check if we have the "YEAR - [PUBLISHER] | JOURNAL" format (article detail)
        if " - " in text:
            parts = text.split(" - ", 1)

            # If we have a second part after " - ", process it for publisher/journal
            if len(parts) > 1 and parts[1].strip():
                pub_journal = parts[1].strip()

                # Split by " | " to separate publisher and journal
                if " | " in pub_journal:
                    pub_parts = pub_journal.split(" | ", 1)
                    info["publisher"] = pub_parts[0].strip()
                    info["journal"] = pub_parts[1].strip()
                # Just journal with the "| Journal" format
                elif pub_journal.startswith("|"):
                    info["journal"] = pub_journal[1:].strip()
                # Just publisher
                else:
                    info["publisher"] = pub_journal

        # Check if we have the "YEAR | JOURNAL" format (search results)
        elif "|" in text:
            parts = text.split("|", 1)
            if len(parts) > 1:
                info["journal"] = parts[1].strip()

        return info
