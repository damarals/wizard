"""
Main application window for CAPES Research Wizard.
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, 
    QPushButton, QHBoxLayout, QLabel, QProgressBar, QMessageBox,
    QStatusBar
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QAction

from .widgets.query_table import QueryTableWidget
from .widgets.papers_table import PapersTableWidget
from .dialogs.add_query import AddQueryDialog
from .dialogs.settings import SettingsDialog
from .dialogs.export import ExportDialog
from ..core.scraper import SearchManager
from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAPES Research Wizard")
        self.resize(1200, 800)
        
        # Load configuration
        self.config = Config()
        
        # Initialize search manager
        self.search_manager = SearchManager(
            max_workers=self.config.get("max_workers", 3),
            request_delay=self.config.get("request_delay", 2.0),
            max_pages=self.config.get("max_pages", 5)
        )
        
        # Connect signals from search manager
        self.search_manager.progress_updated.connect(self.update_query_progress)
        self.search_manager.search_completed.connect(self.search_completed)
        self.search_manager.search_error.connect(self.search_error)
        self.search_manager.status_updated.connect(self.update_status)
        
        # Set up UI components
        self.setup_ui()
        
        logger.info("Application started")
    
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create toolbar
        self.setup_toolbar()
        
        # Create splitter for main sections
        self.splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(self.splitter)
        
        # Add query table (top section)
        self.query_widget = QWidget()
        query_layout = QVBoxLayout(self.query_widget)
        query_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header for queries section
        queries_header = QWidget()
        queries_header_layout = QHBoxLayout(queries_header)
        queries_header_layout.setContentsMargins(0, 0, 0, 5)
        
        queries_title = QLabel("Search Queries")
        queries_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        queries_header_layout.addWidget(queries_title)
        
        queries_header_layout.addStretch()
        
        add_query_btn = QPushButton("Add Query")
        add_query_btn.setIcon(QIcon.fromTheme("list-add"))
        add_query_btn.clicked.connect(self.show_add_dialog)
        queries_header_layout.addWidget(add_query_btn)
        
        query_layout.addWidget(queries_header)
        
        # Query table
        self.query_table = QueryTableWidget()
        self.query_table.start_search.connect(self.start_search)
        self.query_table.pause_search.connect(self.pause_search)
        self.query_table.delete_query.connect(self.delete_query)
        query_layout.addWidget(self.query_table, 1)
        
        # Overall progress section
        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(5, 5, 5, 5)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar, 1)
        
        self.progress_percent = QLabel("0%")
        self.progress_percent.setMinimumWidth(40)
        progress_layout.addWidget(self.progress_percent)
        
        query_layout.addWidget(progress_widget)
        
        # Add papers table (bottom section)
        self.papers_widget = QWidget()
        papers_layout = QVBoxLayout(self.papers_widget)
        papers_layout.setContentsMargins(0, 0, 0, 0)
        
        # Papers count and export button
        papers_header = QWidget()
        papers_header_layout = QHBoxLayout(papers_header)
        papers_header_layout.setContentsMargins(0, 0, 0, 5)
        
        papers_title = QLabel("Articles")
        papers_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        papers_header_layout.addWidget(papers_title)
        
        self.papers_count = QLabel("0 papers found")
        papers_header_layout.addWidget(self.papers_count)
        
        papers_header_layout.addStretch()
        
        self.export_button = QPushButton("Export Papers")
        self.export_button.setIcon(QIcon.fromTheme("document-save"))
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.show_export_dialog)
        papers_header_layout.addWidget(self.export_button)
        
        papers_layout.addWidget(papers_header)
        
        # Papers table
        self.papers_table = PapersTableWidget()
        papers_layout.addWidget(self.papers_table, 1)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.query_widget)
        self.splitter.addWidget(self.papers_widget)
        
        # Set initial sizes (65% / 35%)
        self.splitter.setSizes([650, 350])
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def setup_toolbar(self):
        # Add search query button
        add_action = QAction(QIcon.fromTheme("list-add"), "Add Search Query", self)
        add_action.triggered.connect(self.show_add_dialog)
        add_action.setStatusTip("Add a new search query")
        
        # Settings button
        settings_action = QAction(QIcon.fromTheme("preferences-system"), "Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        settings_action.setStatusTip("Configure application settings")
        
        # Export button
        export_action = QAction(QIcon.fromTheme("document-save"), "Export Results", self)
        export_action.triggered.connect(self.show_export_dialog)
        export_action.setStatusTip("Export articles to CSV")
        export_action.setEnabled(False)
        self.export_action = export_action
        
        # Add to toolbar
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.addAction(add_action)
        toolbar.addAction(settings_action)
        toolbar.addSeparator()
        toolbar.addAction(export_action)
    
    def show_add_dialog(self):
        dialog = AddQueryDialog(self)
        if dialog.exec():
            theme, query, advanced = dialog.get_query_data()
            self.query_table.add_query(theme, query, advanced)
            self.status_bar.showMessage(f"Added query: {theme}")
    
    def show_settings_dialog(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Update settings in search manager
            self.search_manager.update_settings(
                max_workers=self.config.get("max_workers"),
                request_delay=self.config.get("request_delay"),
                max_pages=self.config.get("max_pages")
            )
            self.status_bar.showMessage("Settings updated")
    
    def show_export_dialog(self):
        if self.papers_table.rowCount() == 0:
            QMessageBox.information(self, "No Articles", "There are no articles to export.")
            return
            
        dialog = ExportDialog(self.config, self)
        if dialog.exec():
            filename, fields = dialog.get_export_data()
            try:
                from ..core.exporter import export_articles
                articles = self.papers_table.get_articles()
                exported_file = export_articles(articles, filename, fields)
                
                if exported_file:
                    QMessageBox.information(
                        self, "Export Complete", 
                        f"Successfully exported {len(articles)} articles to {exported_file}"
                    )
                    self.status_bar.showMessage(f"Exported {len(articles)} articles to {exported_file}")
                else:
                    QMessageBox.warning(
                        self, "Export Warning", 
                        "No file was created. Check the logs for details."
                    )
            except Exception as e:
                logger.error(f"Export error: {str(e)}", exc_info=True)
                QMessageBox.critical(
                    self, "Export Error", 
                    f"Failed to export articles: {str(e)}"
                )
    
    @Slot(str, int)
    def update_query_progress(self, query_id, progress):
        # Update progress for specific query
        self.query_table.update_progress(query_id, progress)
        
        # Update overall progress
        overall = self.query_table.calculate_overall_progress()
        self.progress_bar.setValue(overall)
        self.progress_percent.setText(f"{overall}%")
    
    @Slot(str, str)
    def update_status(self, query_id, status_message):
        # Update status label
        self.status_label.setText(status_message)
        self.status_bar.showMessage(status_message)
    
    @Slot(str, list)
    def search_completed(self, query_id, articles):
        # Update query status
        self.query_table.set_completed(query_id)
        
        # Add articles to papers table
        self.papers_table.add_articles(articles)
        
        # Update papers count
        count = self.papers_table.rowCount()
        self.papers_count.setText(f"{count} articles found")
        
        # Enable export button and action if we have results
        self.export_button.setEnabled(count > 0)
        self.export_action.setEnabled(count > 0)
        
        # Update status
        self.status_bar.showMessage(f"Search completed. Found {len(articles)} articles.")
    
    @Slot(str, str)
    def search_error(self, query_id, error_message):
        # Update query status
        self.query_table.set_error(query_id, error_message)
        
        # Show error message
        QMessageBox.warning(
            self, "Search Error", 
            f"Error in search query: {error_message}"
        )
        
        # Update status
        self.status_bar.showMessage(f"Search error: {error_message}")
    
    def start_search(self, query_id):
        query_data = self.query_table.get_query(query_id)
        if query_data:
            # Update UI
            self.query_table.set_running(query_id)
            
            # Start the search
            self.search_manager.start_search(
                query_id=query_id,
                theme=query_data["theme"],
                query=query_data["query"],
                advanced=query_data["advanced"]
            )
            
            # Update status
            self.status_bar.showMessage(f"Started search for: {query_data['theme']}")
    
    def pause_search(self, query_id):
        self.search_manager.pause_search(query_id)
        self.query_table.set_paused(query_id)
        
        # Update status
        query_data = self.query_table.get_query(query_id)
        if query_data:
            self.status_bar.showMessage(f"Paused search for: {query_data['theme']}")
    
    def delete_query(self, query_id):
        # If search is running, cancel it first
        self.search_manager.cancel_search(query_id)
        
        # Get query data before removal for status message
        query_data = self.query_table.get_query(query_id)
        theme = query_data["theme"] if query_data else "query"
        
        # Remove from UI
        self.query_table.remove_query(query_id)
        
        # Update progress
        self.update_query_progress("", 0)
        
        # Update status
        self.status_bar.showMessage(f"Deleted search query: {theme}")
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Cancel all running searches
        active_queries = self.query_table.get_active_queries()
        for query_id in active_queries:
            self.search_manager.cancel_search(query_id)
        
        # Save window state and settings
        self.config.set("window_width", self.width())
        self.config.set("window_height", self.height())
        self.config.set("splitter_sizes", self.splitter.sizes())
        self.config.save()
        
        logger.info("Application closed")
        event.accept()


def main():
    """Run the application"""
    import sys
    app = QApplication(sys.argv)
    
    # Set application style and icon
    app.setStyle("Fusion")
    app.setApplicationName("CAPES Research Wizard")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()