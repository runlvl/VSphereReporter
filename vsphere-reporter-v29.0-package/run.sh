#!/bin/bash

# VMware vSphere Reporter v29.0 - Web Edition
# Copyright (c) 2025 Bechtle GmbH
# Startskript für Linux-Umgebungen

# Farbige Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}VMware vSphere Reporter v29.0 - Web Edition${NC}"
echo -e "${BLUE}Copyright (c) 2025 Bechtle GmbH${NC}"
echo "----------------------------------------"

# Port für die Anwendung
PORT=5009

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Fehler: Python 3 ist nicht installiert${NC}"
    echo "Bitte installieren Sie Python 3.8 oder höher"
    exit 1
fi

# Prüfe Python-Version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo -e "${RED}Fehler: Python-Version zu alt${NC}"
    echo "Benötigt: Python 3.8 oder höher"
    echo "Gefunden: Python $PYTHON_VERSION"
    exit 1
fi

# Prüfe, ob Flask installiert ist
if ! python3 -c "import flask" &> /dev/null; then
    echo -e "${YELLOW}Warnung: Flask ist nicht installiert${NC}"
    echo "Möchten Sie die benötigten Abhängigkeiten jetzt installieren? (j/n)"
    read -r install_deps
    if [[ $install_deps == "j" ]]; then
        echo "Installiere Abhängigkeiten..."
        pip3 install flask werkzeug jinja2 humanize pyVmomi pyecharts python-docx reportlab
        if [ $? -ne 0 ]; then
            echo -e "${RED}Fehler: Konnte Abhängigkeiten nicht installieren${NC}"
            echo "Bitte führen Sie setup.sh aus oder installieren Sie die Abhängigkeiten manuell"
            exit 1
        fi
    else
        echo "Bitte führen Sie setup.sh aus, um die Abhängigkeiten zu installieren"
        exit 1
    fi
fi

# Erstelle benötigte Verzeichnisse
mkdir -p logs reports static/topology

# Prüfe, ob Port bereits belegt ist
if command -v lsof &> /dev/null; then
    PORT_IN_USE=$(lsof -i:$PORT -t)
    if [ -n "$PORT_IN_USE" ]; then
        echo -e "${YELLOW}Warnung: Port $PORT wird bereits verwendet${NC}"
        echo "Möchten Sie einen anderen Port verwenden? (j/n)"
        read -r change_port
        if [[ $change_port == "j" ]]; then
            echo "Bitte geben Sie einen alternativen Port ein:"
            read -r PORT
            echo "Port auf $PORT geändert"
        else
            echo -e "${RED}Die Anwendung kann nicht gestartet werden, da der Port bereits belegt ist${NC}"
            exit 1
        fi
    fi
fi

# Demo-Modus aktivieren?
echo "Möchten Sie den Demo-Modus aktivieren? (j/n)"
echo "Im Demo-Modus wird keine tatsächliche Verbindung zu einem vCenter hergestellt"
read -r demo_mode
if [[ $demo_mode == "j" ]]; then
    export VSPHERE_REPORTER_DEMO=true
    echo -e "${YELLOW}Demo-Modus aktiviert${NC}"
else
    export VSPHERE_REPORTER_DEMO=false
fi

# Debug-Modus aktivieren?
echo "Möchten Sie den Debug-Modus aktivieren? (j/n)"
read -r debug_mode
if [[ $debug_mode == "j" ]]; then
    export VSPHERE_REPORTER_DEBUG=true
    echo -e "${YELLOW}Debug-Modus aktiviert${NC}"
else
    export VSPHERE_REPORTER_DEBUG=false
fi

echo -e "${GREEN}Starte VMware vSphere Reporter v29.0 - Web Edition...${NC}"
echo "Die Anwendung ist erreichbar unter: http://localhost:$PORT"

# Starte die Anwendung
python3 app.py