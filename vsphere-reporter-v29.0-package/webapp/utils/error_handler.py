#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Fehlerbehandlung
Copyright (c) 2025 Bechtle GmbH

Modul für die Fehlerbehandlung und benutzerdefinierte Ausnahmen
"""

import logging
from functools import wraps
import ssl
import socket

# Im Demo-Modus benötigen wir keine VMware-Abhängigkeiten
try:
    import vim
    from pyVmomi.vim import fault
except ImportError:
    # Dummy-Klassen für den Demo-Modus, wenn PyVmomi nicht installiert ist
    class vim:
        class fault:
            HostConnectFault = Exception
            InvalidLogin = Exception
            NoPermission = Exception
            NotAuthenticated = Exception
            
    class fault:
        HostConnectFault = Exception
        InvalidLogin = Exception
        NoPermission = Exception
        NotAuthenticated = Exception


# Benutzerdefinierte Ausnahmen
class VSphereError(Exception):
    """Basisklasse für alle vSphere-bezogenen Ausnahmen"""
    pass


class ConnectionError(VSphereError):
    """Ausnahme für Verbindungsfehler"""
    pass


class AuthenticationError(VSphereError):
    """Ausnahme für Authentifizierungsfehler"""
    pass


class DataAccessError(VSphereError):
    """Ausnahme für Datenzugriffsfehler"""
    pass


def handle_vsphere_error(func):
    """
    Decorator für die Fehlerbehandlung von vSphere-Funktionen
    
    Args:
        func: Die zu dekorierenden Funktion
        
    Returns:
        Die dekorierte Funktion mit Fehlerbehandlung
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except vim.fault.HostConnectFault as e:
            logging.error(f"Verbindungsfehler zum Host: {str(e)}")
            raise ConnectionError(f"Verbindungsfehler zum Host: {str(e)}")
        except vim.fault.InvalidLogin as e:
            logging.error(f"Ungültige Anmeldedaten: {str(e)}")
            raise AuthenticationError(f"Ungültige Anmeldedaten: {str(e)}")
        except (vim.fault.NoPermission, vim.fault.NotAuthenticated) as e:
            logging.error(f"Unzureichende Berechtigungen: {str(e)}")
            raise AuthenticationError(f"Unzureichende Berechtigungen: {str(e)}")
        except ssl.SSLError as e:
            logging.error(f"SSL-Fehler: {str(e)}")
            raise ConnectionError(f"SSL-Fehler: {str(e)}")
        except socket.error as e:
            logging.error(f"Netzwerkfehler: {str(e)}")
            raise ConnectionError(f"Netzwerkfehler: {str(e)}")
        except Exception as e:
            logging.error(f"Unerwarteter Fehler: {str(e)}", exc_info=True)
            raise VSphereError(f"Unerwarteter Fehler: {str(e)}")
    
    return wrapper