#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Error Handler

Dieses Modul stellt Funktionen für die einheitliche Fehlerbehandlung bereit,
insbesondere für Fehler, die bei der Verbindung mit vSphere auftreten können.

Copyright (c) 2025 Bechtle GmbH
"""

import logging
import functools
import ssl
import socket
from datetime import datetime

# pyVmomi Imports
try:
    from pyVmomi import vim
    from pyVmomi import vmodl
except ImportError:
    # Fallback für Demo-Modus oder wenn pyVmomi nicht installiert ist
    vim = type('vim', (), {'fault': type('fault', (), {})})
    vmodl = type('vmodl', (), {'fault': type('fault', (), {})})

logger = logging.getLogger(__name__)

class VSphereReporterError(Exception):
    """Basisklasse für alle VSphere Reporter-spezifischen Fehler"""
    pass

class VSphereConnectionError(VSphereReporterError):
    """Fehler bei der Verbindung zum vCenter"""
    pass

class VSphereAuthenticationError(VSphereReporterError):
    """Fehler bei der Authentifizierung am vCenter"""
    pass

class VSpherePermissionError(VSphereReporterError):
    """Fehler bei fehlenden Berechtigungen"""
    pass

class VSphereNetworkError(VSphereReporterError):
    """Netzwerkfehler bei der Kommunikation mit dem vCenter"""
    pass

class VSphereTimeoutError(VSphereReporterError):
    """Timeout bei der Kommunikation mit dem vCenter"""
    pass

class VSphereDataCollectionError(VSphereReporterError):
    """Fehler bei der Datensammlung"""
    pass

class VSphereReportGenerationError(VSphereReporterError):
    """Fehler bei der Berichtsgenerierung"""
    pass

def log_error(error, level=logging.ERROR):
    """
    Protokolliert einen Fehler mit zusätzlichen Kontextinformationen
    
    Args:
        error: Der aufgetretene Fehler
        level: Log-Level (default: ERROR)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_type = type(error).__name__
    error_message = str(error)
    
    logger.log(level, f"[{timestamp}] {error_type}: {error_message}")

def handle_vsphere_errors(func):
    """
    Decorator für die einheitliche Fehlerbehandlung von vSphere-Operationen
    
    Args:
        func: Die zu dekorierende Funktion
        
    Returns:
        Die dekorierte Funktion mit Fehlerbehandlung
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except vim.fault.InvalidLogin as e:
            log_error(e)
            raise VSphereAuthenticationError(f"Ungültige Anmeldedaten: {str(e)}")
        except vim.fault.NoPermission as e:
            log_error(e)
            raise VSpherePermissionError(f"Keine ausreichenden Berechtigungen: {str(e)}")
        except vim.fault.NotAuthenticated as e:
            log_error(e)
            raise VSphereAuthenticationError(f"Nicht authentifiziert: {str(e)}")
        except vim.fault.HostConnectFault as e:
            log_error(e)
            raise VSphereConnectionError(f"Verbindungsfehler zum Host: {str(e)}")
        except vmodl.fault.NotSupported as e:
            log_error(e)
            raise VSphereReporterError(f"Operation wird nicht unterstützt: {str(e)}")
        except ssl.SSLError as e:
            log_error(e)
            raise VSphereConnectionError(f"SSL-Fehler: {str(e)}. Aktivieren Sie die Option 'SSL-Zertifikatsvalidierung ignorieren'.")
        except socket.timeout as e:
            log_error(e)
            raise VSphereTimeoutError(f"Zeitüberschreitung bei der Verbindung: {str(e)}")
        except socket.error as e:
            log_error(e)
            raise VSphereNetworkError(f"Netzwerkfehler: {str(e)}")
        except Exception as e:
            log_error(e)
            raise VSphereReporterError(f"Unerwarteter Fehler: {str(e)}")
    
    return wrapper

def format_vsphere_error(error):
    """
    Formatiert einen vSphere-Fehler in eine benutzerfreundliche Nachricht
    
    Args:
        error: Der aufgetretene Fehler
        
    Returns:
        str: Eine benutzerfreundliche Fehlermeldung
    """
    if isinstance(error, VSphereAuthenticationError):
        return f"Authentifizierungsfehler: {str(error)}"
    elif isinstance(error, VSpherePermissionError):
        return f"Berechtigungsfehler: {str(error)}"
    elif isinstance(error, VSphereConnectionError):
        return f"Verbindungsfehler: {str(error)}"
    elif isinstance(error, VSphereTimeoutError):
        return f"Zeitüberschreitung: {str(error)}"
    elif isinstance(error, VSphereNetworkError):
        return f"Netzwerkfehler: {str(error)}"
    elif isinstance(error, VSphereDataCollectionError):
        return f"Fehler bei der Datensammlung: {str(error)}"
    elif isinstance(error, VSphereReportGenerationError):
        return f"Fehler bei der Berichtsgenerierung: {str(error)}"
    elif isinstance(error, VSphereReporterError):
        return f"vSphere Reporter Fehler: {str(error)}"
    else:
        return f"Unerwarteter Fehler: {str(error)}"