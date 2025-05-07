@echo off
:: VMware vSphere Reporter v19.1 - Schnellstart
echo Starte VMware vSphere Reporter...
set PYTHONWARNINGS=ignore
set FLASK_ENV=production
set FLASK_APP=app.py
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=5000

:: Virtuelle Umgebung aktivieren, falls vorhanden
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat > nul 2> nul

:: Browser starten
start http://localhost:5000

:: App direkt starten
python app.py

pause