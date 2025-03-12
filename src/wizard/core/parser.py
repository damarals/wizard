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

                    # Extract year
                    year_match = re.search(r"(\d{4})", pub_text)
                    if year_match:
                        article_data["year"] = year_match.group(1)

                    # Extract journal
                    journal_match = re.search(r"\|\s*(.+?)$", pub_text)
                    if journal_match:
                        article_data["journal"] = journal_match.group(1).strip()

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
            # Extract title
            title_elem = soup.select_one("h1.title")
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

            # Extract publisher
            publisher_elem = soup.select_one('b:-soup-contains("Editora")') or soup.select_one(
                'b:-soup-contains("Publisher")'
            )
            if publisher_elem and publisher_elem.parent:
                metadata["publisher"] = (
                    publisher_elem.parent.text.replace("Editora:", "")
                    .replace("Publisher:", "")
                    .strip()
                )

            # Check if open access
            open_access_elem = soup.select_one(".text-green-cool-vivid-50")
            metadata["is_open_access"] = bool(open_access_elem)

            # Check if peer-reviewed
            peer_reviewed_elem = soup.select_one(".text-violet-50")
            metadata["is_peer_reviewed"] = bool(peer_reviewed_elem)

            # Extract citation counts
            citation_elem = soup.select_one('.ppp-count:-soup-contains("Citation Indexes")')
            if citation_elem:
                citation_text = citation_elem.text.strip()
                try:
                    metadata["citation_count"] = int(re.search(r"\d+", citation_text).group())
                except (AttributeError, ValueError):
                    pass

            # Extract reader counts
            reader_elem = soup.select_one('.ppp-count:-soup-contains("Readers")')
            if reader_elem:
                reader_text = reader_elem.text.strip()
                try:
                    metadata["reader_count"] = int(re.search(r"\d+", reader_text).group())
                except (AttributeError, ValueError):
                    pass

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

            # Extract publication date and journal
            pub_info_elem = soup.select_one('.text-down-01:-soup-contains(")")')
            if pub_info_elem:
                pub_text = pub_info_elem.text.strip()
                year_match = re.search(r"(\d{4})", pub_text)
                if year_match:
                    metadata["publication_date"] = year_match.group(1)

                journal_match = re.search(r"\|\s*(.+?)\s*$", pub_text)
                if journal_match:
                    metadata["journal"] = journal_match.group(1).strip()

        except Exception as e:
            logger.error(f"Error parsing article detail: {e}")

        return metadata
