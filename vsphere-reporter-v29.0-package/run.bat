@echo off
REM VMware vSphere Reporter v29.0 - Startskript für Windows
REM Copyright (c) 2025 Bechtle GmbH

echo ===================================================================
echo       VMware vSphere Reporter v29.0 - Web Edition (Windows)
echo ===================================================================
echo.

REM Prüfe, ob die virtuelle Umgebung existiert
if not exist venv (
    echo FEHLER: Virtuelle Umgebung nicht gefunden.
    echo Bitte führen Sie zuerst setup.bat aus.
    pause
    exit /b 1
)

REM Aktiviere virtuelle Umgebung
echo Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

REM Exportiere Debug-Modus, wenn angegeben
if "%1"=="--debug" (
    set VSPHERE_REPORTER_DEBUG=1
    echo Debug-Modus aktiviert.
) else if "%1"=="-d" (
    set VSPHERE_REPORTER_DEBUG=1
    echo Debug-Modus aktiviert.
) else (
    set VSPHERE_REPORTER_DEBUG=0
)

REM Exportiere Host und Port für die Flask-Anwendung
set VSPHERE_REPORTER_HOST=0.0.0.0
set VSPHERE_REPORTER_PORT=5000

REM Starte die Anwendung
echo Starte VMware vSphere Reporter v29.0...
echo Sobald die Anwendung gestartet ist, können Sie sie unter folgender URL aufrufen:
echo http://localhost:5000
echo.
echo Drücken Sie Strg+C, um die Anwendung zu beenden.
echo.

python app.py