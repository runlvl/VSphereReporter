"""
VSphere Reporter Logger-Modul
"""

import os
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(name="vsphere_reporter", log_level=logging.INFO, log_dir="logs"):
    """
    Konfiguriert den Logger für die Anwendung.
    
    Args:
        name: Name des Loggers
        log_level: Logging-Level (INFO, DEBUG, ERROR, etc.)
        log_dir: Verzeichnis für Logdateien
        
    Returns:
        Ein konfigurierter Logger
    """
    logger = logging.getLogger(name)
    
    # Stelle sicher, dass der Logger nur einmal konfiguriert wird
    if logger.handlers:
        return logger
    
    # Setze den Logging-Level
    logger.setLevel(log_level)
    
    # Erstelle das Log-Verzeichnis, falls es nicht existiert
    Path(log_dir).mkdir(exist_ok=True)
    
    # Erstelle einen Handler für Konsolenausgaben
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Erstelle einen Handler für Dateiausgaben
    log_file = os.path.join(log_dir, f"vsphere_reporter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Erstelle ein Formatierungsmuster
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Füge die Handler dem Logger hinzu
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger