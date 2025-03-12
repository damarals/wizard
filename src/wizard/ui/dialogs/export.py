"""
Export dialog for Wizard.
"""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ..widgets.dialog_helpers import setup_dialog_header, style_dialog_buttons


class ExportDialog(QDialog):
    """Dialog for exporting articles to CSV"""

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config

        setup_dialog_header(self, "Exportar Artigos", "DEVICE_FLOPPY")
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)

        # Filename section
        filename_group = QGroupBox("Arquivo de Saída")
        filename_layout = QHBoxLayout(filename_group)

        self.filename_input = QLineEdit()
        self.filename_input.setText(self.config.get("export_filename", "artigos_capes.csv"))
        filename_layout.addWidget(self.filename_input)

        browse_button = QPushButton("Procurar...")
        browse_button.clicked.connect(self.browse_file)
        filename_layout.addWidget(browse_button)

        layout.addWidget(filename_group)

        # Info about fields
        info_label = QLabel(
            "Os campos a serem exportados são definidos nas configurações de exportação. "
            "Utilize o botão de configurações ao lado de 'Exportar Artigos' para modificá-los."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)

        # Spacer
        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Exportar")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Apply styling to buttons
        style_dialog_buttons(self, button_box)

    def browse_file(self):
        """Show file dialog to select save location"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Arquivo CSV",
            self.filename_input.text(),
            "Arquivos CSV (*.csv);;Todos os Arquivos (*)",
        )

        if filename:
            self.filename_input.setText(filename)

    def validate_and_accept(self):
        """Validate inputs before accepting"""
        filename = self.filename_input.text().strip()

        if not filename:
            self.filename_input.setFocus()
            return

        # Ensure filename ends with .csv
        if not filename.lower().endswith(".csv"):
            filename += ".csv"
            self.filename_input.setText(filename)

        # Save filename to config
        self.config.set("export_filename", filename)
        self.config.save()

        self.accept()

    def get_export_data(self):
        """Get the filename and selected fields from config"""
        filename = self.filename_input.text().strip()

        # Ensure filename ends with .csv
        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        # Get fields from config
        selected_fields = self.config.get("default_export_fields", [])

        return filename, selected_fields
