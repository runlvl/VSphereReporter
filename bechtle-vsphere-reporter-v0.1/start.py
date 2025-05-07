#!/usr/bin/env python3
"""
Bechtle vSphere Reporter - Intelligentes Startskript

Dieses Skript startet den vSphere Reporter mit automatischer Port-Auswahl
und Fehlerbehandlung.
"""

import os
import sys
import time
import socket
import argparse
import subprocess
import logging
import webbrowser
from datetime import datetime

# Konfiguration
DEFAULT_PORT = 5000
MAX_PORT = 5100
PORT_CHECK_TIMEOUT = 0.5

# Logging konfigurieren
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(log_dir, f'startup_{timestamp}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('vsphere_reporter_starter')

def is_port_available(port):
    """
    Prüft, ob ein Port verfügbar ist
    
    Args:
        port: Zu prüfender Port
        
    Returns:
        bool: True, wenn der Port verfügbar ist
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(PORT_CHECK_TIMEOUT)
        result = s.connect_ex(('localhost', port))
        return result != 0

def find_available_port(start_port=DEFAULT_PORT, max_port=MAX_PORT):
    """
    Findet einen verfügbaren Port im angegebenen Bereich
    
    Args:
        start_port: Port, ab dem gesucht werden soll
        max_port: Maximaler zu prüfender Port
        
    Returns:
        int: Verfügbaren Port oder None, wenn kein Port verfügbar ist
    """
    for port in range(start_port, max_port + 1):
        if is_port_available(port):
            return port
    return None

def ensure_python_path():
    """
    Stellt sicher, dass der Python-Interpreter verfügbar ist.
    
    Returns:
        str: Pfad zum Python-Interpreter
    """
    # Prüfe den aktuellen Python-Interpreter
    if sys.executable and os.path.exists(sys.executable):
        return sys.executable
    
    # Suche nach Python im Systempfad
    python_commands = ['python3', 'python', 'py']
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   shell=(os.name == 'nt'))
            if result.returncode == 0:
                return cmd
        except Exception:
            continue
    
    logger.error("Kein Python-Interpreter gefunden!")
    print("FEHLER: Es wurde kein Python-Interpreter gefunden. Bitte installieren Sie Python 3.8 oder höher.")
    sys.exit(1)

def wait_for_server(port, max_wait=30):
    """
    Wartet, bis der Server auf dem angegebenen Port erreichbar ist
    
    Args:
        port: Port, auf dem der Server laufen sollte
        max_wait: Maximale Wartezeit in Sekunden
        
    Returns:
        bool: True, wenn der Server erreichbar ist
    """
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if not is_port_available(port):
            return True
        time.sleep(0.5)
    return False

def start_application(port=None, debug=False):
    """
    Startet die Anwendung mit dem angegebenen Port
    
    Args:
        port: Port, auf dem die Anwendung laufen soll (oder None für automatische Auswahl)
        debug: Debug-Modus aktivieren
        
    Returns:
        bool: True bei Erfolg
    """
    # Finde einen verfügbaren Port, wenn keiner angegeben wurde
    if port is None:
        port = find_available_port()
        if port is None:
            logger.error(f"Konnte keinen freien Port im Bereich {DEFAULT_PORT}-{MAX_PORT} finden!")
            print(f"FEHLER: Konnte keinen freien Port im Bereich {DEFAULT_PORT}-{MAX_PORT} finden!")
            return False
    elif not is_port_available(port):
        logger.warning(f"Port {port} ist bereits belegt. Suche nach einem freien Port...")
        port = find_available_port()
        if port is None:
            logger.error(f"Konnte keinen freien Port im Bereich {DEFAULT_PORT}-{MAX_PORT} finden!")
            print(f"FEHLER: Konnte keinen freien Port im Bereich {DEFAULT_PORT}-{MAX_PORT} finden!")
            return False
    
    # Bestimme den Python-Interpreter
    python_path = ensure_python_path()
    
    # Bestimme den Pfad zur app.py
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    
    if not os.path.exists(app_path):
        logger.error(f"app.py nicht gefunden unter {app_path}")
        print(f"FEHLER: Die Hauptanwendungsdatei (app.py) wurde nicht gefunden unter {app_path}!")
        return False
    
    # Umgebungsvariablen für die Anwendung
    env = os.environ.copy()
    env['VSPHERE_REPORTER_PORT'] = str(port)
    
    if debug:
        env['VSPHERE_REPORTER_DEBUG'] = '1'
    
    # Befehl für den Start der Anwendung
    cmd = [python_path, app_path, '--port', str(port)]
    
    if debug:
        cmd.append('--debug')
    
    # Öffne ein neues Terminal-Fenster auf verschiedenen Plattformen
    if os.name == 'nt':  # Windows
        cmd_str = ' '.join(cmd)
        # Starte die Anwendung in einem neuen Terminal-Fenster
        full_cmd = f'start cmd /k "{cmd_str}"'
        subprocess.Popen(full_cmd, shell=True, env=env)
    else:  # Linux/Mac
        try:
            # Versuche mit "x-terminal-emulator" (Debian/Ubuntu)
            full_cmd = ['x-terminal-emulator', '-e', f"{' '.join(cmd)}"]
            subprocess.Popen(full_cmd, env=env)
        except Exception:
            try:
                # Versuche mit "gnome-terminal" (GNOME)
                full_cmd = ['gnome-terminal', '--', python_path, app_path, '--port', str(port)]
                if debug:
                    full_cmd.append('--debug')
                subprocess.Popen(full_cmd, env=env)
            except Exception:
                try:
                    # Versuche mit "konsole" (KDE)
                    full_cmd = ['konsole', '-e', f"{' '.join(cmd)}"]
                    subprocess.Popen(full_cmd, env=env)
                except Exception:
                    # Fallback: Starte im Hintergrund ohne neues Terminal
                    logger.warning("Konnte kein Terminal-Fenster öffnen, starte im Hintergrund")
                    subprocess.Popen(cmd, env=env)
    
    # Warte, bis der Server läuft
    if wait_for_server(port):
        logger.info(f"Server erfolgreich gestartet auf Port {port}")
        print(f"Bechtle vSphere Reporter wurde gestartet auf http://localhost:{port}")
        
        # Öffne den Browser
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception as e:
            logger.warning(f"Konnte Browser nicht öffnen: {str(e)}")
            print(f"Bitte öffnen Sie manuell die URL: http://localhost:{port}")
        
        return True
    else:
        logger.error(f"Server konnte nicht gestartet werden auf Port {port}")
        print("FEHLER: Der Server konnte nicht gestartet werden!")
        return False

def main():
    """Haupteinstiegspunkt für das Starter-Skript"""
    parser = argparse.ArgumentParser(description='Bechtle vSphere Reporter - Starter')
    parser.add_argument('--port', type=int, help='Port zum Starten des Webservers (optional, Standard: automatische Auswahl)')
    parser.add_argument('--debug', action='store_true', help='Debug-Modus aktivieren')
    
    args = parser.parse_args()
    
    print("Starte Bechtle vSphere Reporter v0.1...")
    start_application(args.port, args.debug)

if __name__ == '__main__':
    main()