#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Copyright (c) 2025 Bechtle GmbH

Start-Skript für den webbasierten VMware vSphere Reporter.
Dieses Skript sucht nach einem verfügbaren Port und startet dann die Flask-Anwendung.
"""

import os
import sys
import socket
import logging
import subprocess
import webbrowser
from time import sleep

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Standardport
DEFAULT_PORT = 5000
# Maximale Anzahl von Ports, die überprüft werden sollen
MAX_PORT_CHECK = 20

def is_port_available(port):
    """
    Überprüft, ob ein bestimmter Port verfügbar ist.
    
    Args:
        port: Die zu überprüfende Portnummer
        
    Returns:
        True, wenn der Port verfügbar ist, andernfalls False
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except Exception as e:
        logger.warning(f"Fehler bei der Überprüfung des Ports {port}: {str(e)}")
        return False

def find_available_port(start_port=DEFAULT_PORT, max_attempts=MAX_PORT_CHECK):
    """
    Sucht nach einem verfügbaren Port, beginnend bei start_port.
    
    Args:
        start_port: Der Port, bei dem die Suche beginnen soll
        max_attempts: Die maximale Anzahl von Ports, die überprüft werden sollen
        
    Returns:
        Eine verfügbare Portnummer oder None, wenn kein Port gefunden wurde
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None

def start_app(port):
    """
    Startet die Flask-Anwendung auf dem angegebenen Port.
    
    Args:
        port: Die Portnummer, auf der die Anwendung gestartet werden soll
    """
    # Umgebungsvariablen für Flask setzen
    env = os.environ.copy()
    
    # Demo-Modus aktivieren, wenn die Umgebungsvariable gesetzt ist
    if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() == 'true':
        logger.info("Demo-Modus aktiviert - Es werden keine echten vCenter-Verbindungen hergestellt")
    
    logger.info(f"Starte vSphere Reporter auf Port {port}...")
    
    # Die Anwendung mit Python starten
    try:
        # Den Pfad zur app.py-Datei bestimmen
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        
        # Die Flask-Anwendung starten
        # Der Port wird über die Kommandozeile übergeben
        process = subprocess.Popen([
            sys.executable, 
            app_path,
            "--port",
            str(port)
        ], env=env)
        
        # Kurz warten, um sicherzustellen, dass die Anwendung gestartet wurde
        sleep(2)
        
        # Die URL im Standardbrowser öffnen
        webbrowser.open(f"http://127.0.0.1:{port}")
        
        # Auf den Prozess warten
        process.wait()
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}")
        sys.exit(1)

def main():
    """Hauptfunktion"""
    logger.info("VMware vSphere Reporter v29.0 - Web Edition wird gestartet")
    
    # Demo-Modus aktivieren, wenn die Umgebungsvariable nicht gesetzt ist
    if os.environ.get('VSPHERE_REPORTER_DEMO') is None:
        os.environ['VSPHERE_REPORTER_DEMO'] = 'True'
        logger.info("Demo-Modus aktiviert - Es werden keine echten vCenter-Verbindungen hergestellt")
    
    print("Starte vSphere Reporter...")
    
    # Verfügbaren Port suchen
    print("Suche nach verfügbarem Port...")
    port = find_available_port()
    
    if port is None:
        logger.error(f"Konnte keinen verfügbaren Port im Bereich {DEFAULT_PORT}-{DEFAULT_PORT+MAX_PORT_CHECK-1} finden.")
        print(f"Konnte keinen verfügbaren Port im Bereich {DEFAULT_PORT}-{DEFAULT_PORT+MAX_PORT_CHECK-1} finden.")
        print("Bitte stellen Sie sicher, dass mindestens ein Port in diesem Bereich verfügbar ist.")
        sys.exit(1)
    
    print(f"Verfügbarer Port gefunden: {port}")
    logger.info(f"Verwende Port {port} für den Web-Server")
    
    # Anwendung starten
    start_app(port)

if __name__ == "__main__":
    main()