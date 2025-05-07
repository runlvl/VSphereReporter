@echo off
:: Bechtle vSphere Reporter v0.1 - Intelligenter Starter für Windows
echo Starte Bechtle vSphere Reporter v0.1 (intelligente Portauswahl)...

:: Virtuelle Umgebung aktivieren, falls vorhanden
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat > nul 2> nul

:: Starte den Python-Starter
python start.py

pause