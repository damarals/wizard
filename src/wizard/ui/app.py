"""
Main application window for Wizard.
"""

import os
import sys

from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from wizard.core.scraper import SearchManager
from wizard.ui.dialogs.add_query import AddQueryDialog
from wizard.ui.dialogs.edit_query import EditQueryDialog
from wizard.ui.dialogs.export import ExportDialog
from wizard.ui.dialogs.export_settings import ExportSettingsDialog
from wizard.ui.dialogs.search_settings import SearchSettingsDialog
from wizard.ui.icons import get_icon
from wizard.ui.theme import get_additional_stylesheet, setup_theme
from wizard.ui.widgets.papers_table import PapersTableWidget
from wizard.ui.widgets.query_table import QueryTableWidget
from wizard.utils.config import Config
from wizard.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wizard")
        self.resize(1200, 800)

        # Load configuration
        self.config = Config()

        # Apply theme
        theme_mode = self.config.get("theme_mode", "light")
        self.stylesheet = setup_theme(theme_mode)
        self.setStyleSheet(self.stylesheet + get_additional_stylesheet())

        if getattr(sys, "frozen", False):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "icon.ico"
            )

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Initialize search manager
        self.search_manager = SearchManager(
            max_workers=self.config.get("max_workers", 5),
            request_delay=self.config.get("request_delay", 1.5),
            max_pages=self.config.get("max_pages", 0),
        )

        # Connect signals from search manager
        self.search_manager.progress_updated.connect(self.update_query_progress)
        self.search_manager.search_completed.connect(self.search_completed)
        self.search_manager.search_error.connect(self.search_error)
        self.search_manager.status_updated.connect(self.update_status)

        # Set up UI components
        self.setup_ui()

        logger.info("Aplicação iniciada")

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create splitter for main sections
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.setHandleWidth(2)
        self.splitter.setChildrenCollapsible(False)
        main_layout.addWidget(self.splitter)

        # Add query table (top section)
        self.query_widget = QWidget()
        query_layout = QVBoxLayout(self.query_widget)
        query_layout.setContentsMargins(0, 0, 0, 0)

        # Header for queries section
        queries_header = QWidget()
        queries_header_layout = QHBoxLayout(queries_header)
        queries_header_layout.setContentsMargins(0, 0, 0, 5)

        queries_title = QLabel("Consultas de Pesquisa")
        queries_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        queries_header_layout.addWidget(queries_title)

        queries_header_layout.addStretch()

        # Add Query button
        add_query_btn = QPushButton("Adicionar Consulta")
        add_query_btn.setIcon(get_icon("PLUS", color="#FFFFFF"))
        add_query_btn.clicked.connect(self.show_add_dialog)
        add_query_btn.setProperty("class", "primary-action")
        queries_header_layout.addWidget(add_query_btn)

        # Search Settings button
        search_settings_btn = QPushButton()
        search_settings_btn.setIcon(get_icon("SETTINGS"))
        search_settings_btn.setToolTip("Configurações de Busca")
        search_settings_btn.clicked.connect(self.show_search_settings_dialog)
        search_settings_btn.setProperty("class", "icon-button")
        search_settings_btn.setFixedSize(QSize(30, 30))
        queries_header_layout.addWidget(search_settings_btn)

        query_layout.addWidget(queries_header)

        # Query table
        self.query_table = QueryTableWidget()
        self.query_table.start_search.connect(self.start_search)
        self.query_table.pause_search.connect(self.pause_search)
        self.query_table.delete_query.connect(self.delete_query)
        self.query_table.edit_query.connect(self.show_edit_dialog)
        query_layout.addWidget(self.query_table, 1)

        # Add papers table (bottom section)
        self.papers_widget = QWidget()
        papers_layout = QVBoxLayout(self.papers_widget)
        papers_layout.setContentsMargins(0, 0, 0, 0)

        # Papers count and export button
        papers_header = QWidget()
        papers_header_layout = QHBoxLayout(papers_header)
        papers_header_layout.setContentsMargins(0, 10, 0, 5)

        papers_title = QLabel("Artigos")
        papers_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        papers_header_layout.addWidget(papers_title)

        self.papers_count = QLabel("0 artigos encontrados")
        papers_header_layout.addWidget(self.papers_count)

        papers_header_layout.addStretch()

        # Export Papers button
        self.export_button = QPushButton("Exportar Artigos")
        self.export_button.setIcon(get_icon("DEVICE_FLOPPY", color="#FFFFFF"))  # Use white icon
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.show_export_dialog)
        self.export_button.setProperty("class", "primary-action")
        papers_header_layout.addWidget(self.export_button)

        # Export Settings button
        export_settings_btn = QPushButton()
        export_settings_btn.setIcon(get_icon("SETTINGS"))
        export_settings_btn.setToolTip("Configurações de Exportação")
        export_settings_btn.clicked.connect(self.show_export_settings_dialog)
        export_settings_btn.setFixedSize(QSize(30, 30))
        export_settings_btn.setProperty("class", "icon-button")
        papers_header_layout.addWidget(export_settings_btn)

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
        self.status_bar.showMessage("Pronto")

    def show_add_dialog(self):
        dialog = AddQueryDialog(self)
        if dialog.exec():
            theme, query, advanced = dialog.get_query_data()
            self.query_table.add_query(theme, query, advanced)
            self.status_bar.showMessage(f"Consulta adicionada: {theme}")

    def show_edit_dialog(self, query_id):
        # Get current query data
        query_data = self.query_table.get_query(query_id)
        if not query_data:
            return

        # Show edit dialog with current data
        dialog = EditQueryDialog(
            query_data["theme"], query_data["query"], query_data["advanced"], self
        )

        if dialog.exec():
            # Update query with new data
            theme, query, advanced = dialog.get_query_data()
            success = self.query_table.update_query(query_id, theme, query, advanced)
            if success:
                self.status_bar.showMessage(f"Consulta atualizada: {theme}")

    def show_search_settings_dialog(self):
        dialog = SearchSettingsDialog(self.config, self)
        if dialog.exec():
            # Update settings in search manager
            self.search_manager.update_settings(
                max_workers=self.config.get("max_workers"),
                request_delay=self.config.get("request_delay"),
                max_pages=self.config.get("max_pages"),
            )
            self.status_bar.showMessage("Configurações de busca atualizadas")

    def show_export_settings_dialog(self):
        dialog = ExportSettingsDialog(self.config, self)
        if dialog.exec():
            self.status_bar.showMessage("Configurações de exportação atualizadas")

    def show_export_dialog(self):
        if self.papers_table.rowCount() == 0:
            QMessageBox.information(self, "Sem Artigos", "Não há artigos para exportar.")
            return

        dialog = ExportDialog(self.config, self)
        if dialog.exec():
            filename, fields = dialog.get_export_data()

            # Verificar se há campos selecionados nas configurações
            if not fields:
                # Se não houver campos configurados, mostrar o diálogo de configurações
                QMessageBox.warning(
                    self,
                    "Configurações Incompletas",
                    "Nenhum campo selecionado para exportação. Configure os campos primeiro.",
                )
                self.show_export_settings_dialog()
                return

            try:
                from wizard.core.exporter import export_articles

                articles = self.papers_table.get_articles()
                exported_file = export_articles(articles, filename, fields)

                if exported_file:
                    QMessageBox.information(
                        self,
                        "Exportação Concluída",
                        f"Exportados com sucesso {len(articles)} artigos para {exported_file}",
                    )
                    self.status_bar.showMessage(
                        f"Exportados {len(articles)} artigos para {exported_file}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Aviso de Exportação",
                        "Nenhum arquivo foi criado. Consulte os logs para detalhes.",
                    )
            except Exception as e:
                logger.error(f"Export error: {str(e)}", exc_info=True)
                QMessageBox.critical(
                    self, "Erro de Exportação", f"Falha ao exportar artigos: {str(e)}"
                )

    @Slot(str, int)
    def update_query_progress(self, query_id, progress):
        # Update progress for specific query
        self.query_table.update_progress(query_id, progress)

    @Slot(str, str)
    def update_status(self, query_id, status_message):
        # Update status bar
        self.status_bar.showMessage(status_message)

    @Slot(str, list)
    def search_completed(self, query_id, articles):
        # Update query status
        self.query_table.set_completed(query_id)

        # Add articles to papers table
        self.papers_table.add_articles(articles)

        # Update papers count
        count = self.papers_table.rowCount()
        self.papers_count.setText(f"{count} artigos encontrados")

        # Enable export button if we have results
        self.export_button.setEnabled(count > 0)

        # Update status
        self.status_bar.showMessage(f"Busca concluída. Encontrados {len(articles)} artigos.")

    @Slot(str, str)
    def search_error(self, query_id, error_message):
        # Update query status
        self.query_table.set_error(query_id, error_message)

        # Show error message
        QMessageBox.warning(self, "Erro na Busca", f"Erro na consulta: {error_message}")

        # Update status
        self.status_bar.showMessage(f"Erro na busca: {error_message}")

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
                advanced=query_data["advanced"],
            )

            # Update status
            self.status_bar.showMessage(f"Iniciando busca para: {query_data['theme']}")

    def pause_search(self, query_id):
        self.search_manager.pause_search(query_id)
        self.query_table.set_paused(query_id)

        # Update status
        query_data = self.query_table.get_query(query_id)
        if query_data:
            self.status_bar.showMessage(f"Busca pausada para: {query_data['theme']}")

    def delete_query(self, query_id):
        # If search is running, cancel it first
        self.search_manager.cancel_search(query_id)

        # Get query data before removal for status message
        query_data = self.query_table.get_query(query_id)
        theme = query_data["theme"] if query_data else "consulta"

        # Remove from UI
        self.query_table.remove_query(query_id)

        # Update status
        self.status_bar.showMessage(f"Consulta excluída: {theme}")

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

        logger.info("Aplicação fechada")
        event.accept()


def main():
    """Run the application"""
    import sys

    app = QApplication(sys.argv)

    # Set application style and icon
    app.setStyle("Fusion")
    app.setApplicationName("Wizard")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
