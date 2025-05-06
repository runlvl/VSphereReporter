@echo off
:: VMware vSphere Reporter v19.1 - Optimiertes Setup-Skript fuer Windows
setlocal enabledelayedexpansion

echo VMware vSphere Reporter v19.1 - Setup wird ausgefuehrt...
echo =====================================================================

:: Fortschrittsbalken-Funktionen
:drawProgressBar
set /a filled=%1
set /a total=%2
set bar=
set /a empty=total-filled

:: Fortschritts-Prozentsatz berechnen
set /a percent=(filled*100)/total

:: Fortschrittsbalken anzeigen mit Prozentsatz
call :printBar %filled% %total% %percent%
exit /b

:printBar
set /a barSize=50
set /a filledSize=(%1*barSize)/%2
set /a emptySize=barSize-filledSize

set progressBar=[
for /l %%i in (1,1,%filledSize%) do set progressBar=!progressBar!#
for /l %%i in (1,1,%emptySize%) do set progressBar=!progressBar!-
set progressBar=!progressBar!] !3!%%

echo !progressBar!
exit /b

:: Anfangswerte setzen
set totalSteps=7
set currentStep=0

:: Pruefen, ob Python installiert ist
set /a currentStep+=1
echo [Schritt !currentStep!/%totalSteps%] Pruefe Python-Installation...
call :drawProgressBar !currentStep! %totalSteps%

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH.
    echo Bitte installieren Sie Python 3.8 oder hoeher und fuehren Sie dieses Skript erneut aus.
    pause
    exit /b 1
)

:: Ueberpruefen, ob pip installiert ist
set /a currentStep+=1
echo [Schritt !currentStep!/%totalSteps%] Pruefe pip-Installation...
call :drawProgressBar !currentStep! %totalSteps%

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
set /a currentStep+=1
echo [Schritt !currentStep!/%totalSteps%] Erstelle virtuelle Python-Umgebung...
call :drawProgressBar !currentStep! %totalSteps%

python -m venv venv > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNUNG] Virtuelle Umgebung konnte nicht erstellt werden. Fahre mit System-Python fort.
) else (
    :: Virtuelle Umgebung aktivieren
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat > nul 2>&1
    )
)

:: Upgrade pip
set /a currentStep+=1
echo [Schritt !currentStep!/%totalSteps%] Aktualisiere pip...
call :drawProgressBar !currentStep! %totalSteps%

python -m pip install --upgrade pip --quiet --disable-pip-version-check

:: Installiere Abhaengigkeiten (in Gruppen fuer besseren Fortschrittsbalken)
set /a currentStep+=1
echo [Schritt !currentStep!/%totalSteps%] Installiere pyVmomi und Flask...
call :drawProgressBar !currentStep! %totalSteps%

python -m pip install --quiet --disable-pip-version-check pyVmomi>=7.0.0 Flask>=2.0.0 Flask-WTF>=1.0.0

set /a currentStep+=1
echo [Schritt !currentStep!/%totalSteps%] Installiere reportlab und python-docx...
call :drawProgressBar !currentStep! %totalSteps%

python -m pip install --quiet --disable-pip-version-check reportlab>=3.6.0 python-docx>=0.8.11

set /a currentStep+=1
echo [Schritt !currentStep!/%totalSteps%] Installiere Jinja2 und humanize...
call :drawProgressBar !currentStep! %totalSteps%

python -m pip install --quiet --disable-pip-version-check Jinja2>=3.0.0 humanize>=3.0.0

if %errorlevel% neq 0 (
    echo [FEHLER] Abhaengigkeiten konnten nicht installiert werden.
    pause
    exit /b 1
)

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