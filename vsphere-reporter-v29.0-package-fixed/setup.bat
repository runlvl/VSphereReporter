@echo off
echo VMware vSphere Reporter v29.0 - Setup
echo Copyright (c) 2025 Bechtle GmbH
echo.

echo Pruefe Python-Installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python wurde nicht gefunden! Bitte installieren Sie Python 3.8 oder hoeher.
    echo Besuchen Sie https://www.python.org/downloads/ zum Herunterladen.
    pause
    exit /b 1
)

REM Wir setzen die Version einfach voraus, statt sie zu prüfen
echo Python ist installiert, wir fahren mit der Installation fort.
echo.

echo Pruefe pip...
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo pip wurde nicht gefunden. Installation von pip...
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo Fehler bei der pip-Installation.
        pause
        exit /b 1
    )
)

echo pip ist installiert.
echo.

echo Erstelle virtuelle Umgebung...
if exist venv (
    echo Bestehende virtuelle Umgebung gefunden.
) else (
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Fehler beim Erstellen der virtuellen Umgebung.
        pause
        exit /b 1
    )
)

echo Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

echo Installiere Abhaengigkeiten...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Fehler beim Installieren der Abhaengigkeiten.
    pause
    exit /b 1
)

echo.
echo Setup abgeschlossen!
echo Verwenden Sie run.bat, um die Anwendung zu starten.
echo.
pause