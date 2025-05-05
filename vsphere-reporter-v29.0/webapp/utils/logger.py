#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Logger-Modul für einheitliche Protokollierung
"""

import os
import logging
import logging.handlers
from datetime import datetime

def setup_logger(name, log_folder='logs', debug=False):
    """
    Richtet einen Logger mit einheitlichem Format ein
    
    Args:
        name: Name des Loggers
        log_folder: Verzeichnis für Logdateien
        debug: Debug-Modus aktivieren (ausführlichere Logs)
        
    Returns:
        logging.Logger: Konfigurierter Logger
    """
    # Stellen Sie sicher, dass das Log-Verzeichnis existiert
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
    # Logger erstellen
    logger = logging.getLogger(name)
    
    # Log-Level basierend auf Debug-Modus festlegen
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Dateihandler für kontinuierliches Logging
    log_file = os.path.join(log_folder, f"{name}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    
    # Tägliche Log-Dateien für forensische Zwecke
    daily_log_file = os.path.join(
        log_folder, 
        f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    daily_file_handler = logging.FileHandler(daily_log_file, encoding='utf-8')
    
    # Konsolenhandler
    console_handler = logging.StreamHandler()
    
    # Formatierung für alle Handler
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Formatierung anwenden
    file_handler.setFormatter(formatter)
    daily_file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Level für Handler festlegen
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    daily_file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Handler hinzufügen, wenn noch nicht vorhanden
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(daily_file_handler)
        logger.addHandler(console_handler)
    
    return logger