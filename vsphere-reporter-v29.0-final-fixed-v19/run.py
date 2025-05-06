#!/usr/bin/env python3
"""
VMware vSphere Reporter v19 - Starter-Skript

Dieses Skript startet den Web-Server und öffnet ggf. einen Browser.
"""

import os
import sys
import logging
import argparse
import socket
import webbrowser
from threading import Timer
from datetime import datetime

# Konfiguration
DEFAULT_PORT = 5000
VERSION = '19.0'
APP_NAME = 'VMware vSphere Reporter'
DEBUG_ENV_VAR = 'VSPHERE_REPORTER_DEBUG'

# Logging konfigurieren
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'vsphere_reporter_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logger = logging.getLogger('vsphere_reporter_run')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def is_port_in_use(port):
    """Prüft, ob ein Port bereits verwendet wird"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=DEFAULT_PORT, max_attempts=10):
    """Findet einen verfügbaren Port"""
    print("Suche nach verfügbarem Port...")
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            print(f"Verfügbarer Port gefunden: {port}")
            return port
    
    # Wenn kein Port gefunden wurde, nimm den Standard
    return start_port

def open_browser(port):
    """Öffnet den Browser mit der App-URL"""
    url = f"http://localhost:{port}"
    logger.info(f"Browser geöffnet mit URL: {url}")
    webbrowser.open(url)

def main():
    """Haupteinstiegspunkt"""
    parser = argparse.ArgumentParser(description=f'{APP_NAME} v{VERSION} - Web Server Starter')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port für den Web-Server (Standard: {DEFAULT_PORT})')
    parser.add_argument('--no-browser', action='store_true', help='Verhindert das automatische Öffnen des Browsers')
    parser.add_argument('--debug', action='store_true', help='Aktiviert den Debug-Modus')
    
    args = parser.parse_args()
    
    print(f"Starte {APP_NAME}...")
    
    # Prüfe, ob der angegebene Port verfügbar ist
    port = args.port
    if is_port_in_use(port):
        port = find_available_port(port)
    
    # Setze Debug-Umgebungsvariable
    if args.debug:
        os.environ[DEBUG_ENV_VAR] = 'True'
        logger.info("Debug-Modus aktiviert")
    
    # Setze Port-Umgebungsvariable
    os.environ['VSPHERE_REPORTER_PORT'] = str(port)
    logger.info(f"Verwende Port {port} für den Web-Server")
    
    try:
        # Importiere die App erst jetzt, um die Umgebungsvariablen zu berücksichtigen
        logger.info(f"Starte {APP_NAME} auf Port {port}...")
        
        # Öffne den Browser nach kurzer Verzögerung
        if not args.no_browser:
            Timer(1.5, lambda: open_browser(port)).start()
        
        # Starte die Flask-App
        from app import app
        app.run(host='0.0.0.0', port=port, debug=args.debug)
    except ImportError as e:
        logger.error(f"Fehler beim Importieren der Anwendung: {str(e)}")
        logger.error("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
        print(f"Fehler: {str(e)}")
        print("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}")
        print(f"Fehler: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()