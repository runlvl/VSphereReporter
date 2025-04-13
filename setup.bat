@echo off
echo VMware vSphere Reporter - Setup Script
echo =======================================
echo.

rem Check Python installation
echo Checking Python installation...
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

rem Create directories
echo Creating directory structure...
if not exist logs mkdir logs

rem Install dependencies
echo Installing Python dependencies...
pip install -r vsphere_reporter_requirements.txt

rem Setup complete
echo.
echo Setup complete!
echo You can now run the VMware vSphere Reporter:
echo - GUI: python vsphere_reporter.py
echo.
echo For more information, see the documentation in the docs/ directory.
pause