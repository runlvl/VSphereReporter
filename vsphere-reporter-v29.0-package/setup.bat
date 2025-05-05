@echo off
REM VMware vSphere Reporter v29.0 - Windows Setup-Skript
REM Copyright (c) 2025 Bechtle GmbH

echo.
echo VMware vSphere Reporter v29.0 - Web Edition Setup
echo.

REM Prüfe, ob Python installiert ist
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python wurde nicht gefunden. Bitte installieren Sie Python 3.8 oder neuer.
    echo.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python gefunden. Prüfe Version...
for /f "tokens=2" %%I in ('python --version 2^>^&1') do (
    set PYTHON_VERSION=%%I
)
echo Python-Version: %PYTHON_VERSION%

REM Erstelle Ordnerstruktur
echo.
echo Erstelle Ordnerstruktur...
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports
if not exist "static" mkdir static
if not exist "static\topology" mkdir static\topology
if not exist "webapp\utils" mkdir webapp\utils

REM Installiere Abhängigkeiten
echo.
echo Installiere Abhängigkeiten...
python -m pip install --upgrade pip
python -m pip install flask jinja2 pyecharts werkzeug

echo.
echo Setup abgeschlossen. Sie können nun die Anwendung mit run.bat starten.
echo.
pause