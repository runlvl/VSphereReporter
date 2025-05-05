#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VSphere Reporter Logger
Konfiguriert Logging für die Anwendung
"""

import os
import logging
from datetime import datetime

def setup_logger(name='vsphere_reporter'):
    """
    Konfiguriert einen Logger mit Datei- und Konsolenausgabe
    
    Args:
        name: Name des Loggers
        
    Returns:
        logging.Logger: Konfigurierter Logger
    """
    # Logging-Format erstellen
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger erstellen
    logger = logging.getLogger(name)
    
    # Wenn Logger bereits Handler hat, nichts tun (vermeidet doppelte Handler)
    if logger.handlers:
        return logger
    
    # Standard-Loglevel
    logger.setLevel(logging.INFO)
    
    # Debug-Modus über Umgebungsvariable aktivieren
    if os.environ.get('VSPHERE_REPORTER_DEBUG', 'False').lower() in ('true', '1', 't'):
        logger.setLevel(logging.DEBUG)
    
    # Log-Ausgabe an Konsole
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # Log-Ausgabe in Datei
    try:
        # Stelle sicher, dass logs-Verzeichnis existiert
        os.makedirs('logs', exist_ok=True)
        
        # Eindeutiger Dateiname mit Zeitstempel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/{name}_{timestamp}.log'
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
        
        logger.debug(f"Logging in Datei {log_file} eingerichtet")
    except Exception as e:
        logger.warning(f"Fehler beim Einrichten des Datei-Loggers: {e}")
    
    return logger