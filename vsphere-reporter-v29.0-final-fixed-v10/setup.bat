@echo off
REM VMware vSphere Reporter v29.0
REM Setup Script für Windows

echo VMware vSphere Reporter Setup...

REM Prüfe, ob Python installiert ist
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python wird benötigt, konnte aber nicht gefunden werden.
    echo Bitte installieren Sie Python 3.8 oder höher.
    echo Besuchen Sie https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Prüfe die Python-Version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"
if %ERRORLEVEL% neq 0 (
    echo Python 3.8 oder höher wird benötigt.
    echo Ihre installierte Version ist zu alt.
    echo Bitte aktualisieren Sie Python auf 3.8 oder höher.
    pause
    exit /b 1
)

REM Prüfe, ob pip verfügbar ist
python -m pip --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo pip wird benötigt, konnte aber nicht gefunden werden.
    echo Installiere pip...
    
    REM Versuche, pip zu installieren
    python -m ensurepip --default-pip
    if %ERRORLEVEL% neq 0 (
        echo Fehler bei der pip-Installation.
        pause
        exit /b 1
    )
)

echo Installiere Abhängigkeiten...
python -m pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo Fehler bei der Installation der Abhängigkeiten.
    pause
    exit /b 1
)

echo.
echo Setup abgeschlossen!
echo Starten Sie die Anwendung mit run.bat
echo.

pause