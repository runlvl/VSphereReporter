@echo off
REM VMware vSphere Reporter v29.0 - Setup-Skript für Windows
REM Copyright (c) 2025 Bechtle GmbH

echo ===================================================================
echo        VMware vSphere Reporter v29.0 - Setup (Windows)
echo ===================================================================
echo.

REM Prüfe Python-Installation
echo Prüfe Python-Installation...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Python konnte nicht gefunden werden.
    echo Bitte installieren Sie Python 3.8 oder höher von https://www.python.org/
    pause
    exit /b 1
)

REM Prüfe Python-Version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do (
    set PYTHON_VERSION=%%V
)
echo Gefundene Python-Version: %PYTHON_VERSION%

REM Extrahiere Hauptversionsnummer
for /f "tokens=1 delims=." %%A in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%A
)
for /f "tokens=2 delims=." %%B in ("%PYTHON_VERSION%") do (
    set PYTHON_MINOR=%%B
)

REM Überprüfe, ob die Python-Version mindestens 3.8 ist
if %PYTHON_MAJOR% LSS 3 (
    echo FEHLER: Python-Version %PYTHON_VERSION% ist zu alt.
    echo Bitte installieren Sie Python 3.8 oder höher.
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 8 (
        echo FEHLER: Python-Version %PYTHON_VERSION% ist zu alt.
        echo Bitte installieren Sie Python 3.8 oder höher.
        pause
        exit /b 1
    )
)

REM Prüfe pip-Installation
echo Prüfe pip-Installation...
python -m pip --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: pip ist nicht installiert.
    echo Bitte installieren Sie pip für Python.
    pause
    exit /b 1
)

REM Prüfe, ob venv-Modul verfügbar ist
echo Prüfe venv-Modul...
python -c "import venv" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FEHLER: Das venv-Modul ist nicht verfügbar.
    echo Bitte installieren Sie Python mit dem venv-Modul.
    pause
    exit /b 1
)

REM Erstelle virtuelle Umgebung
echo Erstelle virtuelle Umgebung...
if exist venv (
    echo Eine virtuelle Umgebung existiert bereits. Möchten Sie sie neu erstellen?
    echo Dies wird alle installierten Pakete zurücksetzen.
    choice /C YN /M "Virtuelle Umgebung neu erstellen?"
    if %ERRORLEVEL% EQU 1 (
        echo Lösche bestehende virtuelle Umgebung...
        rmdir /S /Q venv
        python -m venv venv
    )
) else (
    python -m venv venv
)

REM Aktiviere virtuelle Umgebung
echo Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

REM Aktualisiere pip, setuptools und wheel
echo Aktualisiere pip, setuptools und wheel...
python -m pip install --upgrade pip setuptools wheel

REM Erstelle benötigte Verzeichnisse
mkdir logs 2>nul
mkdir reports 2>nul
mkdir static 2>nul
mkdir static\img 2>nul
mkdir static\css 2>nul
mkdir static\js 2>nul
mkdir static\topology 2>nul
mkdir templates 2>nul
mkdir templates\components 2>nul
mkdir templates\reports 2>nul
mkdir webapp\\utils 2>nul

REM Installiere Abhängigkeiten aus requirements.txt, wenn vorhanden
if exist requirements.txt (
    echo Installiere Abhängigkeiten aus requirements.txt...
    pip install -r requirements.txt
) else (
    REM Installiere einzelne Abhängigkeiten
    echo Installiere Abhängigkeiten...
    pip install flask>=2.0.0
    pip install pyVmomi>=7.0.3
    pip install humanize>=4.1.0
    pip install jinja2>=3.0.0
    pip install reportlab>=3.6.0
    pip install python-docx>=0.8.11
)

REM Deaktiviere virtuelle Umgebung
echo Deaktiviere virtuelle Umgebung...
call venv\Scripts\deactivate.bat

echo.
echo ===================================================================
echo Die Installation wurde erfolgreich abgeschlossen.
echo.
echo Um den VMware vSphere Reporter zu starten, führen Sie run.bat aus.
echo ===================================================================
echo.

pause