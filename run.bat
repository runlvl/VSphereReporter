@echo off
REM Run script for VMware vSphere Reporter
REM This script ensures proper Python environment and launches the application

echo Starting VMware vSphere Reporter...

REM Check if Python is installed and in PATH
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and ensure it's added to your PATH.
    echo See docs/admin_guide.md for installation instructions.
    pause
    exit /b 1
)

REM Check Python version (must be 3.8+)
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set "PYVER=%%I"
echo Detected Python version: %PYVER%

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Run the application
echo Launching application...
pythonw vsphere_reporter.py
if %ERRORLEVEL% NEQ 0 (
    echo Application failed to start properly.
    echo Please check the logs in the logs directory for details.
    echo If this is the first run, you may need to install dependencies with:
    echo pip install -r requirements.txt
    pause
    exit /b 1
)

exit /b 0
