@echo off
echo Starte VMware vSphere Reporter...
set PYTHONWARNINGS=ignore
set FLASK_ENV=production
set FLASK_APP=app.py
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=5000

REM Starte Browser
start http://localhost:5000
python app.py

pause