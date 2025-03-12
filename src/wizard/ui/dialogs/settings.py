"""
Settings dialog for CAPES Research Wizard.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
    QDoubleSpinBox, QCheckBox, QTabWidget, QWidget,
    QDialogButtonBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt

from ...utils.config import Config

class SettingsDialog(QDialog):
    """Dialog for configuring application settings"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.config = config
        
        self.setWindowTitle("Settings")
        self.resize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Search tab
        search_tab = QWidget()
        tab_widget.addTab(search_tab, "Search Engine")
        
        search_layout = QVBoxLayout(search_tab)
        
        # Performance group
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        # Workers
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 10)
        self.workers_spin.setValue(self.config.get("max_workers", 3))
        self.workers_spin.setToolTip("Number of concurrent search threads")
        performance_layout.addRow("Concurrent Workers:", self.workers_spin)
        
        # Delay
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.5, 10.0)
        self.delay_spin.setSingleStep(0.5)
        self.delay_spin.setValue(self.config.get("request_delay", 2.0))
        self.delay_spin.setToolTip("Delay between requests in seconds")
        performance_layout.addRow("Request Delay (seconds):", self.delay_spin)
        
        # Max pages
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setRange(1, 100)
        self.max_pages_spin.setValue(self.config.get("max_pages", 5))
        self.max_pages_spin.setSpecialValueText("All")  # "1" will display as "All"
        self.max_pages_spin.setToolTip("Maximum number of pages to scrape per search")
        performance_layout.addRow("Maximum Pages per Search:", self.max_pages_spin)
        
        search_layout.addWidget(performance_group)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        # Fetch details
        self.fetch_details_check = QCheckBox("Fetch detailed article metadata")
        self.fetch_details_check.setChecked(self.config.get("fetch_details", True))
        self.fetch_details_check.setToolTip("If disabled, only basic article information will be collected")
        options_layout.addWidget(self.fetch_details_check)
        
        # Use advanced search
        self.advanced_search_check = QCheckBox("Use advanced search syntax by default")
        self.advanced_search_check.setChecked(self.config.get("use_advanced_search", True))
        options_layout.addWidget(self.advanced_search_check)
        
        search_layout.addWidget(options_group)
        
        # Add spacer
        search_layout.addStretch()
        
        # Display tab
        display_tab = QWidget()
        tab_widget.addTab(display_tab, "Display")
        
        display_layout = QVBoxLayout(display_tab)
        
        # Table options group
        table_group = QGroupBox("Table Display")
        table_layout = QVBoxLayout(table_group)
        
        # Auto-resize columns
        self.auto_resize_check = QCheckBox("Auto-resize table columns to content")
        self.auto_resize_check.setChecked(self.config.get("auto_resize_columns", True))
        table_layout.addWidget(self.auto_resize_check)
        
        # Alternate row colors
        self.alternate_colors_check = QCheckBox("Use alternate row colors")
        self.alternate_colors_check.setChecked(self.config.get("alternate_row_colors", True))
        table_layout.addWidget(self.alternate_colors_check)
        
        display_layout.addWidget(table_group)
        
        # Add spacer
        display_layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def save_settings(self):
        """Save settings to config and accept dialog"""
        # Save search settings
        self.config.set("max_workers", self.workers_spin.value())
        self.config.set("request_delay", self.delay_spin.value())
        self.config.set("max_pages", self.max_pages_spin.value())
        self.config.set("fetch_details", self.fetch_details_check.isChecked())
        self.config.set("use_advanced_search", self.advanced_search_check.isChecked())
        
        # Save display settings
        self.config.set("auto_resize_columns", self.auto_resize_check.isChecked())
        self.config.set("alternate_row_colors", self.alternate_colors_check.isChecked())
        
        # Save config to file
        self.config.save()
        
        self.accept()