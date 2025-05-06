@echo off
:: VMware vSphere Reporter v19 - Optimiertes Setup-Skript für Windows
setlocal enabledelayedexpansion

echo VMware vSphere Reporter v19.0 - Setup wird ausgeführt...

:: Prüfen, ob Python installiert ist
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Python 3.8 oder höher und führen Sie dieses Skript erneut aus.
    pause
    exit /b 1
)

:: Überprüfen, ob pip installiert ist
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installiere pip...
    python -m ensurepip --default-pip --quiet
    if %errorlevel% neq 0 (
        echo [FEHLER] Pip konnte nicht installiert werden.
        pause
        exit /b 1
    )
)

:: Virtuelle Umgebung automatisch erstellen (ohne Abfrage)
echo [INFO] Erstelle virtuelle Python-Umgebung...
python -m venv venv > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNUNG] Virtuelle Umgebung konnte nicht erstellt werden. Fahre mit System-Python fort.
) else (
    :: Virtuelle Umgebung aktivieren
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat > nul 2>&1
    )
)

echo [INFO] Installiere Abhängigkeiten...

:: Abhängigkeiten installieren mit optimierter Performance
python -m pip install --upgrade pip --quiet --disable-pip-version-check
python -m pip install --quiet --disable-pip-version-check ^
    pyVmomi>=7.0.0 ^
    Flask>=2.0.0 ^
    Flask-WTF>=1.0.0 ^
    reportlab>=3.6.0 ^
    python-docx>=0.8.11 ^
    Jinja2>=3.0.0 ^
    humanize>=3.0.0

if %errorlevel% neq 0 (
    echo [FEHLER] Abhängigkeiten konnten nicht installiert werden.
    pause
    exit /b 1
)

:: Erstelle die optimierte run.bat-Datei
echo @echo off> run.bat
echo :: VMware vSphere Reporter v19.0 - Produktionsversion>> run.bat
echo.>> run.bat
echo :: Virtuelle Umgebung aktivieren, falls vorhanden>> run.bat
echo if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat > nul 2>&1>> run.bat
echo.>> run.bat
echo :: Starte die Anwendung>> run.bat
echo python run.py %*>> run.bat

echo [INFO] Setup erfolgreich abgeschlossen!
echo [INFO] Starte VMware vSphere Reporter...

:: Automatisch die Anwendung starten
call run.bat