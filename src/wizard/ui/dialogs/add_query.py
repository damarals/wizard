"""
Dialog for adding a new search query.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from ..widgets.dialog_helpers import setup_dialog_header, style_dialog_buttons


class AddQueryDialog(QDialog):
    """Dialog for adding a new search query"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Use a standard icon name that exists in TablerIcons
        setup_dialog_header(self, "Adicionar Consulta", "SEARCH")

        # Set fixed width for a more consistent UI
        self.setMinimumWidth(600)

        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Theme input
        layout.addWidget(QLabel("Tema:"))
        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("ex: Aprendizado de Máquina, Mudanças Climáticas")
        layout.addWidget(self.theme_input)

        # Query input
        layout.addWidget(QLabel("Termos de Busca:"))
        self.query_input = QTextEdit()
        self.query_input.setMinimumHeight(150)  # Ensure taller text area
        self.query_input.setPlaceholderText(
            "Digite os termos de busca ou consulta avançada com operadores.\n\n"
            "Exemplos:\n"
            "Simples: aprendizado de máquina mudanças climáticas\n"
            'Avançado: ("aprendizado de máquina" OR "deep learning") AND "clima"'
        )
        layout.addWidget(self.query_input)

        # Advanced search option
        advanced_layout = QHBoxLayout()
        self.advanced_checkbox = QCheckBox("Usar Sintaxe de Busca Avançada")
        self.advanced_checkbox.setChecked(True)
        advanced_layout.addWidget(self.advanced_checkbox)
        advanced_layout.addStretch()
        layout.addLayout(advanced_layout)

        # Help text
        help_text = (
            "A busca avançada permite usar operadores como AND, OR, NOT "
            "e agrupamento com parênteses para consultas mais precisas."
        )
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(help_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Adicionar")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Apply styling to buttons
        style_dialog_buttons(self, button_box)

        # Set focus to theme input
        self.theme_input.setFocus()

    def get_query_data(self):
        """Get the theme, query, and advanced option from the dialog"""
        return (
            self.theme_input.text().strip(),
            self.query_input.toPlainText().strip(),
            self.advanced_checkbox.isChecked(),
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
