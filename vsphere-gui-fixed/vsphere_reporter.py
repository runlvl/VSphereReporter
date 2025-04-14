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

# Set QT platform plugin for Linux environments
if platform.system() == 'Linux':
    os.environ['QT_QPA_PLATFORM'] = 'minimal'
    # For VNC display
    os.environ['DISPLAY'] = ':0'
    os.environ['QT_DEBUG_PLUGINS'] = '1'

from PyQt5.QtWidgets import QApplication

from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """Main entry point for the application"""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting VMware vSphere Reporter")
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("VMware vSphere Reporter")
    app.setApplicationVersion("1.0.0")
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()