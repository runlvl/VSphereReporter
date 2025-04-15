@echo off
REM VMware vSphere Reporter - Debug-Modus Starter

echo VMware vSphere Reporter wird im DEBUG-Modus gestartet...
echo Fehlerbehandlung ist deaktiviert, alle Meldungen werden protokolliert
echo.

if not exist logs (
  mkdir logs
  echo Logs-Verzeichnis erstellt
)

set VSPHERE_REPORTER_DEBUG=1
python vsphere_reporter.py

pause