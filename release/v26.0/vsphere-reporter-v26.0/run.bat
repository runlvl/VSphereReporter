@echo off
REM VMware vSphere Reporter - Starter
REM -------------------------------------
REM Diese Batch-Datei startet den VMware vSphere Reporter
REM und unterstützt den -debug Parameter für erweiterte Fehlersuche

REM Prüfe Parameter
set debug_mode=0
for %%a in (%*) do (
    if /I "%%a"=="-debug" set debug_mode=1
)

REM Wenn debug_mode aktiviert ist, setze Umgebungsvariable
if %debug_mode%==1 (
    echo Starte VMware vSphere Reporter im DEBUG-Modus...
    echo Fehlerbehandlung ist deaktiviert, alle Meldungen werden protokolliert
    set VSPHERE_REPORTER_DEBUG=1
) else (
    echo Starte VMware vSphere Reporter...
)

REM Stelle sicher, dass Log-Verzeichnis existiert
if not exist logs (
    mkdir logs
)

REM Starte Python-Anwendung
python vsphere_reporter.py %*

REM Bei Fehler pausieren, um Fehlermeldung anzuzeigen
if %ERRORLEVEL% neq 0 (
    echo.
    echo Es ist ein Fehler aufgetreten. Fehlercode: %ERRORLEVEL%
    echo Bitte prüfen Sie die Log-Dateien im logs-Verzeichnis.
    echo.
    pause
)