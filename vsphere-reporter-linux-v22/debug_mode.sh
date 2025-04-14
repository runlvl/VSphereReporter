#!/bin/bash
# VMware vSphere Reporter - Debug-Modus-Starter
# Dieses Skript startet die Anwendung im Debug-Modus

export VSPHERE_REPORTER_DEBUG=1
echo "VMware vSphere Reporter wird im DEBUG-Modus gestartet..."
echo "Fehlerbehandlung ist deaktiviert, alle Meldungen werden protokolliert"
echo ""

if [ -f "vsphere_reporter_linux.py" ]; then
  python vsphere_reporter_linux.py
else
  python vsphere_reporter.py
fi
