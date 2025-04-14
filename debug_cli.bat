@echo off
REM VMware vSphere Reporter - Debug CLI for Snapshots and Orphaned VMDKs

echo VMware vSphere Reporter - Debug CLI
echo ===================================
echo Diese Datei startet ein Diagnose-Tool, das speziell fuer Probleme
echo mit Snapshots und verwaisten VMDK-Dateien entwickelt wurde.
echo.

IF "%1"=="" (
    echo VERWENDUNG: debug_cli.bat -s VCENTER_SERVER -u USERNAME [-p PASSWORD] [-k]
    echo.
    echo PARAMETER:
    echo   -s, --server    vCenter-Server (IP oder Hostname)
    echo   -u, --user      vCenter-Benutzername
    echo   -p, --password  vCenter-Passwort (optional, wird abgefragt wenn nicht angegeben)
    echo   -k, --insecure  SSL-Zertifikatspruefung ignorieren
    echo   -o, --output    Ausgabedatei (Standard: debug_report.txt)
    echo.
    echo BEISPIEL:
    echo   debug_cli.bat -s vcenter.example.com -u administrator@vsphere.local -k
    echo.
    goto end
)

echo Starte Debug-Tool...
echo.

REM DEBUG-Modus aktivieren
set VSPHERE_REPORTER_DEBUG=1

REM Tool starten und Parameter weitergeben
python debug_cli.py %*

echo.
echo Beendet.

:end
pause