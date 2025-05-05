#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Starter-Skript

Dieses Skript startet die VMware vSphere Reporter Web-Anwendung
und findet automatisch einen verfügbaren Port, falls der
Standardport 5000 nicht verfügbar ist.

Copyright (c) 2025 Bechtle GmbH
"""

import os
import sys
import socket
import logging
import webbrowser
from time import sleep
from datetime import datetime

# Logging-Konfiguration
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format,
                   datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

# Konstanten
DEFAULT_PORT = 5000
MAX_PORT = 5100  # Wir suchen bis Port 5100
DEMO_ENV_VAR = "VSPHERE_REPORTER_DEMO"
DEBUG_ENV_VAR = "VSPHERE_REPORTER_DEBUG"

def is_port_available(port):
    """
    Prüft, ob ein bestimmter Port verfügbar ist.
    
    Args:
        port (int): Der zu prüfende Port
        
    Returns:
        bool: True, wenn der Port verfügbar ist, sonst False
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False

def find_available_port(start_port=DEFAULT_PORT, max_port=MAX_PORT):
    """
    Findet einen verfügbaren Port im angegebenen Bereich.
    
    Args:
        start_port (int): Der erste zu prüfende Port
        max_port (int): Der letzte zu prüfende Port
        
    Returns:
        int: Einen verfügbaren Port oder None, wenn keiner gefunden wurde
    """
    for port in range(start_port, max_port + 1):
        if is_port_available(port):
            return port
    return None

def open_browser(port):
    """
    Öffnet den Standard-Webbrowser mit der Anwendungs-URL.
    
    Args:
        port (int): Der Port, auf dem die Anwendung läuft
    """
    url = f"http://localhost:{port}"
    try:
        # Warte einen Moment, bis der Server gestartet ist
        sleep(2)
        webbrowser.open(url)
        logger.info(f"Browser geöffnet mit URL: {url}")
    except Exception as e:
        logger.warning(f"Konnte Browser nicht automatisch öffnen: {e}")
        logger.info(f"Sie können die Anwendung unter {url} aufrufen")

def setup_demo_mode():
    """
    Setzt Umgebungsvariablen für den Demo-Modus, falls gewünscht.
    
    Returns:
        bool: True, wenn der Demo-Modus aktiviert wurde
    """
    # Lesen der Eingabe vom Benutzer
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('--demo', '-d'):
        os.environ[DEMO_ENV_VAR] = 'True'
        logger.info("Demo-Modus aktiviert")
        return True
    
    # Oder aus der Umgebungsvariable
    demo_mode = os.environ.get(DEMO_ENV_VAR, 'False').lower() in ('true', '1', 't')
    if demo_mode:
        logger.info("Demo-Modus aktiviert (über Umgebungsvariable)")
    
    return demo_mode

def setup_debug_mode():
    """
    Setzt Umgebungsvariablen für den Debug-Modus, falls gewünscht.
    
    Returns:
        bool: True, wenn der Debug-Modus aktiviert wurde
    """
    # Lesen der Eingabe vom Benutzer
    if len(sys.argv) > 1 and sys.argv[1].lower() in ('--debug', '-v'):
        os.environ[DEBUG_ENV_VAR] = 'True'
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug-Modus aktiviert")
        return True
    
    # Oder aus der Umgebungsvariable
    debug_mode = os.environ.get(DEBUG_ENV_VAR, 'False').lower() in ('true', '1', 't')
    if debug_mode:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug-Modus aktiviert (über Umgebungsvariable)")
    
    return debug_mode

def main():
    """
    Hauptfunktion zum Starten der Anwendung
    
    Returns:
        int: Exit-Code (0 bei Erfolg, 1 bei Fehler)
    """
    print("Starte vSphere Reporter...")
    
    # Demo- und Debug-Modi einrichten
    demo_mode = setup_demo_mode()
    debug_mode = setup_debug_mode()
    
    # Verfügbaren Port finden
    print("Suche nach verfügbarem Port...")
    port = find_available_port()
    
    if not port:
        logger.error("Konnte keinen verfügbaren Port finden.")
        return 1
    
    print(f"Verfügbarer Port gefunden: {port}")
    logger.info(f"Verwende Port {port} für den Web-Server")
    
    # Import der Flask-App muss nach dem Setzen der Umgebungsvariablen erfolgen
    logger.info(f"Starte vSphere Reporter auf Port {port}...")
    
    try:
        from app import app
        
        # Browser öffnen (nicht im Debug-Modus)
        if not debug_mode:
            # In einem Thread starten, damit der Server nicht blockiert wird
            from threading import Thread
            browser_thread = Thread(target=open_browser, args=(port,))
            browser_thread.daemon = True
            browser_thread.start()
        
        # Starte Flask-App
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
        return 0
    
    except ImportError as e:
        logger.error(f"Fehler beim Importieren der Anwendung: {e}")
        logger.error("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
        return 1
    
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())