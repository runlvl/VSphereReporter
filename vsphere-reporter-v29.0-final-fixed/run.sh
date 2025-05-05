#!/bin/bash

echo "VMware vSphere Reporter v29.0 - Web Edition"
echo "Copyright (c) 2025 Bechtle GmbH"
echo

# Demo-Modus aktivieren
export VSPHERE_REPORTER_DEMO=True

# Prüfen, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Python 3 wurde nicht gefunden. Bitte stellen Sie sicher, dass Python (Version 3.8 oder höher) installiert ist."
    echo "und dass es im PATH verfügbar ist."
    echo
    echo "Sie können Python unter Linux über den Paketmanager installieren,"
    echo "z.B. mit 'sudo apt-get install python3' (Ubuntu/Debian) oder 'sudo zypper install python3' (SUSE)."
    exit 1
fi

# Prüfen, ob die erforderlichen Pakete installiert sind
echo "Überprüfe Abhängigkeiten..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "Das Paket 'flask' ist nicht installiert. Bitte führen Sie zuerst setup.sh aus."
    exit 1
fi

# Anwendung starten
echo "Starte vSphere Reporter..."
python3 run.py

if [ $? -ne 0 ]; then
    echo "Es ist ein Fehler aufgetreten. Bitte prüfen Sie die Ausgabe oben für weitere Informationen."
    exit 1
fi