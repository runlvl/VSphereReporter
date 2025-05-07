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

REM Starte die Anwendung über Python
python start.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Es ist ein Fehler beim Starten der Anwendung aufgetreten.
    echo Bitte überprüfen Sie die Log-Dateien im Ordner 'logs'.
    pause
)

exit /b 0