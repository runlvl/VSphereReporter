@echo off
:: VMware vSphere Reporter v19.1 - Optimiertes Setup-Skript fuer Windows (Schnellversion)
setlocal

echo VMware vSphere Reporter v19.1 - Setup wird ausgefuehrt...
echo =====================================================================

:: Python-Installation pruefen
echo Pruefe Python-Installation...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Python 3.8 oder hoeher und fuehren Sie dieses Skript erneut aus.
    pause
    exit /b 1
)
echo [OK] Python ist installiert.

:: Pip-Installation pruefen
echo Pruefe pip-Installation...
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Installiere pip...
    python -m ensurepip --default-pip --quiet
    if %errorlevel% neq 0 (
        echo [FEHLER] Pip konnte nicht installiert werden.
        pause
        exit /b 1
    )
)
echo [OK] Pip ist installiert.

:: Virtuelle Umgebung erstellen
echo Erstelle virtuelle Python-Umgebung...
python -m venv venv > nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Virtuelle Umgebung nicht erstellt. Fahre mit System-Python fort.
) else (
    :: Virtuelle Umgebung aktivieren
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat > nul 2>&1
        echo [OK] Virtuelle Umgebung aktiviert.
    )
)

:: Alle Pakete in einem Schritt installieren
echo Installiere alle Abhaengigkeiten...
python -m pip install --upgrade pip --quiet --disable-pip-version-check
python -m pip install --quiet --disable-pip-version-check pyVmomi>=7.0.0 Flask>=2.0.0 Flask-WTF>=1.0.0 reportlab>=3.6.0 python-docx>=0.8.11 Jinja2>=3.0.0 humanize>=3.0.0

if %errorlevel% neq 0 (
    echo [FEHLER] Abhaengigkeiten konnten nicht installiert werden.
    pause
    exit /b 1
)

echo [OK] Alle Abhaengigkeiten wurden erfolgreich installiert.

:: Erstelle die optimierte run.bat-Datei (direkt mit app.py, nicht run.py)
echo @echo off> run.bat
echo :: VMware vSphere Reporter v19.1 - Schnellstart>> run.bat
echo echo Starte VMware vSphere Reporter...>> run.bat
echo set PYTHONWARNINGS=ignore>> run.bat
echo set FLASK_ENV=production>> run.bat
echo set FLASK_APP=app.py>> run.bat
echo set FLASK_RUN_HOST=0.0.0.0>> run.bat
echo set FLASK_RUN_PORT=5000>> run.bat
echo.>> run.bat
echo :: Virtuelle Umgebung aktivieren, falls vorhanden>> run.bat
echo if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat ^> nul 2^> nul>> run.bat
echo.>> run.bat
echo :: Browser starten>> run.bat
echo start http://localhost:5000>> run.bat
echo.>> run.bat
echo :: App direkt starten>> run.bat
echo python app.py>> run.bat
echo.>> run.bat
echo pause>> run.bat

echo [INFO] Setup erfolgreich abgeschlossen!
echo [INFO] Starte VMware vSphere Reporter...

:: Automatisch die Anwendung starten
call run.bat