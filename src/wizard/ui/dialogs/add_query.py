"""
Dialog for adding a new search query.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QCheckBox, QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt

class AddQueryDialog(QDialog):
    """Dialog for adding a new search query"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Add Search Query")
        self.resize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Theme input
        layout.addWidget(QLabel("Theme:"))
        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("e.g., Machine Learning, Climate Change")
        layout.addWidget(self.theme_input)
        
        # Query input
        layout.addWidget(QLabel("Search Query:"))
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText(
            'Enter search terms or advanced query with operators.\n\n'
            'Examples:\n'
            'Simple: machine learning climate change\n'
            'Advanced: ("machine learning" OR "deep learning") AND "climate"'
        )
        layout.addWidget(self.query_input)
        
        # Advanced search option
        advanced_layout = QHBoxLayout()
        self.advanced_checkbox = QCheckBox("Use Advanced Search Syntax")
        self.advanced_checkbox.setChecked(True)
        advanced_layout.addWidget(self.advanced_checkbox)
        advanced_layout.addStretch()
        layout.addLayout(advanced_layout)
        
        # Help text
        help_text = (
            "Advanced search allows using operators like AND, OR, NOT "
            "and grouping with parentheses for more precise queries."
        )
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(help_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set focus to theme input
        self.theme_input.setFocus()
    
    def get_query_data(self):
        """Get the theme, query, and advanced option from the dialog"""
        return (
            self.theme_input.text().strip(),
            self.query_input.toPlainText().strip(),
            self.advanced_checkbox.isChecked()
        )
    
    def accept(self):
        """Validate inputs before accepting"""
        theme = self.theme_input.text().strip()
        query = self.query_input.toPlainText().strip()
        
        if not theme:
            self.theme_input.setFocus()
            return
        
        if not query:
            self.query_input.setFocus()
            return
        
        super().accept()