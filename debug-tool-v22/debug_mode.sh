#!/bin/bash
# VMware vSphere Reporter - Debug-Modus Starter für Linux

echo "VMware vSphere Reporter wird im DEBUG-Modus gestartet..."
echo "Fehlerbehandlung ist deaktiviert, alle Meldungen werden protokolliert"
echo ""

if [ ! -d "logs" ]; then
  mkdir logs
  echo "Logs-Verzeichnis erstellt"
fi

export VSPHERE_REPORTER_DEBUG=1
python3 vsphere_reporter_linux.py

read -p "Drücken Sie eine Taste, um fortzufahren..."
