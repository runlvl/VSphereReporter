@echo off
REM VMware vSphere Reporter v29.0
REM Start Script für Windows

echo Starte VMware vSphere Reporter...

REM Prüfe, ob Python installiert ist
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python wird benötigt, konnte aber nicht gefunden werden.
    echo Bitte installieren Sie Python 3.8 oder höher.
    echo Besuchen Sie https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Starte die Anwendung
python run.py %*

if %ERRORLEVEL% neq 0 (
    echo Es ist ein Fehler aufgetreten. Bitte überprüfen Sie die Fehlermeldung oben.
    pause
)

exit /b %ERRORLEVEL%