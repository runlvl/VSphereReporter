#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Progress dialog for long-running operations
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar,
    QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class ProgressDialog(QDialog):
    """Dialog for showing progress of long-running operations"""
    
    def __init__(self, title, initial_status, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        self.canceled = False
        
        # Initialize UI
        self.init_ui(initial_status)
        
    def init_ui(self, initial_status):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel(initial_status)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.handle_cancel)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def set_status(self, status):
        """Update the status text"""
        self.status_label.setText(status)
        
    def set_progress(self, value):
        """Update the progress bar value"""
        self.progress_bar.setValue(value)
        
    def handle_cancel(self):
        """Handle cancel button click"""
        self.canceled = True
        self.status_label.setText("Canceling operation...")
        self.cancel_button.setEnabled(False)
        
    def is_canceled(self):
        """Check if the operation was canceled"""
        return self.canceled
