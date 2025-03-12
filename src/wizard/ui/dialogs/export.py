"""
Export dialog for CAPES Research Wizard.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QDialogButtonBox, QGroupBox,
    QCheckBox, QScrollArea, QWidget, QGridLayout, QStyle
)
from PySide6.QtCore import Qt

from ...core.exporter import get_available_fields
from ...utils.config import Config

class ExportDialog(QDialog):
    """Dialog for exporting articles to CSV"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.config = config
        
        self.setWindowTitle("Export Articles")
        self.resize(500, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        
        # Filename section
        filename_group = QGroupBox("Output File")
        filename_layout = QHBoxLayout(filename_group)
        
        self.filename_input = QLineEdit()
        self.filename_input.setText(self.config.get("export_filename", "capes_articles.csv"))
        filename_layout.addWidget(self.filename_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        filename_layout.addWidget(browse_button)
        
        layout.addWidget(filename_group)
        
        # Fields selection section
        fields_group = QGroupBox("Fields to Export")
        fields_layout = QVBoxLayout(fields_group)
        
        fields_help = QLabel("Select the fields to include in the exported CSV file:")
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
        
        # Get previously selected fields from config
        selected_fields = self.config.get("selected_export_fields", [])
        if not selected_fields:
            # Default to fields with default_enabled=True
            selected_fields = [f["name"] for f in available_fields if f["default_enabled"]]
        
        # Add a Select All checkbox
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_fields)
        scroll_layout.addWidget(self.select_all_checkbox, 0, 0, 1, 2)
        
        # Add individual field checkboxes
        for i, field in enumerate(available_fields):
            checkbox = QCheckBox(field["name"])
            checkbox.setChecked(field["name"] in selected_fields)
            checkbox.stateChanged.connect(self.update_select_all_state)
            
            description = QLabel(field["description"])
            description.setStyleSheet("color: gray;")
            
            scroll_layout.addWidget(checkbox, i + 1, 0)
            scroll_layout.addWidget(description, i + 1, 1)
            
            self.field_checkboxes[field["name"]] = checkbox
        
        # Update select all state
        self.update_select_all_state()
        
        fields_layout.addWidget(scroll_area)
        
        layout.addWidget(fields_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def browse_file(self):
        """Show file dialog to select save location"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", self.filename_input.text(),
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            self.filename_input.setText(filename)
    
    def toggle_all_fields(self, state):
        """Toggle all field checkboxes"""
        for checkbox in self.field_checkboxes.values():
            checkbox.setChecked(state == Qt.Checked)
    
    def update_select_all_state(self):
        """Update the state of the 'Select All' checkbox"""
        all_checked = all(checkbox.isChecked() for checkbox in self.field_checkboxes.values())
        any_checked = any(checkbox.isChecked() for checkbox in self.field_checkboxes.values())
        
        if all_checked:
            self.select_all_checkbox.setCheckState(Qt.Checked)
        elif any_checked:
            self.select_all_checkbox.setCheckState(Qt.PartiallyChecked)
        else:
            self.select_all_checkbox.setCheckState(Qt.Unchecked)
    
    def validate_and_accept(self):
        """Validate inputs before accepting"""
        filename = self.filename_input.text().strip()
        
        if not filename:
            self.filename_input.setFocus()
            return
        
        # Ensure filename ends with .csv
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
            self.filename_input.setText(filename)
        
        # Get selected fields
        selected_fields = [name for name, checkbox in self.field_checkboxes.items() 
                          if checkbox.isChecked()]
        
        if not selected_fields:
            # If no fields selected, select at least 'title'
            if 'title' in self.field_checkboxes:
                self.field_checkboxes['title'].setChecked(True)
                selected_fields = ['title']
            else:
                return
        
        # Save to config
        self.config.set("export_filename", filename)
        self.config.set("selected_export_fields", selected_fields)
        self.config.save()
        
        self.accept()
    
    def get_export_data(self):
        """Get the filename and selected fields"""
        filename = self.filename_input.text().strip()
        
        # Ensure filename ends with .csv
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        # Get selected fields
        selected_fields = [name for name, checkbox in self.field_checkboxes.items() 
                          if checkbox.isChecked()]
        
        return filename, selected_fields