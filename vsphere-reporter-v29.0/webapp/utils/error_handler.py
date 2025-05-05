#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Fehlerbehandlungsmodul
"""

import logging
import traceback
import socket
from ssl import SSLError

import pyVmomi

logger = logging.getLogger('vsphere_reporter')

# Bekannte Fehlermeldungen und benutzerfreundliche Übersetzungen
ERROR_MESSAGES = {
    # Verbindungsfehler
    "ConnectionRefusedError": "Der vCenter-Server hat die Verbindung verweigert. Bitte überprüfen Sie die Server-Adresse und ob der Server erreichbar ist.",
    "ConnectionResetError": "Die Verbindung wurde vom vCenter-Server zurückgesetzt. Bitte versuchen Sie es erneut oder prüfen Sie Ihre Netzwerkverbindung.",
    "socket.timeout": "Die Verbindung zum vCenter-Server hat das Zeitlimit überschritten. Bitte überprüfen Sie Ihre Netzwerkverbindung.",
    "SSLError": "SSL/TLS-Fehler bei der Verbindung. Aktivieren Sie die Option 'SSL-Zertifikat ignorieren' oder stellen Sie sicher, dass Ihr SSL-Zertifikat gültig ist.",
    
    # Authentifizierungsfehler
    "InvalidLogin": "Ungültige Anmeldedaten. Bitte überprüfen Sie Benutzernamen und Passwort.",
    "NoPermission": "Keine ausreichenden Berechtigungen. Der angegebene Benutzer hat nicht die erforderlichen Rechte.",
    
    # API-Fehler
    "NotAuthenticated": "Nicht authentifiziert. Bitte melden Sie sich erneut an.",
    "NotFound": "Das angeforderte Element wurde nicht gefunden.",
    "InvalidRequest": "Ungültige Anfrage. Bitte versuchen Sie es mit anderen Parametern.",
    
    # VMDK-spezifische Fehler
    "FileNotFound": "Die VMDK-Datei wurde nicht gefunden.",
    "DiskNotAccessible": "Auf die Festplatte konnte nicht zugegriffen werden. Möglicherweise haben Sie keine ausreichenden Berechtigungen.",
    
    # Allgemeine Fehler
    "TimeoutError": "Zeitüberschreitung bei der Operation. Der Server antwortet nicht rechtzeitig.",
    "ServerError": "Interner Serverfehler im vCenter. Bitte kontaktieren Sie Ihren VMware-Administrator.",
    "UnknownError": "Ein unbekannter Fehler ist aufgetreten. Überprüfen Sie die Protokolle für weitere Details."
}

class VSphereError(Exception):
    """Basisklasse für alle vSphere-spezifischen Fehler"""
    def __init__(self, message, original_error=None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

class ConnectionError(VSphereError):
    """Fehler bei der Verbindung zum vCenter"""
    pass

class AuthenticationError(VSphereError):
    """Fehler bei der Authentifizierung"""
    pass

class APIError(VSphereError):
    """Fehler bei API-Aufrufen"""
    pass

class VMDKError(VSphereError):
    """Fehler im Zusammenhang mit VMDK-Dateien"""
    pass

class GeneralError(VSphereError):
    """Allgemeine Fehler"""
    pass

def handle_vsphere_error(func):
    """
    Dekorator zur einheitlichen Fehlerbehandlung für vSphere-Operationen
    
    Args:
        func: Die zu dekorierende Funktion
        
    Returns:
        Die dekorierte Funktion mit Fehlerbehandlung
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except socket.error as e:
            error_type = type(e).__name__
            error_msg = ERROR_MESSAGES.get(error_type, str(e))
            logger.error(f"Netzwerkfehler: {error_msg} - Original: {str(e)}")
            raise ConnectionError(error_msg, e)
        except SSLError as e:
            error_msg = ERROR_MESSAGES.get("SSLError", str(e))
            logger.error(f"SSL-Fehler: {error_msg} - Original: {str(e)}")
            raise ConnectionError(error_msg, e)
        except pyVmomi.vim.fault.InvalidLogin as e:
            error_msg = ERROR_MESSAGES.get("InvalidLogin", str(e))
            logger.error(f"Authentifizierungsfehler: {error_msg} - Original: {str(e)}")
            raise AuthenticationError(error_msg, e)
        except pyVmomi.vim.fault.NoPermission as e:
            error_msg = ERROR_MESSAGES.get("NoPermission", str(e))
            logger.error(f"Berechtigungsfehler: {error_msg} - Original: {str(e)}")
            raise AuthenticationError(error_msg, e)
        except Exception as e:
            error_type = type(e).__name__
            error_msg = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES.get("UnknownError", str(e)))
            logger.error(f"Unbehandelter Fehler: {error_msg} - Original: {str(e)}")
            logger.debug(f"Fehler-Stacktrace: {traceback.format_exc()}")
            raise GeneralError(error_msg, e)
    return wrapper

def friendly_error_message(exception):
    """
    Erzeugt eine benutzerfreundliche Fehlermeldung aus einer Ausnahme
    
    Args:
        exception: Die aufgetretene Ausnahme
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    if isinstance(exception, VSphereError):
        return exception.message
    
    error_type = type(exception).__name__
    return ERROR_MESSAGES.get(error_type, f"Fehler: {str(exception)}")