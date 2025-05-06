#!/bin/bash
# VMware vSphere Reporter v29.0
# Setup Script für Linux

echo "VMware vSphere Reporter Setup..."

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null
then
    echo "Python 3 wird benötigt, konnte aber nicht gefunden werden."
    echo "Bitte installieren Sie Python 3.8 oder höher."
    echo "Beispiel: sudo apt install python3 python3-pip (Ubuntu/Debian)"
    echo "       oder: sudo zypper install python3 python3-pip (OpenSUSE)"
    exit 1
fi

# Prüfe die Python-Version
python3_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python3_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Python 3.8 oder höher wird benötigt."
    echo "Ihre installierte Version ist $python3_version"
    echo "Bitte aktualisieren Sie Python auf 3.8 oder höher."
    exit 1
fi

# Prüfe, ob pip verfügbar ist
if ! command -v pip3 &> /dev/null
then
    echo "pip3 wird benötigt, konnte aber nicht gefunden werden."
    echo "Versuche pip3 zu installieren..."
    
    if [ -f /etc/debian_version ]; then
        echo "Debian/Ubuntu-basiertes System erkannt."
        echo "Führen Sie 'sudo apt install python3-pip' aus, um pip zu installieren."
    elif [ -f /etc/redhat-release ]; then
        echo "Red Hat-basiertes System erkannt."
        echo "Führen Sie 'sudo dnf install python3-pip' aus, um pip zu installieren."
    elif [ -f /etc/SuSE-release ] || [ -f /etc/openSUSE-release ]; then
        echo "SUSE-basiertes System erkannt."
        echo "Führen Sie 'sudo zypper install python3-pip' aus, um pip zu installieren."
    else
        echo "Unbekanntes Betriebssystem."
        echo "Bitte installieren Sie pip3 manuell für Ihr System."
    fi
    
    exit 1
fi

# Mache Skripte ausführbar
chmod +x run.py
chmod +x run.sh

echo "Installiere Abhängigkeiten..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Fehler bei der Installation der Abhängigkeiten."
    exit 1
fi

echo ""
echo "Setup abgeschlossen!"
echo "Starten Sie die Anwendung mit ./run.sh"
echo ""