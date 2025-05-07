#!/bin/bash
# VMware vSphere Reporter v19 Setup-Skript für Linux

echo "VMware vSphere Reporter v19.0 - Setup-Skript"
echo "============================================="
echo ""

# Verzeichnis des Skripts ermitteln
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Prüfen, ob Python installiert ist
command -v python3 >/dev/null 2>&1 || { 
    echo "Python 3 ist nicht installiert. Bitte installieren Sie Python 3.8 oder höher."
    exit 1
}

# Python-Version prüfen
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Python 3.8 oder höher wird benötigt. Ihre Version: $PYTHON_VERSION"
    exit 1
fi

echo "Python-Version $PYTHON_VERSION gefunden. OK!"

# Überprüfen, ob pip installiert ist
command -v pip3 >/dev/null 2>&1 || {
    echo "pip3 ist nicht installiert. Wird installiert..."
    python3 -m ensurepip || {
        echo "Fehler: pip konnte nicht installiert werden."
        exit 1
    }
}

echo "pip ist installiert. OK!"

# Prüfen, ob virtuelle Umgebung erstellt werden soll
USE_VENV=false
if command -v python3 -m venv >/dev/null 2>&1; then
    read -p "Möchten Sie eine virtuelle Python-Umgebung verwenden? (empfohlen) [J/n]: " USE_VENV_RESPONSE
    if [[ "$USE_VENV_RESPONSE" =~ ^[Nn]$ ]]; then
        USE_VENV=false
    else
        USE_VENV=true
    fi
fi

# Virtuelle Umgebung erstellen, wenn gewünscht
if [ "$USE_VENV" = true ]; then
    echo "Erstelle virtuelle Python-Umgebung..."
    python3 -m venv venv || {
        echo "Fehler: Virtuelle Umgebung konnte nicht erstellt werden."
        exit 1
    }
    
    # Virtuelle Umgebung aktivieren
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "Virtuelle Umgebung aktiviert."
    else
        echo "Fehler: Die Aktivierungsdatei der virtuellen Umgebung wurde nicht gefunden."
        exit 1
    fi
fi

echo "Installiere Abhängigkeiten..."

# Abhängigkeiten installieren
pip3 install --upgrade pip
pip3 install pyVmomi>=7.0.0 Flask>=2.0.0 Flask-WTF>=1.0.0 reportlab>=3.6.0 python-docx>=0.8.11 Jinja2>=3.0.0 humanize>=3.0.0 || {
    echo "Fehler: Abhängigkeiten konnten nicht installiert werden."
    exit 1
}

echo "Abhängigkeiten erfolgreich installiert."

# Erstelle die run.sh-Datei
cat > run.sh << 'EOF'
#!/bin/bash
# VMware vSphere Reporter v19 Starter-Skript für Linux

# Verzeichnis des Skripts ermitteln
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Prüfen, ob virtuelle Umgebung existiert und aktivieren
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtuelle Umgebung aktiviert."
fi

# Starte die Anwendung
python3 run.py "$@"
EOF

# Mache run.sh ausführbar
chmod +x run.sh

echo ""
echo "Setup abgeschlossen!"
echo "Um die Anwendung zu starten, führen Sie './run.sh' aus."
echo ""

# Frage, ob die Anwendung direkt gestartet werden soll
read -p "Möchten Sie die Anwendung jetzt starten? [J/n]: " START_APP_RESPONSE
if [[ ! "$START_APP_RESPONSE" =~ ^[Nn]$ ]]; then
    echo "Starte VMware vSphere Reporter..."
    ./run.sh
fi