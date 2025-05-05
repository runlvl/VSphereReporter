@echo off
REM VMware vSphere Reporter v29.0 - Web Edition
REM Copyright (c) 2025 Bechtle GmbH
REM Installationsskript für Windows-Umgebungen

echo VMware vSphere Reporter v29.0 - Web Edition
echo Installation und Setup
echo Copyright (c) 2025 Bechtle GmbH
echo ----------------------------------------

REM Prüfe, ob Python installiert ist
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python ist nicht installiert oder nicht im PATH verfügbar
    echo Bitte installieren Sie Python 3.8 oder höher
    pause
    exit /b 1
)

REM Prüfe Python-Version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
echo Gefundene Python-Version: %PYTHON_VERSION%

REM Prüfe, ob pip installiert ist
python -m pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: pip ist nicht installiert
    echo Bitte installieren Sie pip für Python
    pause
    exit /b 1
)

REM Erstelle virtuelle Umgebung (optional)
echo.
echo Möchten Sie eine virtuelle Python-Umgebung erstellen? (j/n)
echo Eine virtuelle Umgebung wird empfohlen, um Abhängigkeitskonflikte zu vermeiden
set /p CREATE_VENV=": "

if /i "%CREATE_VENV%"=="j" (
    echo.
    echo Prüfe, ob venv verfügbar ist...
    python -m venv --help >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: venv-Modul ist nicht verfügbar
        echo Bitte installieren Sie das Python venv-Modul
        pause
        exit /b 1
    )
    
    echo Erstelle virtuelle Umgebung...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Konnte virtuelle Umgebung nicht erstellen
        pause
        exit /b 1
    )
    
    echo Aktiviere virtuelle Umgebung...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Konnte virtuelle Umgebung nicht aktivieren
        pause
        exit /b 1
    )
    
    echo Virtuelle Umgebung erstellt und aktiviert
    
    REM Erstelle Aktivierungsskript
    echo @echo off > activate_venv.bat
    echo call venv\Scripts\activate.bat >> activate_venv.bat
    echo echo Virtuelle Umgebung aktiviert. Verwenden Sie 'deactivate', um sie zu verlassen. >> activate_venv.bat
    
    echo Ein Aktivierungsskript wurde erstellt: activate_venv.bat
) else (
    echo Keine virtuelle Umgebung wird verwendet.
)

REM Installiere Abhängigkeiten
echo.
echo Installiere benötigte Python-Pakete...
python -m pip install flask werkzeug jinja2 humanize pyVmomi pyecharts python-docx reportlab
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Konnte Abhängigkeiten nicht installieren
    pause
    exit /b 1
)

echo Abhängigkeiten erfolgreich installiert

REM Erstelle benötigte Verzeichnisse
mkdir logs reports static\topology 2>nul
mkdir static\reports\demo 2>nul

REM Abschluss
echo.
echo Installation abgeschlossen!
echo Die Anwendung kann nun mit run.bat gestartet werden.

echo ----------------------------------------
echo Weitere Schritte:
echo 1. Starte die Anwendung mit run.bat
echo 2. Öffne einen Webbrowser und navigiere zu http://localhost:5009
echo 3. Verbinde dich mit deinem vCenter oder verwende den Demo-Modus

pause