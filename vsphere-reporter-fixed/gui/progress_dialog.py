#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Progress Dialog
Dialogfenster zur Anzeige von Fortschritten bei langwierigen Operationen
"""

import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar, 
                            QPushButton, QHBoxLayout, QSpacerItem,
                            QSizePolicy)
from PyQt5.QtCore import Qt, QTimer

# Bechtle-Farbschema
BECHTLE_DARK_BLUE = "#00355e"
BECHTLE_ORANGE = "#da6f1e"
BECHTLE_GREEN = "#23a96a"
BECHTLE_LIGHT_GRAY = "#f3f3f3"
BECHTLE_DARK_GRAY = "#5a5a5a"

class ProgressDialog(QDialog):
    """Dialog zur Anzeige des Fortschritts bei langwierigen Operationen"""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Verhindere Schließen per Escape oder X-Button
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        layout = QVBoxLayout()
        
        # Statusnachricht
        self.status_label = QLabel(message)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Fortschrittsbalken
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Unbestimmter Fortschritt
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {BECHTLE_LIGHT_GRAY};
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {BECHTLE_DARK_BLUE};
            }}
        """)
        layout.addWidget(self.progress_bar)
        
        # Animation für Fortschrittsbalken
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress_animation)
        self.timer.start(100)
        
        # "Abbrechen"-Button (optional)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setVisible(False)  # Standardmäßig nicht sichtbar
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def _update_progress_animation(self):
        """Aktualisiert den Fortschrittsbalken für ein animiertes Erscheinungsbild"""
        pass  # QProgressBar mit range (0,0) animiert automatisch
        
    def update_status(self, message):
        """Aktualisiere die Statusnachricht"""
        self.status_label.setText(message)
        self.logger.debug(f"Fortschrittsstatus aktualisiert: {message}")
        
    def enable_cancel(self, slot=None):
        """Aktiviere den Abbrechen-Button und verbinde ihn optional mit einer Funktion"""
        self.cancel_button.setVisible(True)
        
        if slot:
            # Trenne alle bestehenden Verbindungen
            try:
                self.cancel_button.clicked.disconnect()
            except TypeError:
                pass  # Keine Verbindungen vorhanden
                
            # Verbinde mit neuer Funktion
            self.cancel_button.clicked.connect(slot)
        
    def closeEvent(self, event):
        """Wird aufgerufen, wenn der Dialog geschlossen wird"""
        self.timer.stop()
        event.accept()