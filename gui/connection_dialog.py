#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Connection dialog for vCenter server authentication
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QCheckBox, QPushButton, QGridLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class ConnectionDialog(QDialog):
    """Dialog for connecting to a vCenter server"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to vCenter")
        self.setMinimumWidth(400)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Create form layout
        form_layout = QGridLayout()
        
        # Server field
        form_layout.addWidget(QLabel("vCenter Server:"), 0, 0)
        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("vcenter.example.com")
        form_layout.addWidget(self.server_edit, 0, 1)
        
        # Username field
        form_layout.addWidget(QLabel("Username:"), 1, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("administrator@vsphere.local")
        form_layout.addWidget(self.username_edit, 1, 1)
        
        # Password field
        form_layout.addWidget(QLabel("Password:"), 2, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_edit, 2, 1)
        
        layout.addLayout(form_layout)
        
        # Ignore SSL verification checkbox
        self.ignore_ssl_check = QCheckBox("Ignore SSL certificate verification")
        self.ignore_ssl_check.setChecked(True)
        layout.addWidget(self.ignore_ssl_check)
        
        # Add info text about SSL verification
        ssl_info = QLabel(
            "Note: Ignoring SSL verification is not recommended for production environments, "
            "but may be necessary if the vCenter uses a self-signed certificate."
        )
        ssl_info.setWordWrap(True)
        ssl_info.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(ssl_info)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def accept(self):
        """Validate inputs before accepting"""
        if not self.server_edit.text():
            QMessageBox.warning(self, "Input Error", "vCenter Server address is required.")
            return
            
        if not self.username_edit.text():
            QMessageBox.warning(self, "Input Error", "Username is required.")
            return
            
        if not self.password_edit.text():
            QMessageBox.warning(self, "Input Error", "Password is required.")
            return
            
        super().accept()
