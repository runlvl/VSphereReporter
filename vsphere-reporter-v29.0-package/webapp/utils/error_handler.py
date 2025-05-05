#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Fehlerbehandlung und -management
"""

import logging
import traceback
import sys
from functools import wraps

class VSphereReporterError(Exception):
    """Basisklasse für alle VSphere Reporter-spezifischen Fehler"""
    pass

class ConnectionError(VSphereReporterError):
    """Fehler bei der Verbindung zum vCenter"""
    pass

class AuthenticationError(VSphereReporterError):
    """Fehler bei der Authentifizierung am vCenter"""
    pass

class VMDKError(VSphereReporterError):
    """Fehler bei der VMDK-Verarbeitung"""
    pass

class ReportGenerationError(VSphereReporterError):
    """Fehler bei der Berichtsgenerierung"""
    pass

def handle_vsphere_error(logger=None):
    """
    Dekorator zur Behandlung von vSphere-spezifischen Fehlern
    
    Args:
        logger: Optional, ein Logger-Objekt
        
    Returns:
        Dekorierte Funktion
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Hole den Stacktrace
                exc_type, exc_value, exc_traceback = sys.exc_info()
                stack_trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
                
                # Extrahiere Klassenname und Modulname für bessere Fehlermeldungen
                func_name = func.__name__
                module_name = func.__module__
                
                # Erstelle Fehlermeldung
                error_message = f"Fehler in {module_name}.{func_name}: {str(e)}"
                
                # Protokolliere den Fehler, wenn ein Logger übergeben wurde
                if logger:
                    logger.error(error_message)
                    logger.error("".join(stack_trace))
                
                # Übersetze spezifische vSphere-Fehler in unsere eigenen Fehlerklassen
                try:
                    # pyVmomi-Fehler-Behandlung
                    import pyVmomi
                    from pyVmomi import vim
                    
                    if isinstance(e, vim.fault.InvalidLogin):
                        raise AuthenticationError("Ungültige Anmeldedaten") from e
                    elif isinstance(e, (vim.fault.HostConnectFault, vim.fault.NotAuthenticated)):
                        raise ConnectionError(f"Verbindungsproblem: {str(e)}") from e
                    # Füge weitere vSphere-spezifische Fehlerbehandlungen hinzu
                except ImportError:
                    # pyVmomi ist nicht verfügbar, ignoriere die spezifische Behandlung
                    pass
                
                # Reiche den ursprünglichen Fehler weiter, wenn er nicht behandelt wurde
                raise
        
        return wrapper
    
    return decorator

def format_exception(exception):
    """
    Formatiert eine Exception für die Anzeige
    
    Args:
        exception: Die zu formatierende Exception
        
    Returns:
        str: Formatierte Fehlermeldung
    """
    if isinstance(exception, VSphereReporterError):
        # Für unsere eigenen Fehler zeigen wir nur die Meldung an
        return str(exception)
    else:
        # Für andere Fehler zeigen wir den Typ und die Meldung an
        return f"{type(exception).__name__}: {str(exception)}"