#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fehlerbehandlungsmodul für den VMware vSphere Reporter
Stellt erweiterte Fehlerbehandlungsfunktionen für alle Anwendungsteile bereit
"""

import os
import sys
import logging
import traceback
import datetime
import tempfile

logger = logging.getLogger(__name__)

def setup_error_logging(log_dir=None):
    """
    Konfiguriert die erweiterte Fehlerprotokollierung
    
    Args:
        log_dir: Optionales Verzeichnis für Protokolldateien. Standardmäßig wird ein Logs-Verzeichnis verwendet.
    """
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    
    # Erstelle das Verzeichnis, falls es nicht existiert
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            # Fallback auf das temporäre Verzeichnis, wenn das Log-Verzeichnis nicht erstellt werden kann
            log_dir = tempfile.gettempdir()
    
    # Generiere einen Dateinamen mit aktuellem Zeitstempel
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'vsphere_error_{timestamp}.log')
    
    # Konfiguriere den Datei-Handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Füge den Handler zum Root-Logger hinzu
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    return log_file

def log_exception(e, context=None):
    """
    Protokolliert eine Ausnahme mit vollständigem Traceback und Kontext
    
    Args:
        e: Die aufgetretene Exception
        context: Optionale kontextuelle Informationen
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    
    error_message = f"Exception: {str(e)}"
    if context:
        error_message += f"\nKontext: {context}"
    
    error_message += "\n" + "".join(tb_lines)
    
    logger.error(error_message)
    
    return error_message

def get_user_friendly_error_message(e):
    """
    Erzeugt eine benutzerfreundliche Fehlermeldung aus einer Exception
    
    Args:
        e: Die aufgetretene Exception
        
    Returns:
        str: Benutzerfreundliche Fehlermeldung
    """
    error_type = type(e).__name__
    error_message = str(e)
    
    # Angepasste benutzerfreundliche Nachrichten für häufige Fehler
    if "ConnectionRefused" in error_type or "ConnectionError" in error_type:
        return "Verbindung zum vCenter Server konnte nicht hergestellt werden. Bitte überprüfen Sie die Verbindungseinstellungen und versuchen Sie es erneut."
    
    elif "AuthenticationError" in error_type or "Invalid username or password" in error_message:
        return "Anmeldefehler: Ungültiger Benutzername oder Passwort. Bitte überprüfen Sie Ihre Anmeldedaten."
    
    elif "SSLError" in error_type or "certificate verify failed" in error_message:
        return "SSL-Fehler: Die sichere Verbindung konnte nicht hergestellt werden. Bitte aktivieren Sie die Option 'SSL-Zertifikat ignorieren', wenn Sie selbst-signierte Zertifikate verwenden."
    
    elif "Permission" in error_type or "Permission" in error_message:
        return "Berechtigungsfehler: Der angegebene Benutzer verfügt nicht über ausreichende Berechtigungen für diese Operation."
    
    elif "Timeout" in error_type or "timed out" in error_message:
        return "Zeitüberschreitung: Der Server hat nicht rechtzeitig geantwortet. Bitte überprüfen Sie die Netzwerkverbindung und versuchen Sie es erneut."
    
    elif "FileNotFound" in error_type or "No such file" in error_message:
        return "Datei nicht gefunden: Die angeforderte Datei oder das Verzeichnis existiert nicht."
    
    elif "PermissionError" in error_type and ("access" in error_message.lower() or "permission" in error_message.lower()):
        return "Zugriffsfehler: Keine ausreichenden Berechtigungen für den Zugriff auf eine Datei oder ein Verzeichnis."
    
    elif "DiskFull" in error_type or "No space left" in error_message:
        return "Nicht genügend Speicherplatz: Bitte stellen Sie sicher, dass ausreichend freier Speicherplatz zur Verfügung steht."
    
    # Fallback für unbekannte Fehler
    return f"Ein Fehler ist aufgetreten: {error_message}"

class ErrorHandler:
    """
    Zentrale Fehlerbehandlungsklasse für konsistente Fehlerbehandlung
    """
    
    @staticmethod
    def handle_error(e, context=None, show_traceback=False):
        """
        Verarbeitet eine Exception mit Protokollierung und benutzerfreundlicher Fehlermeldung
        
        Args:
            e: Die aufgetretene Exception
            context: Optionale kontextuelle Informationen
            show_traceback: Boolean, ob der Traceback in der Rückgabe enthalten sein soll
            
        Returns:
            dict: Fehlerinformationen mit benutzerfreundlicher Nachricht und optionalem Traceback
        """
        # Protokolliere den vollständigen Fehler
        error_log = log_exception(e, context)
        
        # Generiere benutzerfreundliche Nachricht
        user_message = get_user_friendly_error_message(e)
        
        # Erstelle die Rückgabeinformationen
        error_info = {
            "message": user_message,
            "error_type": type(e).__name__,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if context:
            error_info["context"] = context
            
        if show_traceback:
            error_info["traceback"] = error_log
            
        return error_info