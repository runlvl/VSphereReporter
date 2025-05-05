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

# Prüfe, ob app.py existiert
if [ ! -f "app.py" ]; then
    echo "FEHLER: app.py nicht gefunden."
    echo "Bitte stellen Sie sicher, dass Sie sich im richtigen Verzeichnis befinden."
    exit 1
fi

# Aktiviere virtuelle Umgebung
echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Prüfe Python-Installation in der virtuellen Umgebung
python --version
if [ $? -ne 0 ]; then
    echo "FEHLER: Python konnte in der virtuellen Umgebung nicht gefunden werden."
    echo "Bitte führen Sie ./setup.sh erneut aus."
    exit 1
fi

# Prüfe Flask-Installation
python -c "import flask; print('Flask Version:', flask.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "FEHLER: Flask ist nicht installiert."
    echo "Installiere Flask und andere Abhängigkeiten..."
    pip install flask>=2.0.0 pyVmomi>=7.0.3 humanize>=4.1.0 jinja2>=3.0.0 reportlab>=3.6.0 python-docx>=0.8.11
    if [ $? -ne 0 ]; then
        echo "FEHLER: Installation der Abhängigkeiten fehlgeschlagen."
        exit 1
    fi
fi

# Erstelle benötigte Verzeichnisse, falls nicht vorhanden
mkdir -p logs
mkdir -p reports
mkdir -p static/img
mkdir -p static/css
mkdir -p static/js
mkdir -p static/topology

# Exportiere Debug-Modus, wenn angegeben
if [ "$1" == "--debug" ] || [ "$1" == "-d" ]; then
    export VSPHERE_REPORTER_DEBUG=1
    export FLASK_DEBUG=1
    echo "Debug-Modus aktiviert."
else
    export VSPHERE_REPORTER_DEBUG=0
    export FLASK_DEBUG=0
fi

# Exportiere Host und Port für die Flask-Anwendung
export FLASK_APP=app.py
export FLASK_DEBUG=1
export VSPHERE_REPORTER_HOST=0.0.0.0
export VSPHERE_REPORTER_PORT=5009

# Aktiviere Demo-Modus für einfaches Testen
export VSPHERE_REPORTER_DEMO=1

# Starte die Anwendung mit verbesserter Fehlerbehandlung
echo "Starte VMware vSphere Reporter v29.0..."
echo ""
echo "Sobald die Anwendung gestartet ist, können Sie sie unter folgender URL aufrufen:"
echo "http://localhost:$VSPHERE_REPORTER_PORT"
echo ""
echo "Falls die Anwendung nicht startet, überprüfen Sie die Fehlermeldungen."
echo "Falls Port 5000 bereits belegt ist, können Sie eine andere Portnummer verwenden:"
echo "export VSPHERE_REPORTER_PORT=5001 (oder eine andere Portnummer)"
echo ""
echo "Drücken Sie Strg+C, um die Anwendung zu beenden."
echo ""

# Versuche zuerst mit Flask CLI zu starten
python -m flask run --host=0.0.0.0 --port=$VSPHERE_REPORTER_PORT
if [ $? -ne 0 ]; then
    echo ""
    echo "FEHLER: Die Anwendung konnte nicht mit Flask CLI gestartet werden."
    echo "Versuche einen alternativen Startmodus..."
    python app.py
    if [ $? -ne 0 ]; then
        echo ""
        echo "FEHLER: Die Anwendung konnte nicht gestartet werden."
        echo "Bitte prüfen Sie die Fehlermeldungen oben."
        echo "Starten Sie das Skript mit --debug für ausführlichere Fehlermeldungen."
        
        # Letzte Möglichkeit: Starte einen einfachen HTTP-Server
        echo ""
        echo "Starte einen einfachen HTTP-Server für statische Dateien..."
        echo "Dies ist nur ein Fallback und bietet nicht die volle Funktionalität."
        cd static
        python -m http.server $VSPHERE_REPORTER_PORT
    fi
fi