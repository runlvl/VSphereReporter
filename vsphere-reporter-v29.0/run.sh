#!/bin/bash
# VMware vSphere Reporter v29.0 - Startskript für Linux
# Copyright (c) 2025 Bechtle GmbH

echo "==================================================================="
echo "      VMware vSphere Reporter v29.0 - Web Edition (Linux)"
echo "==================================================================="
echo ""

# Prüfe, ob die virtuelle Umgebung existiert
if [ ! -d "venv" ]; then
    echo "FEHLER: Virtuelle Umgebung nicht gefunden."
    echo "Bitte führen Sie zuerst ./setup.sh aus."
    exit 1
fi

# Aktiviere virtuelle Umgebung
echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Exportiere Debug-Modus, wenn angegeben
if [ "$1" == "--debug" ] || [ "$1" == "-d" ]; then
    export VSPHERE_REPORTER_DEBUG=1
    echo "Debug-Modus aktiviert."
else
    export VSPHERE_REPORTER_DEBUG=0
fi

# Exportiere Host und Port für die Flask-Anwendung
export VSPHERE_REPORTER_HOST=0.0.0.0
export VSPHERE_REPORTER_PORT=5000

# Starte die Anwendung
echo "Starte VMware vSphere Reporter v29.0..."
echo "Sobald die Anwendung gestartet ist, können Sie sie unter folgender URL aufrufen:"
echo "http://localhost:5000"
echo ""
echo "Drücken Sie Strg+C, um die Anwendung zu beenden."
echo ""

python app.py