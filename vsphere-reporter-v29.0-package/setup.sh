#!/bin/bash
# VMware vSphere Reporter v29.0 - Linux Setup-Skript
# Copyright (c) 2025 Bechtle GmbH

echo
echo "VMware vSphere Reporter v29.0 - Web Edition Setup"
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

echo "Python gefunden. Prüfe Version..."
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "Python-Version: $PYTHON_VERSION"

# Erstelle Ordnerstruktur
echo
echo "Erstelle Ordnerstruktur..."
mkdir -p logs
mkdir -p reports
mkdir -p static
mkdir -p static/topology
mkdir -p webapp/utils

# Mache Skripte ausführbar
echo "Mache Skripte ausführbar..."
chmod +x run.py
chmod +x run.sh

# Installiere Abhängigkeiten
echo
echo "Installiere Abhängigkeiten..."
python3 -m pip install --upgrade pip
python3 -m pip install flask jinja2 pyecharts werkzeug

echo
echo "Setup abgeschlossen. Sie können nun die Anwendung mit run.sh starten."
echo
read -p "Drücken Sie eine Taste, um fortzufahren..." -n1 -s
echo