@echo off
REM VMware vSphere Reporter v29.0 - Windows Startskript
REM Copyright (c) 2025 Bechtle GmbH

echo.
echo VMware vSphere Reporter v29.0 - Web Edition wird gestartet...
echo.

REM Setze Umgebungsvariablen für den Demo-Modus
set VSPHERE_REPORTER_DEMO=true

REM Starte die Anwendung
python run.py

REM Wenn ein Fehler auftritt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Es ist ein Fehler aufgetreten. Bitte prüfen Sie, ob alle Abhängigkeiten installiert sind.
    echo.
    pause
)

pause