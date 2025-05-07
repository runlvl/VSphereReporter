#!/usr/bin/env python3
"""
VMware vSphere Reporter v19.1 - Produktionsversion

Dieses Skript startet den Web-Server und öffnet ggf. einen Browser.
© 2025 Bechtle GmbH - Alle Rechte vorbehalten
"""

import os
import sys
import logging
import argparse
import socket
import webbrowser
import warnings
import io
from threading import Timer
from datetime import datetime

# Konfiguration
DEFAULT_PORT = 5000
VERSION = '19.1'
APP_NAME = 'VMware vSphere Reporter'
DEBUG_ENV_VAR = 'VSPHERE_REPORTER_DEBUG'

# Logging konfigurieren
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'vsphere_reporter_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Konfiguriere Logging global
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Standard-Logger
APP_LOGGER = logging.getLogger('vsphere_reporter_run')

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
    logging.info(f"Browser geöffnet mit URL: {url}")
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
        logging.info("Debug-Modus aktiviert")
    
    # Setze Port-Umgebungsvariable
    os.environ['VSPHERE_REPORTER_PORT'] = str(port)
    print(f"Verwende Port {port} für den Web-Server")
    
    try:
        # Importiere die App erst jetzt, um die Umgebungsvariablen zu berücksichtigen
        logging.info(f"Starte {APP_NAME} auf Port {port}...")
        
        # Öffne den Browser nach kurzer Verzögerung
        if not args.no_browser:
            Timer(1.5, lambda: open_browser(port)).start()
        
        # Radikale Unterdrückung aller Flask/Werkzeug-Warnungen und Entwicklungsserver-Meldungen
        
        # 1. Stelle Logging für Flask/Werkzeug ein, um alle unwichtigen Meldungen zu unterdrücken
        for logger_name in ['werkzeug', 'flask', 'flask.app']:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.ERROR)  # Nur Fehler anzeigen
            
        # 2. Unterdrücke Standardausgabe während des Imports von Flask
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()  # Leite Standardausgabe um
        
        # 3. Unterdrücke alle Warnungen
        warnings.filterwarnings('ignore')
        
        # 4. Setze Umgebungsvariablen, die Flask veranlassen, Startmeldungen zu unterdrücken
        os.environ['WERKZEUG_RUN_MAIN'] = 'true'
        
        # Setze WERKZEUG_SERVER_FD auf einen leeren Wert, um Fehler zu vermeiden
        if 'WERKZEUG_SERVER_FD' in os.environ:
            del os.environ['WERKZEUG_SERVER_FD']
        
        # 5. Stelle Standardausgabe wieder her
        sys.stdout = original_stdout
        
        # Verwende einen einfachen Ansatz: Starte app.py als Subprocess
        logging.info(f"Flask-App wird im Produktionsmodus auf Port {port} gestartet...")
        
        # Erstelle Umgebungsvariablen für den Unterprozess
        env = os.environ.copy()
        env['FLASK_APP'] = 'app.py'
        env['FLASK_ENV'] = 'production'
        env['FLASK_RUN_PORT'] = str(port)
        env['FLASK_RUN_HOST'] = '0.0.0.0'
        env['PYTHONWARNINGS'] = 'ignore'
        
        import subprocess
        
        try:
            # Führe app.py direkt aus
            python_executable = sys.executable
            subprocess.check_call([python_executable, 'app.py'], env=env)
        except subprocess.SubprocessError as e:
            logging.error(f"Fehler beim Ausführen von app.py: {str(e)}")
            print(f"Fehler: {str(e)}")
            sys.exit(1)
    except ImportError as e:
        logging.error(f"Fehler beim Importieren der Anwendung: {str(e)}")
        logging.error("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
        print(f"Fehler: {str(e)}")
        print("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fehler beim Starten der Anwendung: {str(e)}")
        print(f"Fehler: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()