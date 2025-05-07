@echo off
setlocal enabledelayedexpansion

echo VMware vSphere Reporter - MSI-Installer-Erstellung
echo ================================================
echo.

REM Prüfe, ob Python installiert ist
echo Prüfe Python-Installation...
where python > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python nicht gefunden. Möchten Sie Python jetzt herunterladen und installieren?
    echo Diese Installation ist nur für die Erstellung des Installers erforderlich.
    echo Das finale MSI-Paket wird Python automatisch enthalten.
    echo.
    set /p INSTALL_PYTHON="Python installieren? (j/n): "
    if /i "!INSTALL_PYTHON!"=="j" (
        echo Öffne Python-Download-Seite...
        start https://www.python.org/downloads/
        echo Bitte installieren Sie Python und führen Sie dieses Skript erneut aus.
        pause
        exit /b 1
    ) else (
        echo Installation abgebrochen.
        pause
        exit /b 1
    )
)

REM Prüfe, ob WiX Toolset installiert ist
echo Prüfe WiX Toolset-Installation...
where candle > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WiX Toolset nicht gefunden. Möchten Sie WiX Toolset herunterladen?
    echo Dies ist erforderlich, um MSI-Installationspakete zu erstellen.
    echo.
    set /p INSTALL_WIX="WiX Toolset installieren? (j/n): "
    if /i "!INSTALL_WIX!"=="j" (
        echo Öffne WiX Toolset-Download-Seite...
        start https://wixtoolset.org/releases/
        echo Bitte installieren Sie WiX Toolset und führen Sie dieses Skript erneut aus.
        pause
        exit /b 1
    ) else (
        echo Das MSI-Paket kann ohne WiX Toolset nicht erstellt werden.
        echo Erstelle stattdessen eine portable EXE-Version...
        set NO_MSI=1
    )
)

REM Installiere erforderliche Python-Pakete
echo Installiere erforderliche Python-Pakete...
python -m pip install cx_Freeze setuptools wheel pywin32

REM Erstelle Verzeichnisstruktur
echo Erstelle Verzeichnisstruktur...
if not exist dist mkdir dist

REM Starte die Erstellung
echo Starte Erstellung des Installationspakets...
if defined NO_MSI (
    echo Erstelle portable EXE-Version ohne MSI...
    python windows_package_builder.py --portable
) else (
    echo Erstelle vollständiges MSI-Installationspaket...
    python windows_package_builder.py
)

echo.
if %ERRORLEVEL% equ 0 (
    echo Erstellung des Installationspakets erfolgreich abgeschlossen!
    echo Das Paket befindet sich im Verzeichnis 'dist'.
) else (
    echo Bei der Erstellung des Installationspakets ist ein Fehler aufgetreten.
    echo Bitte überprüfen Sie die Fehlermeldungen.
)

pause