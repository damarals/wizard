"""
Custom progress bar widget with status text.
"""

from PySide6.QtWidgets import (
    QWidget, QProgressBar, QLabel, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, Slot

class ProgressBarWidget(QWidget):
    """Progress bar widget with status text"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Status text
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.percentage_label = QLabel("0%")
        status_layout.addWidget(self.percentage_label)
        
        layout.addLayout(status_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
    
    @Slot(int)
    def set_progress(self, value):
        """Set progress value"""
        self.progress_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
    
    @Slot(str)
    def set_status(self, text):
        """Set status text"""
        self.status_label.setText(text)
    
    def reset(self):
        """Reset progress bar to 0"""
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.status_label.setText("Ready")