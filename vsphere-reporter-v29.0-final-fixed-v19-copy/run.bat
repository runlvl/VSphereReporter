@echo off
echo Starte VMware vSphere Reporter...
set PYTHONWARNINGS=ignore
set FLASK_ENV=production
set WERKZEUG_SERVER_FD=
set FLASK_APP=app.py
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=5000

REM Warte kurz, damit die Umgebungsvariablen korrekt gesetzt werden
timeout /t 1 /nobreak >nul

REM Starte Browser
start http://localhost:5000

REM Starte die Anwendung direkt, ohne run.py zu verwenden
python app.py

pause