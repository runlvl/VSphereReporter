@echo off
REM VMware vSphere Reporter v29.0 - Web Edition
REM Copyright (c) 2025 Bechtle GmbH
REM Startskript für Windows-Umgebungen

echo VMware vSphere Reporter v29.0 - Web Edition
echo Copyright (c) 2025 Bechtle GmbH
echo ----------------------------------------

REM Port für die Anwendung
set PORT=5009

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

REM Prüfe, ob Flask installiert ist
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNUNG: Flask ist nicht installiert
    echo.
    set /p INSTALL_DEPS="Möchten Sie die benötigten Abhängigkeiten jetzt installieren? (j/n): "
    if /i "%INSTALL_DEPS%"=="j" (
        echo.
        echo Installiere Abhängigkeiten...
        pip install flask werkzeug jinja2 humanize pyVmomi pyecharts python-docx reportlab
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Konnte Abhängigkeiten nicht installieren
            echo Bitte führen Sie setup.bat aus oder installieren Sie die Abhängigkeiten manuell
            pause
            exit /b 1
        )
    ) else (
        echo Bitte führen Sie setup.bat aus, um die Abhängigkeiten zu installieren
        pause
        exit /b 1
    )
)

REM Erstelle benötigte Verzeichnisse
mkdir logs reports static\topology 2>nul

REM Prüfe, ob Port bereits belegt ist
netstat -an | findstr :%PORT% >nul
if %ERRORLEVEL% EQU 0 (
    echo WARNUNG: Port %PORT% wird bereits verwendet
    echo.
    set /p CHANGE_PORT="Möchten Sie einen anderen Port verwenden? (j/n): "
    if /i "%CHANGE_PORT%"=="j" (
        echo.
        set /p PORT="Bitte geben Sie einen alternativen Port ein: "
        echo Port auf %PORT% geändert
    ) else (
        echo Die Anwendung kann nicht gestartet werden, da der Port bereits belegt ist
        pause
        exit /b 1
    )
)

REM Demo-Modus aktivieren?
echo.
echo Möchten Sie den Demo-Modus aktivieren? (j/n)
echo Im Demo-Modus wird keine tatsächliche Verbindung zu einem vCenter hergestellt
set /p DEMO_MODE=": "
if /i "%DEMO_MODE%"=="j" (
    set VSPHERE_REPORTER_DEMO=true
    echo Demo-Modus aktiviert
) else (
    set VSPHERE_REPORTER_DEMO=false
)

REM Debug-Modus aktivieren?
echo.
echo Möchten Sie den Debug-Modus aktivieren? (j/n)
set /p DEBUG_MODE=": "
if /i "%DEBUG_MODE%"=="j" (
    set VSPHERE_REPORTER_DEBUG=true
    echo Debug-Modus aktiviert
) else (
    set VSPHERE_REPORTER_DEBUG=false
)

echo.
echo Starte VMware vSphere Reporter v29.0 - Web Edition...
echo Die Anwendung ist erreichbar unter: http://localhost:%PORT%
echo.

REM Starte die Anwendung
python app.py

pause