"""
Export settings dialog for Wizard.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from wizard.core.exporter import get_available_fields
from wizard.ui.widgets.dialog_helpers import setup_dialog_header, style_dialog_buttons


class ExportSettingsDialog(QDialog):
    """Dialog for configuring export settings"""

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config
        self.updating_checkboxes = False  # Flag para evitar loops de sinal

        setup_dialog_header(self, "Configurações de Exportação", "SETTINGS")
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)

        # Fields selection section
        fields_group = QGroupBox("Campos Padrão para Exportação")
        fields_layout = QVBoxLayout(fields_group)

        fields_help = QLabel("Selecione os campos a serem incluídos por padrão na exportação:")
        fields_help.setWordWrap(True)
        fields_layout.addWidget(fields_help)

        # Create a scrollable area for fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setColumnStretch(0, 1)
        scroll_layout.setColumnStretch(1, 3)
        scroll_area.setWidget(scroll_widget)

        # Add field checkboxes
        self.field_checkboxes = {}
        available_fields = get_available_fields()

        # Translate field descriptions
        field_translations = {
            "title": "Título",
            "authors": "Autores",
            "publication_date": "Data de Publicação",
            "doi": "DOI",
            "journal": "Periódico",
            "abstract": "Resumo",
            "search_term": "Tema da Busca",
            "topics": "Tópicos",
            "is_open_access": "Acesso Aberto",
            "is_peer_reviewed": "Revisado por Pares",
            "article_id": "ID do Artigo",
            "issn": "ISSN",
            "volume": "Volume",
            "issue": "Edição",
            "language": "Idioma",
            "publisher": "Editora",
            "detail_url": "URL do Artigo",
        }

        # Get previously selected fields from config
        selected_fields = self.config.get("default_export_fields", [])
        if not selected_fields:
            # Default to fields with default_enabled=True
            selected_fields = [f["name"] for f in available_fields if f["default_enabled"]]

        # Add a Select All checkbox
        self.select_all_checkbox = QCheckBox("Selecionar Todos")
        self.select_all_checkbox.clicked.connect(
            self.toggle_all_fields
        )  # Usamos clicked ao invés de stateChanged
        scroll_layout.addWidget(self.select_all_checkbox, 0, 0, 1, 2)

        # Add individual field checkboxes
        for i, field in enumerate(available_fields):
            checkbox = QCheckBox(field_translations.get(field["name"], field["name"]))
            checkbox.setChecked(field["name"] in selected_fields)
            checkbox.clicked.connect(
                self.update_select_all_state
            )  # Usamos clicked ao invés de stateChanged

            description = QLabel(field["description"])
            description.setStyleSheet("color: gray;")

            # Store original field name with the checkbox
            checkbox.setProperty("field_name", field["name"])

            scroll_layout.addWidget(checkbox, i + 1, 0)
            scroll_layout.addWidget(description, i + 1, 1)

            self.field_checkboxes[field["name"]] = checkbox

        # Update select all state
        self.update_select_all_state()

        fields_layout.addWidget(scroll_area)

        layout.addWidget(fields_group)

        # Options group
        options_group = QGroupBox("Opções de Exportação")
        options_layout = QVBoxLayout(options_group)

        # Include headers option
        self.include_headers_check = QCheckBox("Incluir cabeçalhos no CSV")
        self.include_headers_check.setChecked(self.config.get("export_include_headers", True))
        options_layout.addWidget(self.include_headers_check)

        # UTF-8 BOM option (for better Excel compatibility)
        self.utf8_bom_check = QCheckBox("Adicionar BOM (para melhor compatibilidade com Excel)")
        self.utf8_bom_check.setChecked(self.config.get("export_utf8_bom", True))
        options_layout.addWidget(self.utf8_bom_check)

        layout.addWidget(options_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Salvar")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Apply styling to buttons
        style_dialog_buttons(self, button_box)

    def toggle_all_fields(self, checked):
        """Toggle all field checkboxes"""
        if self.updating_checkboxes:
            return

        self.updating_checkboxes = True
        try:
            # Bloquear sinais para evitar recursão infinita
            for checkbox in self.field_checkboxes.values():
                checkbox.setChecked(checked)
        finally:
            self.updating_checkboxes = False

    def update_select_all_state(self):
        """Update the state of the 'Select All' checkbox"""
        if self.updating_checkboxes:
            return

        self.updating_checkboxes = True
        try:
            # Verifica se todos estão marcados
            all_checked = all(checkbox.isChecked() for checkbox in self.field_checkboxes.values())
            # Verifica se nenhum está marcado
            none_checked = not any(
                checkbox.isChecked() for checkbox in self.field_checkboxes.values()
            )

            if all_checked:
                self.select_all_checkbox.setCheckState(Qt.Checked)
            elif none_checked:
                self.select_all_checkbox.setCheckState(Qt.Unchecked)
            else:
                self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        finally:
            self.updating_checkboxes = False

    def save_settings(self):
        """Save settings to config and accept dialog"""
        # Get selected fields (using original field names)
        selected_fields = [
            name for name, checkbox in self.field_checkboxes.items() if checkbox.isChecked()
        ]

        # Save to config
        self.config.set("default_export_fields", selected_fields)
        self.config.set("export_include_headers", self.include_headers_check.isChecked())
        self.config.set("export_utf8_bom", self.utf8_bom_check.isChecked())

        # Save config to file
        self.config.save()

        self.accept()
