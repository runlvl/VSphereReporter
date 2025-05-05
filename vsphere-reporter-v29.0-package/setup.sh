#!/bin/bash
# VMware vSphere Reporter v29.0 - Setup-Skript für Linux
# Copyright (c) 2025 Bechtle GmbH

echo "==================================================================="
echo "       VMware vSphere Reporter v29.0 - Setup (Linux)"
echo "==================================================================="
echo ""

# Prüfe Python-Installation
echo "Prüfe Python-Installation..."
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python 3 konnte nicht gefunden werden."
    echo "Bitte installieren Sie Python 3.8 oder höher."
    exit 1
fi

# Prüfe Python-Version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Gefundene Python-Version: $PYTHON_VERSION"

# Extrahiere Hauptversionsnummer
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# Überprüfe, ob die Python-Version mindestens 3.8 ist
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "FEHLER: Python-Version $PYTHON_VERSION ist zu alt."
    echo "Bitte installieren Sie Python 3.8 oder höher."
    exit 1
fi

# Prüfe pip-Installation
echo "Prüfe pip-Installation..."
if ! command -v pip3 &> /dev/null; then
    echo "FEHLER: pip3 ist nicht installiert."
    echo "Bitte installieren Sie pip für Python 3."
    exit 1
fi

# Prüfe, ob venv-Modul verfügbar ist
echo "Prüfe venv-Modul..."
if ! python3 -c "import venv" &> /dev/null; then
    echo "FEHLER: Das venv-Modul ist nicht verfügbar."
    echo "Bitte installieren Sie das Python venv-Modul."
    echo "Auf Ubuntu/Debian: sudo apt-get install python3-venv"
    echo "Auf openSUSE: sudo zypper install python3-venv"
    echo "Auf Fedora/RHEL: sudo dnf install python3-venv"
    exit 1
fi

# Erstelle virtuelle Umgebung
echo "Erstelle virtuelle Umgebung..."
if [ -d "venv" ]; then
    echo "Eine virtuelle Umgebung existiert bereits. Möchten Sie sie neu erstellen?"
    echo "Dies wird alle installierten Pakete zurücksetzen."
    read -p "Virtuelle Umgebung neu erstellen? (j/n): " RECREATE
    if [[ $RECREATE =~ ^[Jj]$ ]]; then
        echo "Lösche bestehende virtuelle Umgebung..."
        rm -rf venv
        python3 -m venv venv
    fi
else
    python3 -m venv venv
fi

# Aktiviere virtuelle Umgebung
echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Aktualisiere pip, setuptools und wheel
echo "Aktualisiere pip, setuptools und wheel..."
pip install --upgrade pip setuptools wheel

# Erstelle benötigte Verzeichnisse
mkdir -p logs
mkdir -p reports
mkdir -p static/img
mkdir -p static/css
mkdir -p static/js
mkdir -p static/topology
mkdir -p templates/components
mkdir -p templates/reports
mkdir -p webapp/utils

# Installiere Abhängigkeiten aus requirements.txt, wenn vorhanden
if [ -f "requirements.txt" ]; then
    echo "Installiere Abhängigkeiten aus requirements.txt..."
    pip install -r requirements.txt
else
    # Installiere einzelne Abhängigkeiten
    echo "Installiere Abhängigkeiten..."
    pip install flask>=2.0.0
    pip install pyVmomi>=7.0.3
    pip install humanize>=4.1.0
    pip install jinja2>=3.0.0
    pip install reportlab>=3.6.0
    pip install python-docx>=0.8.11
fi

# Deaktiviere virtuelle Umgebung
echo "Deaktiviere virtuelle Umgebung..."
deactivate

# Mache die Skripte ausführbar
chmod +x run.sh

echo ""
echo "==================================================================="
echo "Die Installation wurde erfolgreich abgeschlossen."
echo ""
echo "Um den VMware vSphere Reporter zu starten, führen Sie ./run.sh aus."
echo "==================================================================="
echo ""