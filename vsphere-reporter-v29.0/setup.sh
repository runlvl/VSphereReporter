#!/bin/bash
# VMware vSphere Reporter v29.0 - Setup Script für Linux
# Copyright (c) 2025 Bechtle GmbH

echo "==================================================================="
echo "      VMware vSphere Reporter v29.0 - Installation (Linux)"
echo "==================================================================="
echo ""

# Prüfe Python-Version
echo "Prüfe Python-Installation..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "FEHLER: Python konnte nicht gefunden werden. Bitte installieren Sie Python 3.8 oder neuer."
    exit 1
fi

# Prüfe Python-Version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Gefundene Python-Version: $PYTHON_VERSION"

if [ "$PYTHON_VERSION_MAJOR" -lt 3 ] || ([ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -lt 8 ]); then
    echo "FEHLER: Python 3.8 oder neuer wird benötigt."
    exit 1
fi

# Prüfe pip
echo "Prüfe pip-Installation..."
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    echo "FEHLER: pip ist nicht installiert. Bitte installieren Sie pip für Python 3."
    exit 1
fi

# Erstelle virtuelle Umgebung, wenn nicht vorhanden
echo "Erstelle virtuelle Python-Umgebung..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
fi

# Aktiviere virtuelle Umgebung
echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Aktualisiere pip
echo "Aktualisiere pip..."
pip install --upgrade pip

# Installiere Abhängigkeiten
echo "Installiere Abhängigkeiten..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "FEHLER: Installation der Abhängigkeiten fehlgeschlagen."
    exit 1
fi

# Erstelle Verzeichnisse
echo "Erstelle Verzeichnisse..."
mkdir -p logs
mkdir -p reports
mkdir -p static/topology
mkdir -p static/img

# Kopiere das Bechtle-Logo, falls vorhanden
if [ -f "../attached_assets/logo_bechtle.png" ]; then
    echo "Kopiere Bechtle-Logo..."
    cp "../attached_assets/logo_bechtle.png" "static/img/"
fi

echo ""
echo "==================================================================="
echo "Installation abgeschlossen!"
echo ""
echo "Um die Anwendung zu starten, führen Sie aus: ./run.sh"
echo "==================================================================="