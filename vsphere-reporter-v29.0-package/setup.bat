@echo off
echo VMware vSphere Reporter v29.0 - Setup
echo Copyright (c) 2025 Bechtle GmbH
echo.

echo Überprüfe Python-Installation...
python --version > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python wurde nicht gefunden. Bitte stellen Sie sicher, dass Python (Version 3.8 oder höher) installiert ist.
    echo und dass es im PATH verfügbar ist.
    echo.
    echo Sie können Python von https://www.python.org/downloads/ herunterladen.
    pause
    exit /b 1
)

echo Überprüfe Pip-Installation...
python -m pip --version > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Pip wurde nicht gefunden. Bitte stellen Sie sicher, dass Pip installiert ist.
    echo.
    echo Sie können Pip mit 'python -m ensurepip' installieren.
    pause
    exit /b 1
)

echo Installiere benötigte Pakete...
python -m pip install --upgrade pip
python -m pip install --no-cache-dir flask flask-wtf pyVmomi python-docx reportlab humanize jinja2

if %ERRORLEVEL% NEQ 0 (
    echo Fehler bei der Installation der benötigten Pakete. Bitte überprüfen Sie die Fehlermeldungen.
    pause
    exit /b 1
)

echo.
echo Installation abgeschlossen. Sie können jetzt die Anwendung mit 'run.bat' starten.
pause
exit /b 0