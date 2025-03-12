"""
Table widget for displaying and managing search queries.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QProgressBar,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from ...utils.logger import get_logger

logger = get_logger(__name__)


class QueryTableWidget(QTableWidget):
    """Table for displaying and managing search queries"""

    # Signals
    start_search = Signal(str)  # query_id
    pause_search = Signal(str)  # query_id
    delete_query = Signal(str)  # query_id
    edit_query = Signal(str)  # query_id (nova sinal para edição)

    # Column indices
    COL_THEME = 0
    COL_QUERY = 1
    COL_STATUS = 2
    COL_PROGRESS = 3
    COL_ACTIONS = 4

    # Status colors
    STATUS_COLORS = {
        "idle": QColor(240, 240, 240),
        "running": QColor(255, 255, 224),  # Light yellow
        "paused": QColor(220, 220, 220),
        "completed": QColor(224, 255, 224),  # Light green
        "error": QColor(255, 224, 224),  # Light red
    }

    # Status labels in Portuguese
    STATUS_LABELS = {
        "idle": "Pronto",
        "running": "Executando",
        "paused": "Pausado",
        "completed": "Concluído",
        "error": "Erro",
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # Store query data
        self.queries = {}  # query_id -> query data dict
        self.next_id = 1  # Counter for generating unique IDs

        # Set up table
        self.setup_table()

    def setup_table(self):
        # Set columns
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Tema", "Termos de Busca", "Status", "Progresso", "Ações"])

        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(self.COL_THEME, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_QUERY, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_STATUS, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_PROGRESS, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_ACTIONS, QHeaderView.ResizeToContents)

        # Set selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Hide vertical header (row numbers)
        self.verticalHeader().setVisible(False)

        # No edit triggers
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Allow sorting
        self.setSortingEnabled(True)

        # Set alternate row colors
        self.setAlternatingRowColors(True)

    def add_query(self, theme, query, advanced=True):
        """Add a new query to the table"""
        # Generate query ID
        query_id = f"query_{self.next_id}"
        self.next_id += 1

        # Store query data
        self.queries[query_id] = {
            "theme": theme,
            "query": query,
            "advanced": advanced,
            "status": "idle",
            "progress": 0,
        }

        # Add row to table
        row = self.rowCount()
        self.insertRow(row)

        # Set theme and query
        theme_item = QTableWidgetItem(theme)
        theme_item.setData(Qt.UserRole, query_id)  # Store query_id for reference
        self.setItem(row, self.COL_THEME, theme_item)

        query_item = QTableWidgetItem(query)
        query_item.setToolTip(query)
        self.setItem(row, self.COL_QUERY, query_item)

        # Create status cell
        status_item = QTableWidgetItem(self.STATUS_LABELS["idle"])
        status_item.setTextAlignment(Qt.AlignCenter)
        status_item.setBackground(self.STATUS_COLORS["idle"])
        self.setItem(row, self.COL_STATUS, status_item)

        # Create progress bar cell
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progress_bar.setMinimumWidth(150)
        self.setCellWidget(row, self.COL_PROGRESS, progress_bar)

        # Create actions cell
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 2, 5, 2)
        actions_layout.setSpacing(2)

        # Start button
        start_button = QPushButton()
        start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        start_button.setToolTip("Iniciar Busca")
        start_button.setFixedSize(QSize(24, 24))
        start_button.clicked.connect(lambda: self.start_search.emit(query_id))
        actions_layout.addWidget(start_button)

        # Pause button (initially hidden)
        pause_button = QPushButton()
        pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        pause_button.setToolTip("Pausar Busca")
        pause_button.setFixedSize(QSize(24, 24))
        pause_button.clicked.connect(lambda: self.pause_search.emit(query_id))
        pause_button.setVisible(False)
        actions_layout.addWidget(pause_button)

        # Edit button
        edit_button = QPushButton()
        edit_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        edit_button.setToolTip("Editar Consulta")
        edit_button.setFixedSize(QSize(24, 24))
        edit_button.clicked.connect(lambda: self.edit_query.emit(query_id))
        actions_layout.addWidget(edit_button)

        # Delete button
        delete_button = QPushButton()
        delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        delete_button.setToolTip("Excluir Consulta")
        delete_button.setFixedSize(QSize(24, 24))
        delete_button.clicked.connect(lambda: self.delete_query.emit(query_id))
        actions_layout.addWidget(delete_button)

        # Store buttons in query data for reference
        self.queries[query_id]["buttons"] = {
            "start": start_button,
            "pause": pause_button,
            "edit": edit_button,
            "delete": delete_button,
        }

        self.setCellWidget(row, self.COL_ACTIONS, actions_widget)

        # Store row index with query data
        self.queries[query_id]["row"] = row

        logger.debug(f"Added query: {theme} (ID: {query_id})")

        # Return the query ID
        return query_id

    def update_query(self, query_id, theme, query, advanced):
        """Update an existing query"""
        if query_id not in self.queries:
            return False

        # Update stored data
        self.queries[query_id].update({"theme": theme, "query": query, "advanced": advanced})

        # Update table cells
        row = self.queries[query_id]["row"]

        # Update theme
        theme_item = self.item(row, self.COL_THEME)
        theme_item.setText(theme)

        # Update query
        query_item = self.item(row, self.COL_QUERY)
        query_item.setText(query)
        query_item.setToolTip(query)

        return True

    def update_progress(self, query_id, progress):
        """Update progress for a query"""
        if query_id not in self.queries:
            return

        # Update stored data
        self.queries[query_id]["progress"] = progress

        # Update progress bar
        row = self.queries[query_id]["row"]
        progress_bar = self.cellWidget(row, self.COL_PROGRESS)
        if progress_bar:
            progress_bar.setValue(progress)

    def set_running(self, query_id):
        """Set query status to running"""
        if query_id not in self.queries:
            return

        # Update stored data
        self.queries[query_id]["status"] = "running"

        # Update status cell
        row = self.queries[query_id]["row"]
        status_item = self.item(row, self.COL_STATUS)
        if status_item:
            status_item.setText(self.STATUS_LABELS["running"])
            status_item.setBackground(self.STATUS_COLORS["running"])

        # Update buttons
        buttons = self.queries[query_id]["buttons"]
        buttons["start"].setVisible(False)
        buttons["pause"].setVisible(True)
        buttons["edit"].setEnabled(False)

    def set_paused(self, query_id):
        """Set query status to paused"""
        if query_id not in self.queries:
            return

        # Update stored data
        self.queries[query_id]["status"] = "paused"

        # Update status cell
        row = self.queries[query_id]["row"]
        status_item = self.item(row, self.COL_STATUS)
        if status_item:
            status_item.setText(self.STATUS_LABELS["paused"])
            status_item.setBackground(self.STATUS_COLORS["paused"])

        # Update buttons
        buttons = self.queries[query_id]["buttons"]
        buttons["start"].setVisible(True)
        buttons["pause"].setVisible(False)
        buttons["edit"].setEnabled(True)

    def set_completed(self, query_id):
        """Set query status to completed"""
        if query_id not in self.queries:
            return

        # Update stored data
        self.queries[query_id]["status"] = "completed"
        self.queries[query_id]["progress"] = 100

        # Update status cell
        row = self.queries[query_id]["row"]
        status_item = self.item(row, self.COL_STATUS)
        if status_item:
            status_item.setText(self.STATUS_LABELS["completed"])
            status_item.setBackground(self.STATUS_COLORS["completed"])

        # Update progress bar
        progress_bar = self.cellWidget(row, self.COL_PROGRESS)
        if progress_bar:
            progress_bar.setValue(100)

        # Update buttons
        buttons = self.queries[query_id]["buttons"]
        buttons["start"].setVisible(True)
        buttons["pause"].setVisible(False)
        buttons["edit"].setEnabled(True)

    def set_error(self, query_id, error_message):
        """Set query status to error"""
        if query_id not in self.queries:
            return

        # Update stored data
        self.queries[query_id]["status"] = "error"
        self.queries[query_id]["error"] = error_message

        # Update status cell
        row = self.queries[query_id]["row"]
        status_item = self.item(row, self.COL_STATUS)
        if status_item:
            status_item.setText(self.STATUS_LABELS["error"])
            status_item.setBackground(self.STATUS_COLORS["error"])
            status_item.setToolTip(error_message)

        # Update buttons
        buttons = self.queries[query_id]["buttons"]
        buttons["start"].setVisible(True)
        buttons["pause"].setVisible(False)
        buttons["edit"].setEnabled(True)

    def remove_query(self, query_id):
        """Remove a query from the table"""
        if query_id not in self.queries:
            return

        # Remove row from table
        row = self.queries[query_id]["row"]
        self.removeRow(row)

        # Update row indices for remaining queries
        for qid, data in self.queries.items():
            if data["row"] > row:
                data["row"] -= 1

        # Remove from stored data
        logger.debug(f"Removed query: {self.queries[query_id]['theme']} (ID: {query_id})")
        del self.queries[query_id]

    def get_query(self, query_id):
        """Get query data by ID"""
        return self.queries.get(query_id)

    def get_active_queries(self):
        """Get list of active query IDs"""
        return [qid for qid, data in self.queries.items() if data["status"] == "running"]

    def calculate_overall_progress(self):
        """Calculate overall progress across all queries"""
        if not self.queries:
            return 0

        # Get all queries that have started
        active_queries = [
            data
            for data in self.queries.values()
            if data["status"] in ["running", "completed", "paused"]
        ]

        if not active_queries:
            return 0

        # Calculate average progress
        total_progress = sum(data["progress"] for data in active_queries)
        return int(total_progress / len(active_queries))
