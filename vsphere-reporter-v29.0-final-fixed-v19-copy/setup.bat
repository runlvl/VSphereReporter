@echo off
:: VMware vSphere Reporter v19.1 - Optimiertes Setup-Skript fuer Windows
setlocal

echo VMware vSphere Reporter v19.1 - Setup wird ausgefuehrt...
echo =====================================================================

:: Alternative Fortschrittsanzeige
set total_steps=7
set current=0

echo Fortschrittsanzeige: (0%% abgeschlossen)
echo.

:: Schritt 1: Python-Installation pruefen
set /a current+=1
set /a percent=(current*100)/total_steps
echo **** Schritt %current%/%total_steps% (%percent%%% abgeschlossen) ****
echo [Schritt %current%/%total_steps%] Pruefe Python-Installation...

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Python 3.8 oder hoeher und fuehren Sie dieses Skript erneut aus.
    pause
    exit /b 1
)

echo [OK] Python ist installiert.
echo.

:: Schritt 2: Pip-Installation pruefen
set /a current+=1
set /a percent=(current*100)/total_steps
echo **** Schritt %current%/%total_steps% (%percent%%% abgeschlossen) ****
echo [Schritt %current%/%total_steps%] Pruefe pip-Installation...

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

echo [OK] Pip ist installiert.
echo.

:: Schritt 3: Virtuelle Umgebung erstellen
set /a current+=1
set /a percent=(current*100)/total_steps
echo **** Schritt %current%/%total_steps% (%percent%%% abgeschlossen) ****
echo [Schritt %current%/%total_steps%] Erstelle virtuelle Python-Umgebung...

python -m venv venv > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNUNG] Virtuelle Umgebung konnte nicht erstellt werden. Fahre mit System-Python fort.
) else (
    :: Virtuelle Umgebung aktivieren
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat > nul 2>&1
        echo [OK] Virtuelle Umgebung erstellt und aktiviert.
    )
)
echo.

:: Schritt 4: Pip aktualisieren
set /a current+=1
set /a percent=(current*100)/total_steps
echo **** Schritt %current%/%total_steps% (%percent%%% abgeschlossen) ****
echo [Schritt %current%/%total_steps%] Aktualisiere pip...

python -m pip install --upgrade pip --quiet --disable-pip-version-check
echo [OK] Pip aktualisiert.
echo.

:: Schritt 5: PyVmomi und Flask installieren
set /a current+=1
set /a percent=(current*100)/total_steps
echo **** Schritt %current%/%total_steps% (%percent%%% abgeschlossen) ****
echo [Schritt %current%/%total_steps%] Installiere pyVmomi und Flask...

python -m pip install --quiet --disable-pip-version-check pyVmomi>=7.0.0 Flask>=2.0.0 Flask-WTF>=1.0.0
echo [OK] pyVmomi und Flask installiert.
echo.

:: Schritt 6: Reportlab und python-docx installieren
set /a current+=1
set /a percent=(current*100)/total_steps
echo **** Schritt %current%/%total_steps% (%percent%%% abgeschlossen) ****
echo [Schritt %current%/%total_steps%] Installiere reportlab und python-docx...

python -m pip install --quiet --disable-pip-version-check reportlab>=3.6.0 python-docx>=0.8.11
echo [OK] reportlab und python-docx installiert.
echo.

:: Schritt 7: Jinja2 und humanize installieren
set /a current+=1
set /a percent=(current*100)/total_steps
echo **** Schritt %current%/%total_steps% (%percent%%% abgeschlossen) ****
echo [Schritt %current%/%total_steps%] Installiere Jinja2 und humanize...

python -m pip install --quiet --disable-pip-version-check Jinja2>=3.0.0 humanize>=3.0.0
echo [OK] Jinja2 und humanize installiert.
echo.

if %errorlevel% neq 0 (
    echo [FEHLER] Abhaengigkeiten konnten nicht installiert werden.
    pause
    exit /b 1
)

echo **** Installation abgeschlossen (100%% abgeschlossen) ****
echo [Installation abgeschlossen] Alle Abhaengigkeiten wurden erfolgreich installiert.

:: Erstelle die optimierte run.bat-Datei (direkt mit app.py, nicht run.py)
echo @echo off> run.bat
echo :: VMware vSphere Reporter v19.1 - Produktionsversion>> run.bat
echo echo Starte VMware vSphere Reporter...>> run.bat
echo.>> run.bat
echo :: Umgebungsvariablen setzen und WERKZEUG-Problem vermeiden>> run.bat
echo set PYTHONWARNINGS=ignore>> run.bat
echo set FLASK_ENV=production>> run.bat
echo set WERKZEUG_SERVER_FD=>> run.bat
echo set FLASK_APP=app.py>> run.bat
echo set FLASK_RUN_HOST=0.0.0.0>> run.bat
echo set FLASK_RUN_PORT=5000>> run.bat
echo.>> run.bat
echo :: Virtuelle Umgebung aktivieren, falls vorhanden>> run.bat
echo if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat ^> nul 2^>^&1>> run.bat
echo.>> run.bat
echo :: Warte kurz, damit die Umgebungsvariablen korrekt gesetzt werden>> run.bat
echo timeout /t 1 /nobreak ^>nul>> run.bat
echo.>> run.bat
echo :: Starte Browser>> run.bat
echo start http://localhost:5000>> run.bat
echo.>> run.bat
echo :: Starte die Anwendung direkt, ohne run.py zu verwenden>> run.bat
echo python app.py>> run.bat
echo.>> run.bat
echo pause>> run.bat

echo [INFO] Setup erfolgreich abgeschlossen!
echo [INFO] Starte VMware vSphere Reporter...

:: Automatisch die Anwendung starten
call run.bat