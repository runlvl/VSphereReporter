@echo off
REM Bechtle vSphere Reporter v0.1 - Startskript für Windows

echo Starte Bechtle vSphere Reporter v0.1...

REM Prüfe, ob Python installiert ist
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Python konnte nicht gefunden werden.
    echo Bitte installieren Sie Python 3.8 oder höher.
    pause
    exit /b 1
)

REM Direkt mit Python starten ohne den start Befehl
python app.py

if %ERRORLEVEL% NEQ 0 (
    echo Direkter Start fehlgeschlagen. Versuche intelligenten Start...
    python start.py
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Es ist ein Fehler beim Starten der Anwendung aufgetreten.
        echo Bitte überprüfen Sie die Log-Dateien im Ordner 'logs'.
        pause
    )
)

exit /b 0