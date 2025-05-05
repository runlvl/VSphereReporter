@echo off
echo VMware vSphere Reporter v29.0 - Starten
echo Copyright (c) 2025 Bechtle GmbH
echo.

if not exist venv (
    echo Virtuelle Umgebung nicht gefunden. Bitte fuehren Sie zuerst setup.bat aus.
    pause
    exit /b 1
)

echo Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

echo Starte vSphere Reporter...
python run.py %*

if %ERRORLEVEL% NEQ 0 (
    echo Fehler beim Starten der Anwendung.
    pause
    exit /b 1
)

pause