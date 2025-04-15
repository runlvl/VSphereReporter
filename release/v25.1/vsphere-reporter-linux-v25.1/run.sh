#!/bin/bash

echo "VMware vSphere Reporter v25.1 wird gestartet..."
echo ""

# Prüfen, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Python 3 wurde nicht gefunden. Bitte installieren Sie Python 3.8 oder höher."
    echo ""
    echo "Unter Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "Unter OpenSuse: sudo zypper install python3 python3-pip"
    echo ""
    exit 1
fi

# Überprüfen Sie die Python-Version
python_version=$(python3 --version | grep -oP '(?<=Python )\d+\.\d+\.\d+')
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]); then
    echo "WARNUNG: Python-Version 3.8 oder höher ist erforderlich."
    echo "Installierte Version: $python_version"
    echo ""
    echo "Möchten Sie trotzdem fortfahren? (j/n)"
    read -r answer
    if [[ "$answer" != "j" && "$answer" != "J" ]]; then
        echo "Installation abgebrochen."
        exit 1
    fi
fi

# Prüfen, ob Abhängigkeiten installiert sind
echo "Überprüfe Abhängigkeiten..."
if ! python3 -c "import pyVmomi" &> /dev/null; then
    echo "pyVmomi ist nicht installiert. Installiere Abhängigkeiten..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Fehler beim Installieren der Abhängigkeiten."
        exit 1
    fi
else
    echo "Abhängigkeiten sind bereits installiert."
fi

echo ""
echo "Starte VMware vSphere Reporter..."
echo ""

# Debug-Modus prüfen
if [ "$1" = "-d" ] || [ "$1" = "--debug" ]; then
    echo "Debug-Modus aktiviert"
    export VSPHERE_REPORTER_DEBUG=1
    python3 vsphere_reporter.py
else
    python3 vsphere_reporter.py
fi