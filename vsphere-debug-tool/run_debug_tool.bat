@echo off
REM VMware vSphere Reporter Debug Tool
REM Dieses Skript startet das Diagnose-Tool für Snapshots und verwaiste VMDKs

setlocal
echo VMware vSphere Reporter - Debug Tool für Snapshots und verwaiste VMDKs
echo ====================================================================
echo.

REM Debug-Modus aktivieren
set VSPHERE_REPORTER_DEBUG=1

:input_server
set /p VCENTER_SERVER="vCenter-Server-Adresse eingeben: "
if "%VCENTER_SERVER%"=="" (
    echo Fehler: vCenter-Server-Adresse ist erforderlich
    goto input_server
)

:input_username
set /p VCENTER_USERNAME="vCenter-Benutzername eingeben: "
if "%VCENTER_USERNAME%"=="" (
    echo Fehler: vCenter-Benutzername ist erforderlich
    goto input_username
)

:input_diagnostic_type
echo.
echo Diagnosetyp auswählen:
echo [1] Snapshots
echo [2] Verwaiste VMDKs 
echo [3] Beides (Standard)
set /p DIAGNOSTIC_TYPE="Wählen Sie eine Option (1/2/3) [3]: "

if "%DIAGNOSTIC_TYPE%"=="1" (
    set DIAGNOSTIC_PARAM=--diagnostic-type snapshots
) else if "%DIAGNOSTIC_TYPE%"=="2" (
    set DIAGNOSTIC_PARAM=--diagnostic-type orphaned-vmdks
) else (
    set DIAGNOSTIC_PARAM=--diagnostic-type all
)

:input_ssl
echo.
set /p IGNORE_SSL="SSL-Zertifikatvalidierung ignorieren? (j/n) [n]: "
if /i "%IGNORE_SSL%"=="j" (
    set SSL_PARAM=--ignore-ssl
) else (
    set SSL_PARAM=
)

echo.
echo Starte Diagnose-Tool...
python vsphere_debug_collector.py --server %VCENTER_SERVER% --username %VCENTER_USERNAME% %DIAGNOSTIC_PARAM% %SSL_PARAM%

echo.
echo Diagnose abgeschlossen. Prüfen Sie die Log-Dateien für Details.
pause
endlocal