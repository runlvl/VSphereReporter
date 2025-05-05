@echo off
echo VMware vSphere Reporter Web Edition v29.0 - Setup
echo ====================================================
echo.
echo This script will install the required dependencies for the application.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3.8 or higher and try again.
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYVER=%%I
echo Detected Python version: %PYVER%
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to install dependencies.
    echo Please check the error messages above and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.
echo You can now run the application using run.bat
echo.
pause