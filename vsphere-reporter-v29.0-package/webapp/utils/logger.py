#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Logger-Modul für konsistentes Logging in der gesamten Anwendung
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import datetime

def setup_logger(name, log_dir=None, debug_mode=False):
    """
    Richtet einen Logger mit konsistenter Formatierung ein
    
    Args:
        name: Name des Loggers
        log_dir: Verzeichnis für Logdateien (optional)
        debug_mode: True für Debug-Modus mit ausführlicheren Logs
        
    Returns:
        logging.Logger: Konfigurierter Logger
    """
    # Logger erstellen
    logger = logging.getLogger(name)
    
    # Bestehende Handler entfernen, um doppeltes Logging zu vermeiden
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Level basierend auf Debug-Modus setzen
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    
    # Formatierung für reguläre Logs
    regular_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    # Formatierung für Debug-Logs
    debug_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s',
        '%Y-%m-%d %H:%M:%S'
    )
    
    # Konsolenausgabe
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    console_handler.setFormatter(debug_formatter if debug_mode else regular_formatter)
    logger.addHandler(console_handler)
    
    # Datei-Logging, falls ein Verzeichnis angegeben ist
    if log_dir:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_dir, f'{name}_{timestamp}.log')
        
        # Reguläre Logdatei
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        file_handler.setFormatter(debug_formatter if debug_mode else regular_formatter)
        logger.addHandler(file_handler)
        
        # Separate Fehler-Logdatei
        error_log_file = os.path.join(log_dir, f'{name}_{timestamp}_error.log')
        error_file_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(debug_formatter)
        logger.addHandler(error_file_handler)
    
    # Log-Nachricht zur Initialisierung
    logger.info(f"Logger '{name}' initialisiert (Debug-Modus: {'Aktiv' if debug_mode else 'Inaktiv'})")
    
    return logger

class BrowserConsoleHandler(logging.Handler):
    """
    Spezieller Handler, der Logs an die Browserkonsole sendet
    Wird verwendet, um Logs über die JavaScript-Konsole des Browsers für Frontend-Debugging anzuzeigen
    """
    def __init__(self):
        """Initialisiert den Browser-Konsolen-Handler"""
        super().__init__()
        self.logs = []
    
    def emit(self, record):
        """
        Fügt einen Logeintrag hinzu
        
        Args:
            record: Der Logeintrag
        """
        try:
            log_entry = self.format(record)
            self.logs.append({
                'time': record.created,
                'level': record.levelname,
                'message': log_entry
            })
            
            # Begrenze die Anzahl der gespeicherten Logs
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]
        except Exception:
            self.handleError(record)
    
    def get_logs(self, level=None, limit=100):
        """
        Gibt die gespeicherten Logs zurück
        
        Args:
            level: Optional Loglevel-Filter (z.B. 'DEBUG', 'INFO', 'ERROR')
            limit: Maximale Anzahl der zurückgegebenen Logs
            
        Returns:
            list: Gefilterte Logs
        """
        if level:
            filtered_logs = [log for log in self.logs if log['level'] == level]
        else:
            filtered_logs = self.logs
        
        return filtered_logs[-limit:]
    
    def clear(self):
        """Löscht alle gespeicherten Logs"""
        self.logs = []