#!/bin/bash
# VMware vSphere Reporter v29.0 - Linux Startskript
# Copyright (c) 2025 Bechtle GmbH

echo
echo "VMware vSphere Reporter v29.0 - Web Edition wird gestartet..."
echo

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "Python 3 wurde nicht gefunden. Bitte installieren Sie Python 3.8 oder neuer."
    echo
    echo "Installation unter OpenSuse Tumbleweed: sudo zypper install python3"
    echo "Alternativ: https://www.python.org/downloads/"
    echo
    read -p "Drücken Sie eine Taste, um fortzufahren..." -n1 -s
    echo
    exit 1
fi

# Setze Umgebungsvariablen für den Demo-Modus
export VSPHERE_REPORTER_DEMO=true

# Mache das Skript ausführbar, falls es nicht bereits ist
chmod +x run.py

# Starte die Anwendung
python3 run.py

# Wenn ein Fehler auftritt
if [ $? -ne 0 ]; then
    echo
    echo "Es ist ein Fehler aufgetreten. Bitte prüfen Sie, ob alle Abhängigkeiten installiert sind."
    echo
    read -p "Drücken Sie eine Taste, um fortzufahren..." -n1 -s
    echo
fi

read -p "Drücken Sie eine Taste, um fortzufahren..." -n1 -s
echo