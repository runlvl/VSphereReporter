@echo off
REM VMware vSphere Reporter - Windows Startskript
REM Diese Datei startet die Anwendung

REM Prüfen, ob der Debug-Modus durch einen Parameter angefordert wird
IF "%1"=="-debug" (
    echo Starte VMware vSphere Reporter im DEBUG-Modus...
    SET VSPHERE_REPORTER_DEBUG=1
) ELSE (
    echo Starte VMware vSphere Reporter...
)

REM Anwendung starten
python vsphere_reporter.py

REM Beenden mit einer Pause, falls Fehler aufgetreten sind
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Es sind Fehler aufgetreten. Bitte wenden Sie sich an den Support.
    echo Fehlercode: %ERRORLEVEL%
    pause
)