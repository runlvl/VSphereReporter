@echo off
REM VMware vSphere Reporter v29.0 - Setup Script für Windows
REM Copyright (c) 2025 Bechtle GmbH

echo ===================================================================
echo       VMware vSphere Reporter v29.0 - Installation (Windows)
echo ===================================================================
echo.

REM Prüfe Python-Installation
echo Prüfe Python-Installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Python konnte nicht gefunden werden. Bitte installieren Sie Python 3.8 oder neuer.
    echo und stellen Sie sicher, dass es im PATH verfügbar ist.
    pause
    exit /b 1
)

REM Prüfe Python-Version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Gefundene Python-Version: %PYTHON_VERSION%

REM Erstelle virtuelle Umgebung, wenn nicht vorhanden
echo Erstelle virtuelle Python-Umgebung...
if not exist venv (
    python -m venv venv
)

REM Aktiviere virtuelle Umgebung
echo Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

REM Aktualisiere pip
echo Aktualisiere pip...
python -m pip install --upgrade pip

REM Installiere Abhängigkeiten
echo Installiere Abhängigkeiten...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Installation der Abhängigkeiten fehlgeschlagen.
    pause
    exit /b 1
)

REM Erstelle Verzeichnisse
echo Erstelle Verzeichnisse...
if not exist logs mkdir logs
if not exist reports mkdir reports
if not exist static\topology mkdir static\topology
if not exist static\img mkdir static\img

REM Kopiere das Bechtle-Logo, falls vorhanden
if exist ..\attached_assets\logo_bechtle.png (
    echo Kopiere Bechtle-Logo...
    copy ..\attached_assets\logo_bechtle.png static\img\
)

echo.
echo ===================================================================
echo Installation abgeschlossen!
echo.
echo Um die Anwendung zu starten, führen Sie aus: run.bat
echo ===================================================================

pause