#!/bin/bash
# Bechtle vSphere Reporter v0.1 - Startskript für Linux

echo "Starte Bechtle vSphere Reporter v0.1..."

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python 3 konnte nicht gefunden werden."
    echo "Bitte installieren Sie Python 3.8 oder höher."
    exit 1
fi

# Mache das Skript ausführbar, falls es das noch nicht ist
chmod +x start.py

# Starte die Anwendung über Python
python3 start.py "$@"

# Prüfe auf Fehler
if [ $? -ne 0 ]; then
    echo
    echo "Es ist ein Fehler beim Starten der Anwendung aufgetreten."
    echo "Bitte überprüfen Sie die Log-Dateien im Ordner 'logs'."
    exit 1
fi

exit 0