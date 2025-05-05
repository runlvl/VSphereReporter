#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Fehlerbehandlungsmodul für benutzerfreundliche Fehlermeldungen
"""

import logging
import re
import ssl
import socket
from urllib.error import URLError
from http.client import HTTPException
import requests.exceptions
from ssl import SSLError
import pyVmomi
from pyVmomi import vim

logger = logging.getLogger('vsphere_reporter')

# Fehlerklassen nach Kategorie
CONNECTION_ERRORS = (
    ConnectionError,
    ConnectionRefusedError,
    ConnectionResetError,
    ConnectionAbortedError,
    socket.timeout,
    socket.error,
    TimeoutError,
    URLError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    SSLError,
    ssl.SSLError,
    HTTPException
)

AUTHENTICATION_ERRORS = (
    vim.fault.InvalidLogin,
    vim.fault.NoPermission,
    vim.fault.NotAuthenticated
)

SERVER_ERRORS = (
    vim.fault.HostDisconnected,
    vim.fault.NotFound,
    vim.fault.ResourceInUse,
    vim.fault.TaskInProgress,
    vim.fault.InvalidState
)

PERMISSION_ERRORS = (
    vim.fault.NoPermission,
    vim.fault.AuthMinimumAdminPermission
)

def friendly_error_message(exception):
    """
    Konvertiert technische Fehlermeldungen in benutzerfreundliche Nachrichten
    
    Args:
        exception: Die aufgetretene Exception
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    logger.debug(f"Fehlerbehandlung für Exception: {type(exception).__name__}: {str(exception)}")
    
    # Verbindungsfehler
    if isinstance(exception, CONNECTION_ERRORS):
        return _handle_connection_error(exception)
    
    # Authentifizierungsfehler
    elif isinstance(exception, AUTHENTICATION_ERRORS):
        return _handle_authentication_error(exception)
    
    # Server-Fehler
    elif isinstance(exception, SERVER_ERRORS):
        return _handle_server_error(exception)
    
    # Berechtigungsfehler
    elif isinstance(exception, PERMISSION_ERRORS):
        return _handle_permission_error(exception)
    
    # VMware spezifische Fehler
    elif isinstance(exception, vim.fault.VimFault):
        return _handle_vim_fault(exception)
    
    # Generische Fehler
    else:
        return _handle_generic_error(exception)

def _handle_connection_error(exception):
    """
    Behandelt Verbindungsfehler
    
    Args:
        exception: Die aufgetretene Exception
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    error_message = str(exception)
    
    if isinstance(exception, (SSLError, ssl.SSLError)):
        return "SSL-Fehler beim Verbinden mit dem vCenter. Bitte aktivieren Sie die Option 'Selbstsignierte SSL-Zertifikate ignorieren' oder stellen Sie sicher, dass das Zertifikat des Servers gültig ist."
    
    elif isinstance(exception, (socket.timeout, TimeoutError, requests.exceptions.Timeout)):
        return "Zeitüberschreitung bei der Verbindung zum vCenter-Server. Bitte überprüfen Sie die Netzwerkverbindung und stellen Sie sicher, dass der Server erreichbar ist."
    
    elif isinstance(exception, (ConnectionRefusedError, requests.exceptions.ConnectionError)) or "connection refused" in error_message.lower():
        return "Verbindung zum vCenter-Server wurde verweigert. Bitte überprüfen Sie die Serveradresse und stellen Sie sicher, dass der Server läuft und über Port 443 erreichbar ist."
    
    elif "certificate verify failed" in error_message.lower():
        return "Die Überprüfung des SSL-Zertifikats ist fehlgeschlagen. Bitte aktivieren Sie die Option 'Selbstsignierte SSL-Zertifikate ignorieren'."
    
    elif "unknown host" in error_message.lower() or "name or service not known" in error_message.lower():
        return "Der angegebene Hostname konnte nicht aufgelöst werden. Bitte überprüfen Sie die Serveradresse."
    
    else:
        return f"Verbindungsfehler: {str(exception)}"

def _handle_authentication_error(exception):
    """
    Behandelt Authentifizierungsfehler
    
    Args:
        exception: Die aufgetretene Exception
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    if isinstance(exception, vim.fault.InvalidLogin):
        return "Ungültiger Benutzername oder Passwort. Bitte überprüfen Sie Ihre Anmeldeinformationen."
    
    elif isinstance(exception, vim.fault.NotAuthenticated):
        return "Authentifizierungsfehler. Bitte melden Sie sich erneut an."
    
    else:
        return f"Authentifizierungsfehler: {str(exception)}"

def _handle_server_error(exception):
    """
    Behandelt Server-Fehler
    
    Args:
        exception: Die aufgetretene Exception
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    if isinstance(exception, vim.fault.HostDisconnected):
        return "Ein oder mehrere ESXi-Hosts sind nicht mit dem vCenter verbunden. Dies kann zu unvollständigen Berichten führen."
    
    elif isinstance(exception, vim.fault.NotFound):
        return "Eine angeforderte Ressource wurde auf dem Server nicht gefunden."
    
    elif isinstance(exception, vim.fault.ResourceInUse):
        return "Eine Ressource wird derzeit verwendet und kann nicht bearbeitet werden."
    
    elif isinstance(exception, vim.fault.TaskInProgress):
        return "Eine Aufgabe wird bereits ausgeführt. Bitte versuchen Sie es später erneut."
    
    elif isinstance(exception, vim.fault.InvalidState):
        return "Die Aktion kann im aktuellen Zustand nicht ausgeführt werden."
    
    else:
        return f"Server-Fehler: {str(exception)}"

def _handle_permission_error(exception):
    """
    Behandelt Berechtigungsfehler
    
    Args:
        exception: Die aufgetretene Exception
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    if isinstance(exception, vim.fault.NoPermission):
        return "Unzureichende Berechtigungen für diese Aktion. Bitte stellen Sie sicher, dass Ihr Benutzer mindestens Leserechte auf alle vSphere-Objekte hat."
    
    elif isinstance(exception, vim.fault.AuthMinimumAdminPermission):
        return "Diese Aktion erfordert Administratorrechte."
    
    else:
        return f"Berechtigungsfehler: {str(exception)}"

def _handle_vim_fault(exception):
    """
    Behandelt VMware spezifische Fehler
    
    Args:
        exception: Die aufgetretene Exception
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    # Extrahiere den Fehlertyp aus der Klassennamen
    error_type = type(exception).__name__
    error_message = str(exception)
    
    # Entferne den namespace und extrahiere den lesbaren Fehlernamen
    if error_type.startswith('vim.fault.'):
        error_type = error_type[10:]  # Entferne 'vim.fault.'
    
    # Formatiere den Fehlernamen für bessere Lesbarkeit
    error_type = re.sub(r'([a-z])([A-Z])', r'\1 \2', error_type)
    
    return f"vSphere-Fehler ({error_type}): {error_message}"

def _handle_generic_error(exception):
    """
    Behandelt generische Fehler
    
    Args:
        exception: Die aufgetretene Exception
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    error_type = type(exception).__name__
    error_message = str(exception)
    
    # Spezialbehandlung für bekannte Typen
    if error_type == 'AttributeError' and 'NoneType' in error_message:
        return "Fehler beim Zugriff auf eine Ressource: Ein erforderliches Objekt wurde nicht gefunden. Dies kann auf fehlende Daten oder Berechtigungen hinweisen."
    
    elif error_type == 'TypeError':
        return "Interner Fehler bei der Verarbeitung von Daten. Bitte melden Sie diesen Fehler dem Support."
    
    elif error_type == 'ValueError':
        return f"Ungültiger Wert: {error_message}"
    
    elif error_type == 'KeyError':
        return "Fehler beim Zugriff auf Daten: Ein erforderlicher Schlüssel wurde nicht gefunden."
    
    elif error_type == 'IndexError':
        return "Fehler beim Zugriff auf Daten: Index außerhalb des gültigen Bereichs."
    
    else:
        # Generische Nachricht für unbekannte Fehler
        return f"Ein Fehler ist aufgetreten: {error_type} - {error_message}"