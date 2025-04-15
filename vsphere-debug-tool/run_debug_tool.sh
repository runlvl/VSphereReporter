#!/bin/bash
# VMware vSphere Reporter Debug Tool
# Dieses Skript startet das Diagnose-Tool für Snapshots und verwaiste VMDKs

# Debug-Modus aktivieren
export VSPHERE_REPORTER_DEBUG=1

echo "VMware vSphere Reporter - Debug Tool für Snapshots und verwaiste VMDKs"
echo "===================================================================="
echo

# vCenter-Server-Adresse abfragen
while [ -z "$VCENTER_SERVER" ]; do
    read -p "vCenter-Server-Adresse eingeben: " VCENTER_SERVER
    if [ -z "$VCENTER_SERVER" ]; then
        echo "Fehler: vCenter-Server-Adresse ist erforderlich"
    fi
done

# vCenter-Benutzername abfragen
while [ -z "$VCENTER_USERNAME" ]; do
    read -p "vCenter-Benutzername eingeben: " VCENTER_USERNAME
    if [ -z "$VCENTER_USERNAME" ]; then
        echo "Fehler: vCenter-Benutzername ist erforderlich"
    fi
done

# Diagnosetyp abfragen
echo
echo "Diagnosetyp auswählen:"
echo "[1] Snapshots"
echo "[2] Verwaiste VMDKs" 
echo "[3] Beides (Standard)"
read -p "Wählen Sie eine Option (1/2/3) [3]: " DIAGNOSTIC_TYPE

if [ "$DIAGNOSTIC_TYPE" = "1" ]; then
    DIAGNOSTIC_PARAM="--diagnostic-type snapshots"
elif [ "$DIAGNOSTIC_TYPE" = "2" ]; then
    DIAGNOSTIC_PARAM="--diagnostic-type orphaned-vmdks"
else
    DIAGNOSTIC_PARAM="--diagnostic-type all"
fi

# SSL-Validierung abfragen
echo
read -p "SSL-Zertifikatvalidierung ignorieren? (j/n) [n]: " IGNORE_SSL
if [ "$IGNORE_SSL" = "j" ] || [ "$IGNORE_SSL" = "J" ]; then
    SSL_PARAM="--ignore-ssl"
else
    SSL_PARAM=""
fi

echo
echo "Starte Diagnose-Tool..."
python3 vsphere_debug_collector.py --server "$VCENTER_SERVER" --username "$VCENTER_USERNAME" $DIAGNOSTIC_PARAM $SSL_PARAM

echo
echo "Diagnose abgeschlossen. Prüfen Sie die Log-Dateien für Details."
read -p "Drücken Sie Enter, um fortzufahren..." KEY