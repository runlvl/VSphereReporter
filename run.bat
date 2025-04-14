@echo off
setlocal enabledelayedexpansion
REM Run script for VMware vSphere Reporter
REM This script ensures proper Python environment and launches the application

echo Starting VMware vSphere Reporter...

rem Set up variables for Python executables to try
set PYTHON_EXES=python python3 py pythonw py -3

rem Check Python installation through various possible commands
echo Checking Python installation...
set PYTHON_FOUND=0
set PYTHON_CMD=
set PYTHONW_CMD=pythonw

for %%P in (%PYTHON_EXES%) do (
    %%P --version > nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set PYTHON_FOUND=1
        set PYTHON_CMD=%%P
        echo Found Python with command: %%P
        goto :python_found
    )
)

rem Check Python in common installation locations
if exist "C:\Python310\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD=C:\Python310\python.exe
    set PYTHONW_CMD=C:\Python310\pythonw.exe
    goto :python_found
)

if exist "C:\Python39\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD=C:\Python39\python.exe
    set PYTHONW_CMD=C:\Python39\pythonw.exe
    goto :python_found
)

if exist "C:\Program Files\Python310\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD="C:\Program Files\Python310\python.exe"
    set PYTHONW_CMD="C:\Program Files\Python310\pythonw.exe"
    goto :python_found
)

rem Check in AppData locations (user installed Python)
for %%V in (311 310 39 38) do (
    set APPDATA_PYTHON=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe
    if exist "!APPDATA_PYTHON!" (
        set PYTHON_FOUND=1
        set PYTHON_CMD="!APPDATA_PYTHON!"
        set PYTHONW_CMD="!APPDATA_PYTHON:python.exe=pythonw.exe!"
        goto :python_found
    )
)

rem Check Windows Store Python installations
for %%V in (311 310 39 38) do (
    set STORE_PYTHON=%LOCALAPPDATA%\Microsoft\WindowsApps\python%%V.exe
    if exist "!STORE_PYTHON!" (
        set PYTHON_FOUND=1
        set PYTHON_CMD="!STORE_PYTHON!"
        set PYTHONW_CMD="!STORE_PYTHON:python.exe=pythonw.exe!"
        goto :python_found
    )
)

:python_not_found
if %PYTHON_FOUND% equ 0 (
    echo Python not found. Please install Python 3.8 or higher.
    echo You can download Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

:python_found
echo Python found! Checking version...
%PYTHON_CMD% -c "import sys; print(f'Using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Run the application
echo Launching application...
if "!PYTHON_CMD!" == "py -3" (
    py -3 vsphere_reporter.py
) else if exist "!PYTHONW_CMD!" (
    !PYTHONW_CMD! vsphere_reporter.py
) else (
    !PYTHON_CMD! vsphere_reporter.py
)

if !ERRORLEVEL! NEQ 0 (
    echo Application failed to start properly.
    echo Please check the logs in the logs directory for details.
    echo If this is the first run, you may need to install dependencies with setup.bat
    pause
    exit /b 1
)

exit /b 0
