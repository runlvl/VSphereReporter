#!/bin/bash

echo "VMware vSphere Reporter v29.0 - Setup"
echo "Copyright (c) 2025 Bechtle GmbH"
echo

# Prüfen, ob Python 3 installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Python 3 wurde nicht gefunden. Bitte stellen Sie sicher, dass Python (Version 3.8 oder höher) installiert ist."
    echo "und dass es im PATH verfügbar ist."
    echo
    echo "Sie können Python unter Linux über den Paketmanager installieren,"
    echo "z.B. mit 'sudo apt-get install python3' (Ubuntu/Debian) oder 'sudo zypper install python3' (SUSE)."
    exit 1
fi

# Prüfen, ob Pip installiert ist
echo "Überprüfe Pip-Installation..."
if ! python3 -m pip --version &> /dev/null; then
    echo "Pip wurde nicht gefunden. Bitte stellen Sie sicher, dass Pip installiert ist."
    echo
    echo "Sie können Pip mit 'sudo apt-get install python3-pip' (Ubuntu/Debian)"
    echo "oder 'sudo zypper install python3-pip' (SUSE) installieren."
    exit 1
fi

# Installiere benötigte Pakete
echo "Installiere benötigte Pakete..."
python3 -m pip install --upgrade pip
python3 -m pip install --no-cache-dir flask flask-wtf pyVmomi python-docx reportlab humanize jinja2

if [ $? -ne 0 ]; then
    echo "Fehler bei der Installation der benötigten Pakete. Bitte überprüfen Sie die Fehlermeldungen."
    exit 1
fi

# Setze Ausführungsrechte für die Start-Skripte
chmod +x run.sh

echo
echo "Installation abgeschlossen. Sie können jetzt die Anwendung mit './run.sh' starten."
echo