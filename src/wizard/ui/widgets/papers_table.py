"""
Table widget for displaying article results.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
)

from ...utils.logger import get_logger

logger = get_logger(__name__)


class PapersTableWidget(QTableWidget):
    """Table for displaying article results"""

    # Column indices
    COL_TITLE = 0
    COL_AUTHORS = 1
    COL_YEAR = 2
    COL_JOURNAL = 3
    COL_DOI = 4

    def __init__(self, parent=None):
        super().__init__(parent)

        # Store article data
        self.articles = []  # List of Article objects

        # Set up table
        self.setup_table()

    def setup_table(self):
        # Set columns
        self.setColumnCount(5)
        header_labels = ["Título", "Autores", "Ano", "Periódico", "DOI"]
        self.setHorizontalHeaderLabels(header_labels)

        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(self.COL_TITLE, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_AUTHORS, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_YEAR, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_JOURNAL, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_DOI, QHeaderView.ResizeToContents)

        # Set selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Hide vertical header (row numbers)
        self.verticalHeader().setVisible(False)

        # No edit triggers
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Allow sorting
        self.setSortingEnabled(True)

        # Set alternate row colors
        self.setAlternatingRowColors(True)

        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def add_article(self, article):
        """Add a single article to the table"""
        # Check if article already exists (by DOI or title + authors)
        if self.article_exists(article):
            return

        # Add article to stored data
        self.articles.append(article)

        # Add row to table
        row = self.rowCount()
        self.insertRow(row)

        # Set title cell
        title_item = QTableWidgetItem(article.title)
        if article.abstract:
            title_item.setToolTip(article.abstract)
        self.setItem(row, self.COL_TITLE, title_item)

        # Set authors cell
        authors_text = "; ".join(article.authors) if article.authors else ""
        authors_item = QTableWidgetItem(authors_text)
        self.setItem(row, self.COL_AUTHORS, authors_item)

        # Set year cell
        year = article.publication_date or ""
        year_item = QTableWidgetItem(year)
        year_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, self.COL_YEAR, year_item)

        # Set journal cell
        journal = article.journal or ""
        journal_item = QTableWidgetItem(journal)
        self.setItem(row, self.COL_JOURNAL, journal_item)

        # Set DOI cell
        doi = article.doi or ""
        doi_item = QTableWidgetItem(doi)
        self.setItem(row, self.COL_DOI, doi_item)

    def add_articles(self, articles):
        """Add multiple articles to the table"""
        # Temporarily disable sorting for faster insertion
        self.setSortingEnabled(False)

        for article in articles:
            self.add_article(article)

        # Re-enable sorting
        self.setSortingEnabled(True)

    def article_exists(self, article):
        """Check if an article already exists in the table"""
        # First check by DOI if available
        if article.doi:
            for existing in self.articles:
                if existing.doi and existing.doi == article.doi:
                    return True

        # Fallback to title + first author check
        title_lower = article.title.lower()
        first_author = article.authors[0] if article.authors else None

        for existing in self.articles:
            if existing.title.lower() == title_lower:
                if not first_author or not existing.authors:
                    return True
                if existing.authors[0] == first_author:
                    return True

        return False

    def get_articles(self):
        """Get the list of articles"""
        return self.articles

    def clear_articles(self):
        """Clear all articles from the table"""
        self.articles = []
        self.setRowCount(0)

    def get_selected_articles(self):
        """Get the selected articles"""
        selected_rows = set(index.row() for index in self.selectedIndexes())
        return [self.articles[row] for row in selected_rows if row < len(self.articles)]

    def show_context_menu(self, position):
        """Show context menu for table"""
        menu = QMenu(self)

        # Get selected articles
        selected_articles = self.get_selected_articles()

        if selected_articles:
            # Copy options
            copy_menu = menu.addMenu("Copiar")

            copy_title = copy_menu.addAction("Título")
            copy_title.triggered.connect(lambda: self.copy_to_clipboard(selected_articles, "title"))

            copy_authors = copy_menu.addAction("Autores")
            copy_authors.triggered.connect(
                lambda: self.copy_to_clipboard(selected_articles, "authors")
            )

            copy_doi = copy_menu.addAction("DOI")
            copy_doi.triggered.connect(lambda: self.copy_to_clipboard(selected_articles, "doi"))

            # Add separator
            menu.addSeparator()

        # Select all action
        select_all = menu.addAction("Selecionar Todos")
        select_all.triggered.connect(self.selectAll)

        # Clear selection action
        clear_selection = menu.addAction("Limpar Seleção")
        clear_selection.triggered.connect(self.clearSelection)

        # Show menu at position
        menu.exec(self.mapToGlobal(position))

    def copy_to_clipboard(self, articles, field):
        """Copy field from articles to clipboard"""
        if not articles:
            return

        from PySide6.QtGui import QGuiApplication

        clipboard = QGuiApplication.clipboard()

        # Build text to copy
        lines = []
        for article in articles:
            if field == "title":
                lines.append(article.title)
            elif field == "authors":
                lines.append("; ".join(article.authors) if article.authors else "")
            elif field == "doi":
                lines.append(article.doi or "")

        # Set clipboard text
        clipboard.setText("\n".join(lines))
