#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter
A comprehensive reporting tool for VMware vSphere environments

This is the main entry point for the application.
"""

import sys
import os
import logging
import platform
import traceback

# Set QT platform plugin for Linux environments
if platform.system() == 'Linux':
    os.environ['QT_QPA_PLATFORM'] = 'minimal'
    # For VNC display
    os.environ['DISPLAY'] = ':0'
    os.environ['QT_DEBUG_PLUGINS'] = '1'

from PyQt5.QtWidgets import QApplication, QMessageBox

from gui.main_window import MainWindow
from utils.logger import setup_logger

# Globaler Exception-Handler
def global_exception_handler(exctype, value, tb):
    """
    Globaler Exception-Handler, um Abstürze zu verhindern und Fehlermeldungen anzuzeigen
    """
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    
    logger = logging.getLogger(__name__)
    logger.critical(f"Unbehandelte Ausnahme: {error_msg}")
    
    # Zeige Fehlermeldung an
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Fehler")
    msg_box.setText("Ein unerwarteter Fehler ist aufgetreten:")
    msg_box.setDetailedText(error_msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
    
    # Originalen sys.excepthook aufrufen
    sys.__excepthook__(exctype, value, tb)

def main():
    """Main entry point for the application"""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting VMware vSphere Reporter")
    
    # Globalen Exception-Handler installieren
    sys.excepthook = global_exception_handler
    logger.info("Globaler Exception-Handler installiert")
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("VMware vSphere Reporter")
    app.setApplicationVersion("24.1.0")
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()