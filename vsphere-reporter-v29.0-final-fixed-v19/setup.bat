@echo off
:: VMware vSphere Reporter v19 Setup-Skript für Windows

echo VMware vSphere Reporter v19.0 - Setup-Skript
echo =============================================
echo.

:: Prüfen, ob Python installiert ist
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python ist nicht installiert oder nicht im PATH. Bitte installieren Sie Python 3.8 oder höher.
    pause
    exit /b 1
)

:: Python-Version prüfen
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python-Version %PYTHON_VERSION% gefunden. OK!

:: Überprüfen, ob pip installiert ist
python -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo pip ist nicht installiert. Wird installiert...
    python -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        echo Fehler: pip konnte nicht installiert werden.
        pause
        exit /b 1
    )
)

echo pip ist installiert. OK!

:: Prüfen, ob virtuelle Umgebung erstellt werden soll
set /p USE_VENV="Möchten Sie eine virtuelle Python-Umgebung verwenden? (empfohlen) [J/n]: "
if /i "%USE_VENV%" == "n" (
    set USE_VENV=false
) else (
    set USE_VENV=true
)

:: Virtuelle Umgebung erstellen, wenn gewünscht
if %USE_VENV% == true (
    echo Erstelle virtuelle Python-Umgebung...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Fehler: Virtuelle Umgebung konnte nicht erstellt werden.
        pause
        exit /b 1
    )
    
    :: Virtuelle Umgebung aktivieren
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo Virtuelle Umgebung aktiviert.
    ) else (
        echo Fehler: Die Aktivierungsdatei der virtuellen Umgebung wurde nicht gefunden.
        pause
        exit /b 1
    )
)

echo Installiere Abhängigkeiten...

:: Abhängigkeiten installieren
python -m pip install --upgrade pip
python -m pip install pyVmomi>=7.0.0 Flask>=2.0.0 Flask-WTF>=1.0.0 reportlab>=3.6.0 python-docx>=0.8.11 Jinja2>=3.0.0 humanize>=3.0.0
if %errorlevel% neq 0 (
    echo Fehler: Abhängigkeiten konnten nicht installiert werden.
    pause
    exit /b 1
)

echo Abhängigkeiten erfolgreich installiert.

:: Erstelle die run.bat-Datei
echo @echo off> run.bat
echo :: VMware vSphere Reporter v19 Starter-Skript für Windows>> run.bat
echo.>> run.bat
echo :: Prüfen, ob virtuelle Umgebung existiert und aktivieren>> run.bat
echo if exist "venv\Scripts\activate.bat" (>> run.bat
echo     call venv\Scripts\activate.bat>> run.bat
echo     echo Virtuelle Umgebung aktiviert.>> run.bat
echo )>> run.bat
echo.>> run.bat
echo :: Starte die Anwendung>> run.bat
echo python run.py %*>> run.bat

echo.
echo Setup abgeschlossen!
echo Um die Anwendung zu starten, führen Sie 'run.bat' aus.
echo.

:: Frage, ob die Anwendung direkt gestartet werden soll
set /p START_APP="Möchten Sie die Anwendung jetzt starten? [J/n]: "
if /i not "%START_APP%" == "n" (
    echo Starte VMware vSphere Reporter...
    call run.bat
)

pause