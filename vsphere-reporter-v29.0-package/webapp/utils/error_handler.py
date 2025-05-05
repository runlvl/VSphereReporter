#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Copyright (c) 2025 Bechtle GmbH

Fehlerbehandlungsmodul für den vSphere Reporter.
"""

import logging
import ssl
import socket
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast

# Versuche, die vSphere-API zu importieren
try:
    import pyVmomi
    from pyVmomi import vim
except ImportError:
    vim = type('vim', (), {})  # Erstelle ein Dummy-Objekt, wenn die Bibliothek nicht verfügbar ist

logger = logging.getLogger(__name__)

# Benutzerdefinierte Ausnahmen
class VSphereError(Exception):
    """Basisklasse für alle vSphere-bezogenen Fehler."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ConnectionError(VSphereError):
    """Fehler bei der Verbindung zum vCenter-Server."""
    
    def __init__(self, server: str, message: str):
        self.server = server
        full_message = f"Verbindungsfehler zum Server {server}: {message}"
        super().__init__(full_message)

class AuthenticationError(VSphereError):
    """Fehler bei der Authentifizierung am vCenter-Server."""
    
    def __init__(self, server: str, username: str, message: str):
        self.server = server
        self.username = username
        full_message = f"Authentifizierungsfehler für Benutzer {username} am Server {server}: {message}"
        super().__init__(full_message)

class PermissionError(VSphereError):
    """Fehlende Berechtigungen für eine Operation."""
    
    def __init__(self, operation: str, message: str):
        self.operation = operation
        full_message = f"Berechtigungsfehler bei Operation '{operation}': {message}"
        super().__init__(full_message)

class OperationError(VSphereError):
    """Fehler bei der Ausführung einer Operation."""
    
    def __init__(self, operation: str, message: str):
        self.operation = operation
        full_message = f"Fehler bei Operation '{operation}': {message}"
        super().__init__(full_message)

F = TypeVar('F', bound=Callable[..., Any])

def handle_vsphere_error(func: F) -> F:
    """
    Dekorator zur Behandlung von vSphere-spezifischen Fehlern.
    
    Fängt verschiedene Ausnahmen ab und wandelt sie in spezifische VSphereError-Unterklassen um.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except vim.fault.HostConnectFault as e:
            # Allgemeiner Verbindungsfehler zum Host
            logger.error(f"Verbindungsfehler zum Host: {str(e)}")
            self = args[0] if args else None
            server = getattr(self, 'host', 'Unbekannter Server')
            raise ConnectionError(server, str(e))
        except vim.fault.InvalidLogin as e:
            # Ungültige Anmeldedaten
            logger.error(f"Ungültige Anmeldedaten: {str(e)}")
            self = args[0] if args else None
            server = getattr(self, 'host', 'Unbekannter Server')
            username = getattr(self, 'username', 'Unbekannter Benutzer')
            raise AuthenticationError(server, username, str(e))
        except vim.fault.NoPermission as e:
            # Fehlende Berechtigungen
            logger.error(f"Fehlende Berechtigungen: {str(e)}")
            operation = func.__name__
            raise PermissionError(operation, str(e))
        except ssl.SSLError as e:
            # SSL-Fehler
            logger.error(f"SSL-Fehler: {str(e)}")
            self = args[0] if args else None
            server = getattr(self, 'host', 'Unbekannter Server')
            raise ConnectionError(server, f"SSL-Fehler: {str(e)}")
        except (socket.error, socket.timeout) as e:
            # Netzwerkfehler
            logger.error(f"Netzwerkfehler: {str(e)}")
            self = args[0] if args else None
            server = getattr(self, 'host', 'Unbekannter Server')
            raise ConnectionError(server, f"Netzwerkfehler: {str(e)}")
        except Exception as e:
            # Sonstige Fehler
            logger.exception(f"Unerwarteter Fehler: {str(e)}")
            operation = func.__name__
            raise OperationError(operation, str(e))
    
    return cast(F, wrapper)

def format_exception(e: Exception) -> Dict[str, Any]:
    """
    Formatiert eine Ausnahme als Dictionary für die Verwendung in Fehlerantworten.
    
    Args:
        e: Die zu formatierende Ausnahme
        
    Returns:
        Ein Dictionary mit Fehlerinformationen
    """
    error_info = {
        'type': e.__class__.__name__,
        'message': str(e),
        'details': {}
    }
    
    if isinstance(e, ConnectionError):
        error_info['details']['server'] = e.server
    elif isinstance(e, AuthenticationError):
        error_info['details']['server'] = e.server
        error_info['details']['username'] = e.username
    elif isinstance(e, PermissionError):
        error_info['details']['operation'] = e.operation
    elif isinstance(e, OperationError):
        error_info['details']['operation'] = e.operation
    
    return error_info

def log_exception(e: Exception, logger: logging.Logger) -> None:
    """
    Protokolliert eine Ausnahme mit dem angegebenen Logger.
    
    Args:
        e: Die zu protokollierende Ausnahme
        logger: Der zu verwendende Logger
    """
    if isinstance(e, ConnectionError):
        logger.error(f"Verbindungsfehler: {str(e)}")
    elif isinstance(e, AuthenticationError):
        logger.error(f"Authentifizierungsfehler: {str(e)}")
    elif isinstance(e, PermissionError):
        logger.error(f"Berechtigungsfehler: {str(e)}")
    elif isinstance(e, OperationError):
        logger.error(f"Operationsfehler: {str(e)}")
    else:
        logger.exception(f"Unbehandelter Fehler: {str(e)}")