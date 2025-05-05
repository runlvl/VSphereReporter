#!/bin/bash

# VMware vSphere Reporter v29.0 - Web Edition
# Copyright (c) 2025 Bechtle GmbH
# Installationsskript für Linux-Umgebungen

# Farbige Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}VMware vSphere Reporter v29.0 - Web Edition${NC}"
echo -e "${BLUE}Installation und Setup${NC}"
echo -e "${BLUE}Copyright (c) 2025 Bechtle GmbH${NC}"
echo "----------------------------------------"

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
else
    echo -e "${GREEN}Python $PYTHON_VERSION gefunden${NC}"
fi

# Prüfe, ob pip installiert ist
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Fehler: pip ist nicht installiert${NC}"
    echo "Bitte installieren Sie pip für Python 3"
    exit 1
else
    echo -e "${GREEN}pip gefunden${NC}"
fi

# Erstelle virtuelle Umgebung (optional)
echo -e "${YELLOW}Möchten Sie eine virtuelle Python-Umgebung erstellen? (j/n)${NC}"
echo "Eine virtuelle Umgebung wird empfohlen, um Abhängigkeitskonflikte zu vermeiden"
read -r create_venv
if [[ $create_venv == "j" ]]; then
    echo "Prüfe, ob venv verfügbar ist..."
    if ! python3 -m venv --help &> /dev/null; then
        echo -e "${RED}Fehler: venv-Modul ist nicht verfügbar${NC}"
        echo "Bitte installieren Sie das Python venv-Modul"
        exit 1
    fi
    
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Fehler: Konnte virtuelle Umgebung nicht erstellen${NC}"
        exit 1
    fi
    
    echo "Aktiviere virtuelle Umgebung..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}Fehler: Konnte virtuelle Umgebung nicht aktivieren${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Virtuelle Umgebung erstellt und aktiviert${NC}"
    
    # Erstelle Aktivierungsskript
    cat > activate_venv.sh << EOL
#!/bin/bash
source venv/bin/activate
echo "Virtuelle Umgebung aktiviert. Verwenden Sie 'deactivate', um sie zu verlassen."
EOL
    chmod +x activate_venv.sh
    echo "Ein Aktivierungsskript wurde erstellt: ./activate_venv.sh"
else
    echo "Keine virtuelle Umgebung wird verwendet."
fi

# Installiere Abhängigkeiten
echo "Installiere benötigte Python-Pakete..."
pip3 install flask werkzeug jinja2 humanize pyVmomi pyecharts python-docx reportlab

if [ $? -ne 0 ]; then
    echo -e "${RED}Fehler: Konnte Abhängigkeiten nicht installieren${NC}"
    exit 1
fi

echo -e "${GREEN}Abhängigkeiten erfolgreich installiert${NC}"

# Erstelle benötigte Verzeichnisse
mkdir -p logs reports static/topology

# Erstelle Demo-Berichte-Verzeichnis
mkdir -p static/reports/demo

# Abschluss
echo -e "${GREEN}Installation abgeschlossen!${NC}"
echo "Die Anwendung kann nun mit ./run.sh gestartet werden."

# Mache run.sh ausführbar
chmod +x run.sh

echo "----------------------------------------"
echo -e "${YELLOW}Weitere Schritte:${NC}"
echo "1. Starte die Anwendung mit ./run.sh"
echo "2. Öffne einen Webbrowser und navigiere zu http://localhost:5009"
echo "3. Verbinde dich mit deinem vCenter oder verwende den Demo-Modus"

exit 0