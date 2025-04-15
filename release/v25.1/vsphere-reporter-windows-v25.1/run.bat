@echo off
echo VMware vSphere Reporter v25.1 wird gestartet...
echo.

:: Prüfen, ob Python installiert ist
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python wurde nicht gefunden. Bitte installieren Sie Python 3.8 oder höher.
    echo.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Überprüfen Sie die Python-Version
python --version | findstr /r "3\.[8-9]\..*\|3\.1[0-9]\..*" >nul
if %ERRORLEVEL% neq 0 (
    echo WARNUNG: Möglicherweise ist Python-Version 3.8 oder höher erforderlich.
    echo Installierte Version:
    python --version
    echo.
    echo Fortfahren? (Drücken Sie STRG+C zum Abbrechen oder eine beliebige Taste zum Fortfahren)
    pause >nul
)

:: Prüfen, ob Abhängigkeiten installiert sind
echo Überprüfe Abhängigkeiten...
python -c "import pyVmomi" 2>nul
if %ERRORLEVEL% neq 0 (
    echo pyVmomi ist nicht installiert. Installiere Abhängigkeiten...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Fehler beim Installieren der Abhängigkeiten.
        pause
        exit /b 1
    )
) else (
    echo Abhängigkeiten sind bereits installiert.
)

echo.
echo Starte VMware vSphere Reporter...
echo.

:: Debug-Modus prüfen
if "%1"=="-d" (
    echo Debug-Modus aktiviert
    set VSPHERE_REPORTER_DEBUG=1
    python vsphere_reporter.py
) else if "%1"=="--debug" (
    echo Debug-Modus aktiviert
    set VSPHERE_REPORTER_DEBUG=1
    python vsphere_reporter.py
) else (
    python vsphere_reporter.py
)

pause