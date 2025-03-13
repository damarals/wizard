"""
CAPES Periodicals Portal Scraper

This module provides functionality to search the CAPES Periodicals Portal
and extract article metadata.
"""

import concurrent.futures
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import QObject, QThread, Signal

from wizard.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Article:
    """Represents metadata for a scientific article."""

    title: str
    authors: List[str]
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    abstract: Optional[str] = None
    search_term: str = ""  # This will store the theme
    article_id: Optional[str] = None  # ID in CAPES portal
    issn: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    detail_url: Optional[str] = None
    is_open_access: bool = False
    is_peer_reviewed: bool = False


class SearchWorker(QThread):
    """Worker thread for running searches without blocking the UI"""

    progress_updated = Signal(str, int)  # query_id, progress percentage
    search_completed = Signal(str, list)  # query_id, results (list of Articles)
    search_error = Signal(str, str)  # query_id, error message
    status_updated = Signal(str, str)  # query_id, status message

    def __init__(self, scraper, query_id, theme, search_query, advanced=True):
        super().__init__()
        self.scraper = scraper
        self.query_id = query_id
        self.theme = theme
        self.search_query = search_query
        self.advanced = advanced
        self.running = True

    def run(self):
        try:
            # Create search dictionary with theme as key and query as value
            search_dict = {self.theme: self.search_query}

            # Progress callback to emit signals
            def progress_callback(progress: int, status: str):
                if self.running:
                    self.progress_updated.emit(self.query_id, progress)
                    self.status_updated.emit(self.query_id, status)

            # Run the search
            self.status_updated.emit(self.query_id, "Starting search...")
            results = self.scraper.search(
                search_dict, advanced=self.advanced, callback=progress_callback
            )

            # Emit completed signal if still running
            if self.running:
                self.status_updated.emit(self.query_id, f"Found {len(results)} articles")
                self.search_completed.emit(self.query_id, results)

        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            if self.running:
                self.status_updated.emit(self.query_id, f"Error: {str(e)}")
                self.search_error.emit(self.query_id, str(e))

    def stop(self):
        """Stop the worker thread"""
        self.running = False
        # Emita um sinal final para indicar que a busca foi pausada
        self.status_updated.emit(self.query_id, "Busca pausada")


class SearchManager(QObject):
    """Manages multiple concurrent searches"""

    progress_updated = Signal(str, int)  # query_id, progress percentage
    search_completed = Signal(str, list)  # query_id, results (list of Articles)
    search_error = Signal(str, str)  # query_id, error message
    status_updated = Signal(str, str)  # query_id, status message

    def __init__(self, max_workers=3, request_delay=2.0, max_pages=None):
        super().__init__()
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.max_pages = max_pages

        # Create scraper
        self.scraper = ArticleScraper(
            max_workers=max_workers, request_delay=request_delay, max_pages=max_pages
        )

        # Track active workers
        self.workers = {}  # query_id -> SearchWorker

    def start_search(self, query_id, theme, query, advanced=True):
        """Start a search for the given query"""
        # Cancel existing search for this query_id if running
        self.cancel_search(query_id)

        # Create and start worker
        worker = SearchWorker(self.scraper, query_id, theme, query, advanced)

        # Connect signals
        worker.progress_updated.connect(self.progress_updated)
        worker.search_completed.connect(self.search_completed)
        worker.search_error.connect(self.search_error)
        worker.status_updated.connect(self.status_updated)

        # Store and start worker
        self.workers[query_id] = worker
        worker.start()

    def stop_search(self, query_id):
        """Stop a running search"""
        if query_id in self.workers:
            worker = self.workers[query_id]
            worker.stop()
            worker.wait()
            del self.workers[query_id]

    def cancel_search(self, query_id):
        """Cancel a running search"""
        if query_id in self.workers:
            worker = self.workers[query_id]
            worker.stop()
            # Aguarde o thread terminar antes de removê-lo
            worker.wait()
            del self.workers[query_id]

    def update_settings(self, max_workers=None, request_delay=None, max_pages=None):
        """Update scraper settings"""
        if max_workers is not None:
            self.max_workers = max_workers
            self.scraper.max_workers = max_workers

        if request_delay is not None:
            self.request_delay = request_delay
            self.scraper.request_delay = request_delay

        if max_pages is not None:
            self.max_pages = max_pages
            self.scraper.max_pages = max_pages


class ArticleScraper:
    """
    A class to scrape metadata from the CAPES Periodicals Portal.
    """

    BASE_URL = "https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html"
    DETAIL_URL_PATTERN = "https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=all&id={}"

    def __init__(self, max_workers=3, request_delay=2.0, max_pages=0):
        """
        Initialize the scraper.

        Args:
            max_workers: Maximum number of concurrent workers for parallel requests
            request_delay: Delay between requests in seconds
            max_pages: Maximum number of pages to scrape per search (0 for all)
        """
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.max_pages = max_pages

        # Create session
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
            }
        )

    def _construct_search_url(self, search_term: str, advanced: bool = False, page: int = 1) -> str:
        """
        Construct the search URL for a given search term.

        Args:
            search_term: The term to search for
            advanced: Whether to use advanced search format
            page: The page number to fetch (default: 1)

        Returns:
            The complete search URL
        """
        from urllib.parse import quote

        if advanced:
            # Format for advanced search with operators
            encoded_term = quote(f"all:contains({search_term})")
            return f"{self.BASE_URL}?q={encoded_term}&mode=advanced&source=all&page={page}"
        else:
            # Simple search
            encoded_term = quote(search_term)
            return f"{self.BASE_URL}?q={encoded_term}&page={page}"

    def _extract_doi(self, url: str) -> Optional[str]:
        """
        Extract DOI from a URL if present.

        Args:
            url: URL that might contain a DOI

        Returns:
            Extracted DOI or None if not found
        """
        doi_pattern = re.compile(
            r"(?:doi\.org\/|doi=|\/doi\/)(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)", re.IGNORECASE
        )
        match = doi_pattern.search(url)
        return match.group(1) if match else None

    def _extract_article_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract article ID from a CAPES portal URL.

        Args:
            url: URL of the article detail page

        Returns:
            Article ID or None if not found
        """
        id_pattern = re.compile(r"id=([A-Z0-9]+)")
        match = id_pattern.search(url)
        return match.group(1) if match else None

    def _get_total_pages(self, soup: BeautifulSoup) -> int:
        """
        Extract the total number of pages from the search results.

        Args:
            soup: BeautifulSoup object of the search results page

        Returns:
            Total number of pages (defaults to 1 if cannot determine)
        """
        try:
            total_span = soup.select_one("div.pagination-information span.total")
            if total_span and total_span.text.strip().isdigit():
                total_items = int(total_span.text.strip())
                per_page = 30  # Default to 30 items per page

                logger.info(f"Found total items from span: {total_items}, per page: {per_page}")
                return (total_items + per_page - 1) // per_page  # Ceiling division

            # No results
            logger.warning("No results found.")
            return 0

        except Exception as e:
            logger.warning(f"Error determining total pages: {e}")
            return 1  # Default to 1 page

    def scrape_article_detail(self, article_id: str) -> dict:
        """
        Scrape detailed information about an article from its dedicated page.

        Args:
            article_id: The CAPES ID of the article

        Returns:
            Dictionary with additional metadata
        """
        detail_url = self.DETAIL_URL_PATTERN.format(article_id)

        try:
            response = self.session.get(detail_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract additional metadata
            metadata = {}
            metadata["detail_url"] = detail_url

            # Extract abstract
            abstract_elem = soup.select_one("#item-resumo")
            if abstract_elem:
                metadata["abstract"] = abstract_elem.text.strip()

            # Extract ISSN
            issn_elem = soup.find(string=re.compile(r"ISSN", re.IGNORECASE))
            if issn_elem and issn_elem.parent and issn_elem.parent.find_next_sibling():
                metadata["issn"] = issn_elem.parent.find_next_sibling().text.strip()

            # Extract publication date (year)
            year_elem = soup.select_one("#item-ano")
            if year_elem:
                # Remove semicolon and other non-digit characters
                year_text = re.search(r"(\d{4})", year_elem.text)
                if year_text:
                    metadata["publication_date"] = year_text.group(1)

            # Extract volume, issue, language
            pub_info = soup.select_one("p.small.text-muted")
            if pub_info:
                text = pub_info.text

                # Extract volume
                volume_match = re.search(r"Volume:\s*([^;]+)", text)
                if volume_match:
                    metadata["volume"] = volume_match.group(1).strip()

                # Extract issue
                issue_match = re.search(r"Issue:\s*(\d+)", text)
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
                    doi = self._extract_doi(link_url)
                    if doi:
                        metadata["doi"] = doi
                        break

            # Journal and publisher are now extracted from the search results page in _extract_basic_article_info

            return metadata

        except requests.RequestException as e:
            logger.error(f"Request error fetching details for {article_id}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching details for {article_id}: {e}")
            return {}

    def get_all_article_listings(
        self,
        search_dict: Dict[str, str],
        advanced: bool = True,
        callback: Callable[[int, str], None] = None,
    ) -> Dict[str, List[Dict]]:
        """
        First phase: Get all article listings (from all pages) for each search term.

        Args:
            search_dict: Dictionary with theme as key and search query as value
            advanced: Whether to use advanced search syntax for all queries
            callback: Progress callback function (progress percentage, status message)

        Returns:
            Dictionary with theme as key and list of basic article info as value
        """
        all_listings = {}
        total_themes = len(search_dict)
        themes_processed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_theme = {}

            for theme, query in search_dict.items():
                future = executor.submit(
                    self._get_listings_for_term, query, theme, advanced, callback
                )
                future_to_theme[future] = theme

            for future in concurrent.futures.as_completed(future_to_theme):
                theme = future_to_theme[future]
                try:
                    listings = future.result()
                    all_listings[theme] = listings

                    themes_processed += 1
                    if callback:
                        progress = min(50, int((themes_processed / total_themes) * 50))
                        callback(
                            progress,
                            f"Collected {len(listings)} article listings for theme '{theme}'",
                        )

                    logger.info(f"Collected {len(listings)} article listings for theme '{theme}'")
                except Exception as e:
                    logger.error(f"Error getting listings for theme '{theme}': {e}")
                    themes_processed += 1

        return all_listings

    def _get_listings_for_term(
        self,
        search_term: str,
        theme: str,
        is_advanced: bool,
        callback: Callable[[int, str], None] = None,
    ) -> List[Dict]:
        """Get all article listings for a single search term across all pages."""
        listings = []
        url = self._construct_search_url(search_term, advanced=is_advanced, page=1)
        logger.info(f"Fetching listings for theme '{theme}' with query: {search_term}")

        if callback:
            callback(0, f"Searching for '{theme}'...")

        try:
            # Get the first page
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Determine total number of pages
            total_pages = self._get_total_pages(soup)
            logger.info(f"Found {total_pages} pages of results for theme '{theme}'")

            if callback:
                callback(5, f"Found {total_pages} pages for '{theme}'")

            # Apply MAX_PAGES limit if set
            if self.max_pages > 0:
                total_pages = min(total_pages, self.max_pages)
                logger.info(f"Limiting to {total_pages} pages due to MAX_PAGES setting")

            # Process the first page
            page_listings = self._extract_basic_article_info(soup, theme, search_term)
            listings.extend(page_listings)

            if callback:
                callback(10, f"Processing page 1/{total_pages} for '{theme}'")

            # Process remaining pages if any
            for page_num in range(2, total_pages + 1):
                logger.info(f"Fetching page {page_num}/{total_pages} for theme '{theme}'")

                if callback:
                    progress = 10 + int(40 * (page_num - 1) / total_pages)
                    callback(progress, f"Processing page {page_num}/{total_pages} for '{theme}'")

                # Add delay between page requests
                time.sleep(self.request_delay)

                # Construct URL for the current page
                page_url = self._construct_search_url(
                    search_term, advanced=is_advanced, page=page_num
                )

                try:
                    page_response = self.session.get(page_url, timeout=30)
                    page_response.raise_for_status()

                    page_soup = BeautifulSoup(page_response.text, "html.parser")
                    page_listings = self._extract_basic_article_info(page_soup, theme, search_term)

                    listings.extend(page_listings)

                except requests.RequestException as e:
                    logger.error(f"Error fetching page {page_num} for theme '{theme}': {e}")
                    continue
                except Exception as e:
                    logger.error(
                        f"Unexpected error processing page {page_num} for theme '{theme}': {e}"
                    )
                    continue

            return listings

        except Exception as e:
            logger.error(f"Error fetching listings for theme '{theme}': {e}")
            return []

    def _extract_basic_article_info(
        self, soup: BeautifulSoup, theme: str, search_term: str
    ) -> List[Dict]:
        """Extract basic article information from search results page."""
        listings = []
        article_sections = soup.select("#resultados .result-busca")

        for section in article_sections:
            try:
                # Extract title
                title_elem = section.select_one(".titulo-busca")
                title = title_elem.text.strip() if title_elem else "No title found"

                # Get article ID and detail URL
                article_id = None
                detail_url = None
                if title_elem and title_elem.get("href"):
                    detail_url = title_elem.get("href")
                    if not detail_url.startswith("http"):
                        detail_url = f"https://www.periodicos.capes.gov.br{detail_url}"
                    article_id = self._extract_article_id_from_url(detail_url)

                # Extract publisher and journal from text-down-01 paragraph
                publisher = None
                journal = None
                journal_paragraphs = section.select("p.text-down-01")
                for p in journal_paragraphs:
                    if "| " in p.text:
                        # Format is typically: "Year - Publisher | Journal"
                        parts = p.text.split("|")
                        if len(parts) >= 2:
                            # Get journal (right side of |)
                            journal = parts[1].strip()

                            # Get publisher (left side of |, after the year)
                            left_side = parts[0]
                            if "-" in left_side:
                                publisher_part = left_side.split("-", 1)[1]
                                publisher = publisher_part.strip()
                        break

                # Only store basic info needed for the second phase
                listings.append(
                    {
                        "title": title,
                        "article_id": article_id,
                        "detail_url": detail_url,
                        "theme": theme,
                        "search_term": search_term,
                        "journal": journal,
                        "publisher": publisher,
                    }
                )

            except Exception as e:
                logger.error(f"Error extracting basic info for an article: {e}")

        return listings

    def fetch_article_details(
        self, article_listings: Dict[str, List[Dict]], callback: Callable[[int, str], None] = None
    ) -> List[Article]:
        """
        Second phase: Fetch detailed metadata for all articles in the listings.

        Args:
            article_listings: Dictionary with theme as key and list of basic article info as value
            callback: Progress callback function (progress percentage, status message)

        Returns:
            List of Article objects with complete metadata
        """
        # Flatten the listings from all themes into a single list
        all_listings = []
        for theme, listings in article_listings.items():
            all_listings.extend(listings)

        total_articles = len(all_listings)
        logger.info(f"Starting to fetch details for {total_articles} articles")

        if callback:
            callback(50, f"Fetching details for {total_articles} articles")

        # Create a progress counter
        processed_count = 0
        articles_with_details = 0

        # Function to process a single article
        def process_article(listing):
            nonlocal processed_count, articles_with_details

            try:
                article_id = listing.get("article_id")
                if not article_id:
                    logger.warning(f"Missing article ID for {listing.get('title')}")
                    return None

                # Fetch detailed information
                details = self.scrape_article_detail(article_id)

                # Update progress
                processed_count += 1
                if details:
                    articles_with_details += 1

                if callback and processed_count % 5 == 0:
                    progress = 50 + int((processed_count / total_articles) * 50)
                    callback(progress, f"Processed {processed_count}/{total_articles} articles")

                # Create basic Article object
                article = Article(
                    title=listing.get("title", "Unknown Title"),
                    authors=details.get("authors", []),
                    search_term=listing.get("theme", listing.get("search_term", "")),
                    article_id=article_id,
                    detail_url=listing.get("detail_url"),
                    journal=listing.get("journal"),
                    publisher=listing.get("publisher"),
                )

                # Update article with remaining detailed information
                for key, value in details.items():
                    if value and hasattr(article, key) and key != "authors":
                        setattr(article, key, value)

                return article

            except Exception as e:
                logger.error(f"Error processing article {listing.get('article_id')}: {e}")
                return None

        # Process articles in parallel
        articles = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for listing in all_listings:
                futures.append(executor.submit(process_article, listing))

            for future in concurrent.futures.as_completed(futures):
                try:
                    article = future.result()
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Error processing article: {e}")

            if callback:
                callback(100, f"Completed processing {len(articles)} articles")

        logger.info(
            f"Completed fetching details for {len(articles)} articles (out of {total_articles})"
        )
        return articles

    def search(
        self,
        search_dict: Dict[str, str],
        advanced: bool = True,
        callback: Callable[[int, str], None] = None,
    ) -> List[Article]:
        """
        Execute the complete two-phase scraping workflow.

        Args:
            search_dict: Dictionary with theme as key and search query as value
            advanced: Whether to use advanced search syntax for all queries
            callback: Progress callback function (progress percentage, status message)

        Returns:
            List of Article objects with complete metadata
        """
        # Phase 1: Get all article listings
        logger.info("PHASE 1: Collecting all article listings")
        if callback:
            callback(0, "PHASE 1: Collecting article listings")

        article_listings = self.get_all_article_listings(search_dict, advanced, callback)

        # Count total articles
        total_listings = sum(len(listings) for listings in article_listings.values())
        logger.info(
            f"PHASE 1 COMPLETE: Found {total_listings} articles across {len(article_listings)} themes"
        )

        if callback:
            callback(50, f"Found {total_listings} articles. Starting phase 2...")

        # Phase 2: Fetch detailed metadata
        logger.info("PHASE 2: Fetching detailed metadata for each article")
        articles = self.fetch_article_details(article_listings, callback)
        logger.info(f"PHASE 2 COMPLETE: Successfully processed {len(articles)} articles")

        if callback:
            callback(100, f"Completed: Found {len(articles)} articles")

        return articles
