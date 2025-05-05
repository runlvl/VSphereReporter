#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VSphere Reporter Fehlerbehandlung
Dieses Modul stellt Funktionen und Klassen für die einheitliche Fehlerbehandlung bereit.
"""

import functools
import logging
import traceback

logger = logging.getLogger(__name__)

class VSphereReporterError(Exception):
    """Basisklasse für alle Fehler im VSphere Reporter"""
    pass

class ConnectionError(VSphereReporterError):
    """Fehler bei Verbindung zum vCenter"""
    pass

class AuthenticationError(VSphereReporterError):
    """Authentifizierungsfehler"""
    pass

class DataCollectionError(VSphereReporterError):
    """Fehler bei der Datensammlung"""
    pass

class ReportGenerationError(VSphereReporterError):
    """Fehler bei der Berichtsgenerierung"""
    pass

def handle_vsphere_errors(func):
    """
    Decorator für einheitliche Fehlerbehandlung in VSphere-bezogenen Funktionen
    
    Args:
        func: Die zu dekorierenden Funktion
        
    Returns:
        Decorator-Funktion
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except VSphereReporterError:
            # Eigene Fehlerklassen direkt weitergeben
            raise
        except Exception as e:
            # Detaillierte Fehlerausgabe im Debug-Modus
            error_details = f"{str(e)} ({type(e).__name__})"
            logger.error(f"Fehler in {func.__name__}: {error_details}")
            logger.debug(f"Stacktrace: {traceback.format_exc()}")
            
            # Allgemeinen Fehler in eigene Fehlerklasse umwandeln
            raise VSphereReporterError(f"Unerwarteter Fehler: {error_details}")
    
    return wrapper