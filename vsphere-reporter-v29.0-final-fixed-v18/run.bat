@echo off
echo Starte VMware vSphere Reporter v18 (Diagnose-Version)...
echo.

set FLASK_APP=app.py
set FLASK_ENV=production
set PYTHONPATH=%CD%
set VSPHERE_REPORTER_DEBUG=1

python -m flask run --host=0.0.0.0 --port=5000

pause