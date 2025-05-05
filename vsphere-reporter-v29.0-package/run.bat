@echo off
echo VMware vSphere Reporter v29.0 - Web Edition
echo Copyright (c) 2025 Bechtle GmbH
echo.

REM Demo-Modus aktivieren
SET VSPHERE_REPORTER_DEMO=True

REM Pfad zur Python-Installation überprüfen
python --version > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python wurde nicht gefunden. Bitte stellen Sie sicher, dass Python (Version 3.8 oder höher) installiert ist.
    echo und dass es im PATH verfügbar ist.
    echo.
    echo Sie können Python von https://www.python.org/downloads/ herunterladen.
    pause
    exit /b 1
)

REM Prüfen, ob die erforderlichen Pakete installiert sind
echo Überprüfe Abhängigkeiten...
python -c "import flask" > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Das Paket 'flask' ist nicht installiert. Bitte führen Sie zuerst setup.bat aus.
    pause
    exit /b 1
)

REM Anwendung starten
echo Starte vSphere Reporter...
python run.py

if %ERRORLEVEL% NEQ 0 (
    echo Es ist ein Fehler aufgetreten. Bitte prüfen Sie die Ausgabe oben für weitere Informationen.
    pause
    exit /b 1
)

pause
exit /b 0