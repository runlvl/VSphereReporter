#!/bin/bash
# VMware vSphere Reporter - Linux Setup-Skript
# Dieses Skript installiert die erforderlichen Abhängigkeiten.

# Farbdefinitionen
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}VMware vSphere Reporter - Setup${NC}"
echo "Installiere Abhängigkeiten..."

# Überprüfen, ob pip verfügbar ist
if ! command -v pip >/dev/null 2>&1; then
    echo -e "${RED}Python pip nicht gefunden.${NC}"
    echo "Bitte installieren Sie pip mit Ihrem Paketmanager."
    echo "Beispiel für Ubuntu/Debian: sudo apt-get install python3-pip"
    echo "Beispiel für RHEL/CentOS: sudo yum install python3-pip"
    echo "Beispiel für OpenSUSE: sudo zypper install python3-pip"
    exit 1
fi

# Verzeichnisstruktur erstellen
mkdir -p logs

# Abhängigkeiten installieren
echo -e "${GREEN}Installiere Python-Abhängigkeiten...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Fehler beim Installieren der Abhängigkeiten.${NC}"
    exit 1
fi

# Prüfen, ob PyQt5 installiert wurde oder ob wir Tkinter verwenden müssen
if python -c "import PyQt5" 2>/dev/null; then
    echo -e "${GREEN}PyQt5 wurde erfolgreich installiert.${NC}"
    echo -e "${GREEN}Sie können die Anwendung mit 'python vsphere_reporter.py' starten.${NC}"
else
    echo -e "${ORANGE}PyQt5 konnte nicht installiert werden.${NC}"
    echo -e "${ORANGE}Die Anwendung wird im Tkinter-Modus (Linux-GUI) ausgeführt.${NC}"
    echo -e "${GREEN}Sie können die Anwendung mit 'python vsphere_reporter_linux.py' starten.${NC}"
fi

# Ausführbare Berechtigungen setzen
chmod +x vsphere_reporter.py
chmod +x vsphere_reporter_linux.py
chmod +x vsphere_reporter_cli.py

echo -e "${BLUE}Setup abgeschlossen.${NC}"
echo "Um im Debug-Modus zu starten, setzen Sie die Umgebungsvariable VSPHERE_REPORTER_DEBUG=1"
echo "Beispiel: VSPHERE_REPORTER_DEBUG=1 python vsphere_reporter_linux.py"
echo "Oder für die CLI-Version: VSPHERE_REPORTER_DEBUG=1 python vsphere_reporter_cli.py [parameter]"