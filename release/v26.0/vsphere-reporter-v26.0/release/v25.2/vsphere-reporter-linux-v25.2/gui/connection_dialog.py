#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Connection Dialog
Dialogfenster zum Herstellen einer Verbindung mit vCenter
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QCheckBox, QGroupBox,
                            QFormLayout, QDialogButtonBox, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

# Bechtle-Farbschema
BECHTLE_DARK_BLUE = "#00355e"
BECHTLE_ORANGE = "#da6f1e"
BECHTLE_GREEN = "#23a96a"
BECHTLE_LIGHT_GRAY = "#f3f3f3"
BECHTLE_DARK_GRAY = "#5a5a5a"

class ConnectionDialog(QDialog):
    """Dialog zum Herstellen einer Verbindung mit vCenter"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        self.server = ""
        self.username = ""
        self.password = ""
        self.ignore_ssl = True
        
        self.init_ui()
        
    def init_ui(self):
        """Initialisiere die Benutzeroberfläche"""
        self.setWindowTitle("Verbindung zu vCenter herstellen")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Header mit Bechtle-Branding
        header_layout = QHBoxLayout()
        header_label = QLabel("Cloud Solutions | Datacenter & Endpoint")
        header_label.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        layout.addLayout(header_layout)
        
        # Produktname
        product_name = QLabel("VMware vSphere Reporter")
        product_name.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-size: 20px; font-weight: bold;")
        layout.addWidget(product_name)
        
        # Verbindungsdaten
        connection_group = QGroupBox("vCenter-Verbindungsdaten")
        connection_layout = QFormLayout()
        
        # Server
        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("vcenter.example.com")
        connection_layout.addRow("vCenter-Server:", self.server_edit)
        
        # Benutzername
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("administrator@vsphere.local")
        connection_layout.addRow("Benutzername:", self.username_edit)
        
        # Passwort
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        connection_layout.addRow("Passwort:", self.password_edit)
        
        # SSL-Zertifikatsüberprüfung
        self.ignore_ssl_check = QCheckBox("SSL-Zertifikatsüberprüfung ignorieren")
        self.ignore_ssl_check.setChecked(True)
        connection_layout.addRow("", self.ignore_ssl_check)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        
        # Style für Buttons
        for button in button_box.buttons():
            if button_box.buttonRole(button) == QDialogButtonBox.AcceptRole:
                button.setText("Verbinden")
                button.setStyleSheet(f"""
                    background-color: {BECHTLE_DARK_BLUE};
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                """)
            elif button_box.buttonRole(button) == QDialogButtonBox.RejectRole:
                button.setText("Abbrechen")
                
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def validate_and_accept(self):
        """Validiere die Eingaben und akzeptiere den Dialog"""
        self.server = self.server_edit.text().strip()
        self.username = self.username_edit.text().strip()
        self.password = self.password_edit.text()
        self.ignore_ssl = self.ignore_ssl_check.isChecked()
        
        # Validiere Eingaben
        if not self.server:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte geben Sie die vCenter-Serveradresse ein.")
            return
            
        if not self.username:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte geben Sie einen Benutzernamen ein.")
            return
            
        if not self.password:
            QMessageBox.warning(self, "Fehlende Eingabe", "Bitte geben Sie ein Passwort ein.")
            return
            
        self.logger.info(f"Verbindungsparameter validiert für Server {self.server}")
        
        # Dialog akzeptieren
        self.accept()