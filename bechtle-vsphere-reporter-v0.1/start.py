"""
Bechtle vSphere Reporter v0.1 - Starter Script
Einfacher Starter, der einen verfügbaren Port findet
"""

import os
import socket
import webbrowser
import subprocess
import time
import sys

def find_available_port(start_port=5000, max_attempts=100):
    """Suche nach einem freien Port"""
    current_port = start_port
    for _ in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', current_port))
            sock.close()
            return current_port
        except OSError:
            current_port += 1
    raise RuntimeError(f"Konnte keinen freien Port nach {max_attempts} Versuchen finden.")

def main():
    """Hauptfunktion"""
    print("Starte Bechtle vSphere Reporter v0.1...")
    
    # Finde einen freien Port
    try:
        port = find_available_port()
        print(f"Verwende Port {port} für den Web-Server")
        
        # Setze Umgebungsvariablen
        env = os.environ.copy()
        env["VSPHERE_REPORTER_PORT"] = str(port)
        env["PYTHONWARNINGS"] = "ignore"
        
        # Starte die App
        print(f"Starte Anwendung auf Port {port}...")
        
        # Öffne den Browser nach einer kurzen Verzögerung
        def open_browser():
            time.sleep(2)
            url = f"http://localhost:{port}"
            print(f"Öffne Browser mit URL: {url}")
            webbrowser.open(url)
        
        import threading
        threading.Thread(target=open_browser).start()
        
        # Starte die App im Vordergrund
        subprocess.run([sys.executable, "app.py"], env=env)
        
    except Exception as e:
        print(f"Fehler beim Starten der Anwendung: {str(e)}")
        input("Drücke Enter zum Beenden...")

if __name__ == "__main__":
    main()