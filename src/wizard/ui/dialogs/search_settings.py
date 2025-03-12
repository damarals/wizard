"""
Search engine settings dialog for Wizard.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QSpinBox,
    QVBoxLayout,
)

from wizard.ui.widgets.dialog_helpers import setup_dialog_header, style_dialog_buttons


class SearchSettingsDialog(QDialog):
    """Dialog for configuring search engine settings"""

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config

        setup_dialog_header(self, "Configurações da Busca", "SETTINGS")
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)

        # Performance group
        performance_group = QGroupBox("Desempenho")
        performance_layout = QFormLayout(performance_group)

        # Workers
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 10)
        self.workers_spin.setValue(self.config.get("max_workers", 3))
        self.workers_spin.setToolTip("Número de pesquisas concorrentes")
        performance_layout.addRow("Pesquisas Concorrentes:", self.workers_spin)

        # Delay
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.5, 10.0)
        self.delay_spin.setSingleStep(0.5)
        self.delay_spin.setValue(self.config.get("request_delay", 2.0))
        self.delay_spin.setToolTip("Intervalo entre requisições em segundos")
        performance_layout.addRow("Intervalo (segundos):", self.delay_spin)

        # Max pages
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setRange(1, 100)
        self.max_pages_spin.setValue(self.config.get("max_pages", 5))
        self.max_pages_spin.setSpecialValueText("Todos")  # "1" will display as "Todos"
        self.max_pages_spin.setToolTip("Número máximo de páginas por busca")
        performance_layout.addRow("Máximo de Páginas por Busca:", self.max_pages_spin)

        layout.addWidget(performance_group)

        # Options group
        options_group = QGroupBox("Opções")
        options_layout = QVBoxLayout(options_group)

        # Fetch details
        self.fetch_details_check = QCheckBox("Buscar metadados detalhados dos artigos")
        self.fetch_details_check.setChecked(self.config.get("fetch_details", True))
        self.fetch_details_check.setToolTip(
            "Se desativado, apenas informações básicas serão coletadas"
        )
        options_layout.addWidget(self.fetch_details_check)

        # Use advanced search
        self.advanced_search_check = QCheckBox("Usar sintaxe de busca avançada por padrão")
        self.advanced_search_check.setChecked(self.config.get("use_advanced_search", True))
        options_layout.addWidget(self.advanced_search_check)

        layout.addWidget(options_group)

        # Add spacer
        layout.addStretch()

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

    def save_settings(self):
        """Save settings to config and accept dialog"""
        # Save search settings
        self.config.set("max_workers", self.workers_spin.value())
        self.config.set("request_delay", self.delay_spin.value())
        self.config.set("max_pages", self.max_pages_spin.value())
        self.config.set("fetch_details", self.fetch_details_check.isChecked())
        self.config.set("use_advanced_search", self.advanced_search_check.isChecked())

        # Save config to file
        self.config.save()

        self.accept()
