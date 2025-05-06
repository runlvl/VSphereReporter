#!/bin/bash
# VMware vSphere Reporter v29.0
# Start Script für Linux

echo "Starte VMware vSphere Reporter..."

# Prüfe, ob Python installiert ist
if ! command -v python3 &> /dev/null
then
    echo "Python 3 wird benötigt, konnte aber nicht gefunden werden."
    echo "Bitte installieren Sie Python 3.8 oder höher."
    echo "Beispiel: sudo apt install python3 python3-pip (Ubuntu/Debian)"
    echo "       oder: sudo zypper install python3 python3-pip (OpenSUSE)"
    exit 1
fi

# Mache das Skript ausführbar
chmod +x run.py

# Starte die Anwendung
python3 run.py "$@"

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "Es ist ein Fehler aufgetreten. Bitte überprüfen Sie die Fehlermeldung oben."
    read -p "Drücken Sie eine Taste zum Beenden..." -n1 -s
fi

exit $exit_code