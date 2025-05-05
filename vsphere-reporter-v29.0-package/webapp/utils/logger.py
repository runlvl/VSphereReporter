#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Logging-Konfiguration und Hilfsfunktionen
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

def configure_logging(logger_name, level=logging.INFO):
    """
    Konfiguriert das Logger-System mit einer Konsolen- und einer Dateiausgabe
    
    Args:
        logger_name: Name des Loggers
        level: Logging-Level (default: INFO)
        
    Returns:
        Ein konfigurierter Logger
    """
    # Logger erstellen
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Entferne alle bestehenden Handler, falls der Logger bereits existiert
    if logger.handlers:
        logger.handlers.clear()
    
    # Formatter erstellen
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Konsolen-Handler erstellen
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Log-Verzeichnis erstellen, falls es nicht existiert
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Dateinamen mit Datum generieren
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"vsphere_reporter_{timestamp}.log")
    
    # Datei-Handler erstellen
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialisiert (Level: {logging.getLevelName(level)})")
    logger.info(f"Log-Datei: {log_file}")
    
    return logger

def log_exception(logger, exception, message=None):
    """
    Protokolliert eine Exception mit Stacktrace
    
    Args:
        logger: Der Logger
        exception: Die zu protokollierende Exception
        message: Optionale Nachricht
    """
    if message:
        logger.error(f"{message}: {str(exception)}")
    else:
        logger.error(str(exception))
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_traceback:
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        logger.error("".join(tb_lines))