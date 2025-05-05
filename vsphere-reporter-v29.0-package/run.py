#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Startskript
Copyright (c) 2025 Bechtle GmbH

Dieses Skript startet die vSphere Reporter Webanwendung.
Es prüft auf verfügbare Ports und initialisiert die Anwendung.
"""

import os
import sys
import socket
import logging
import webbrowser
import subprocess
from threading import Timer
import importlib.util

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DEFAULT_PORT = 5000
MAX_PORT_CHECK = 6500

def is_port_in_use(port):
    """Prüft, ob ein Port bereits verwendet wird."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=DEFAULT_PORT):
    """Sucht nach einem verfügbaren Port, beginnend mit start_port."""
    port = start_port
    while is_port_in_use(port) and port < MAX_PORT_CHECK:
        port += 1
    
    if port >= MAX_PORT_CHECK:
        logging.error(f"Kein verfügbarer Port im Bereich {start_port}-{MAX_PORT_CHECK} gefunden.")
        sys.exit(1)
    
    return port

def open_browser(port):
    """Öffnet den Browser mit der URL der Anwendung."""
    url = f"http://localhost:{port}"
    print(f"Öffne Browser mit URL: {url}")
    
    # Verzögerung, um sicherzustellen, dass der Server gestartet ist
    Timer(1.5, lambda: webbrowser.open(url)).start()

def check_dependencies():
    """Überprüft, ob alle erforderlichen Abhängigkeiten installiert sind."""
    required_modules = ['flask', 'jinja2']
    missing_modules = []
    
    for module in required_modules:
        if importlib.util.find_spec(module) is None:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Fehlende Abhängigkeiten: {', '.join(missing_modules)}")
        print("Bitte führen Sie setup.bat (Windows) oder setup.sh (Linux) aus, um die Abhängigkeiten zu installieren.")
        sys.exit(1)

def check_folders():
    """Überprüft, ob alle erforderlichen Verzeichnisse existieren, und erstellt sie bei Bedarf."""
    required_folders = ['logs', 'reports', 'static', 'static/topology']
    
    for folder in required_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logging.info(f"Verzeichnis erstellt: {folder}")

def main():
    """Hauptfunktion zum Starten der Anwendung."""
    try:
        # Abhängigkeiten und Verzeichnisse prüfen
        check_dependencies()
        check_folders()
        
        # Demo-Modus aktivieren
        os.environ['VSPHERE_REPORTER_DEMO'] = 'true'
        
        # Verfügbaren Port finden
        print("Suche nach verfügbarem Port...")
        port = find_available_port()
        print(f"Verfügbarer Port gefunden: {port}")
        
        # Webserver starten
        print(f"Starte vSphere Reporter auf Port {port}...")
        
        # Import app.py
        import app
        
        # Browser öffnen
        open_browser(port)
        
        # App starten
        app.app.run(host='0.0.0.0', port=port)
        
    except KeyboardInterrupt:
        print("\nvSphere Reporter wurde beendet.")
    except Exception as e:
        logging.error(f"Fehler beim Starten des vSphere Reporters: {str(e)}", exc_info=True)
        print(f"\nFehler: {str(e)}")
        print("Prüfen Sie die Log-Dateien für weitere Informationen.")
        input("\nDrücken Sie eine Taste, um fortzufahren...")

if __name__ == "__main__":
    print()
    print("Starte vSphere Reporter...")
    print()
    main()
    print("Drücken Sie Strg+C, um den vSphere Reporter zu beenden.")