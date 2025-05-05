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

REM Prüfe, ob app.py existiert
if not exist app.py (
    echo FEHLER: app.py nicht gefunden.
    echo Bitte stellen Sie sicher, dass Sie sich im richtigen Verzeichnis befinden.
    pause
    exit /b 1
)

REM Aktiviere virtuelle Umgebung
echo Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

REM Prüfe Python-Installation in der virtuellen Umgebung
python --version
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Python konnte in der virtuellen Umgebung nicht gefunden werden.
    echo Bitte führen Sie setup.bat erneut aus.
    pause
    exit /b 1
)

REM Prüfe Flask-Installation
python -c "import flask; print('Flask Version:', flask.__version__)"
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Flask ist nicht installiert.
    echo Installiere Flask und andere Abhängigkeiten...
    pip install flask>=2.0.0 pyVmomi>=7.0.3 humanize>=4.1.0 jinja2>=3.0.0 reportlab>=3.6.0 python-docx>=0.8.11
    if %ERRORLEVEL% NEQ 0 (
        echo FEHLER: Installation der Abhängigkeiten fehlgeschlagen.
        pause
        exit /b 1
    )
)

REM Erstelle benötigte Verzeichnisse, falls nicht vorhanden
if not exist logs mkdir logs
if not exist reports mkdir reports
if not exist static mkdir static
if not exist static\img mkdir static\img
if not exist static\css mkdir static\css
if not exist static\js mkdir static\js
if not exist static\topology mkdir static\topology

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
set FLASK_APP=app.py
set FLASK_DEBUG=1
set VSPHERE_REPORTER_HOST=0.0.0.0
set VSPHERE_REPORTER_PORT=5009

REM Aktiviere Demo-Modus für einfaches Testen
set VSPHERE_REPORTER_DEMO=1

REM Starte die Anwendung mit verbesserter Fehlerbehandlung
echo Starte VMware vSphere Reporter v29.0...
echo.
echo Sobald die Anwendung gestartet ist, können Sie sie unter folgender URL aufrufen:
echo http://localhost:%VSPHERE_REPORTER_PORT%
echo.
echo Falls die Anwendung nicht startet, überprüfen Sie die Fehlermeldungen.
echo Falls Port 5000 bereits belegt ist, können Sie eine andere Portnummer verwenden:
echo set VSPHERE_REPORTER_PORT=5001 (oder eine andere Portnummer)
echo.
echo Drücken Sie Strg+C, um die Anwendung zu beenden.
echo.

python -m flask run --host=0.0.0.0 --port=%VSPHERE_REPORTER_PORT%
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FEHLER: Die Anwendung konnte nicht gestartet werden.
    echo Versuche einen alternativen Startmodus...
    python app.py
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo FEHLER: Die Anwendung konnte nicht gestartet werden.
        echo Bitte prüfen Sie die Fehlermeldungen oben.
        echo Starten Sie das Skript mit --debug für ausführlichere Fehlermeldungen.
    )
)

pause