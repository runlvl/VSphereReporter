@echo off
setlocal enabledelayedexpansion
echo VMware vSphere Reporter - Setup Script
echo =======================================
echo.

rem Set up variables for Python executables to try
set PYTHON_EXES=python python3 py

rem Check Python installation through various possible commands
echo Checking Python installation...
set PYTHON_FOUND=0
set PYTHON_CMD=

for %%P in (%PYTHON_EXES%) do (
    echo Trying to find Python with "%%P" command...
    %%P --version > nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set PYTHON_FOUND=1
        set PYTHON_CMD=%%P
        echo Found Python with command: %%P
        goto :python_found
    )
)

:check_py_launcher
echo Checking Python launcher (py)...
py --version > nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Found Python launcher.
    echo Checking for Python 3...
    py -3 --version > nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set PYTHON_FOUND=1
        set PYTHON_CMD=py -3
        echo Found Python 3 with py launcher
        goto :python_found
    )
)

rem Check Python in common installation locations
echo Checking Python in standard installation locations...
if exist "C:\Python310\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD=C:\Python310\python.exe
    echo Found Python at C:\Python310\python.exe
    goto :python_found
)

if exist "C:\Python39\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD=C:\Python39\python.exe
    echo Found Python at C:\Python39\python.exe
    goto :python_found
)

if exist "C:\Program Files\Python310\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD="C:\Program Files\Python310\python.exe"
    echo Found Python at C:\Program Files\Python310\python.exe
    goto :python_found
)

if exist "C:\Program Files\Python39\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD="C:\Program Files\Python39\python.exe"
    echo Found Python at C:\Program Files\Python39\python.exe
    goto :python_found
)

if exist "C:\Program Files (x86)\Python310\python.exe" (
    set PYTHON_FOUND=1
    set PYTHON_CMD="C:\Program Files (x86)\Python310\python.exe"
    echo Found Python at C:\Program Files (x86)\Python310\python.exe
    goto :python_found
)

rem Check in AppData locations (user installed Python)
echo Checking in AppData locations...
for %%V in (311 310 39 38) do (
    set APPDATA_PYTHON=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe
    echo Checking %APPDATA_PYTHON%
    if exist "!APPDATA_PYTHON!" (
        set PYTHON_FOUND=1
        set PYTHON_CMD="!APPDATA_PYTHON!"
        echo Found Python at !APPDATA_PYTHON!
        goto :python_found
    )
)

rem Check Windows Store Python installations
echo Checking Windows Store Python installations...
for %%V in (311 310 39 38) do (
    set STORE_PYTHON=%LOCALAPPDATA%\Microsoft\WindowsApps\python%%V.exe
    echo Checking !STORE_PYTHON!
    if exist "!STORE_PYTHON!" (
        set PYTHON_FOUND=1
        set PYTHON_CMD="!STORE_PYTHON!"
        echo Found Python at !STORE_PYTHON!
        goto :python_found
    )
)

:python_not_found
if %PYTHON_FOUND% equ 0 (
    echo Python not found. Please install Python 3.8 or higher.
    echo You can download Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, run this setup script again.
    pause
    exit /b 1
)

:python_found
echo Python found! Checking version...
%PYTHON_CMD% -c "import sys; print(f'Using Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"

rem Create directories
echo Creating directory structure...
if not exist logs mkdir logs

rem Install dependencies
echo Installing Python dependencies...
for %%P in (pip pip3) do (
    %%P --version > nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo Using %%P to install dependencies...
        %%P install -r vsphere_reporter_requirements.txt
        if !ERRORLEVEL! equ 0 (
            echo Dependencies installed successfully with %%P.
            goto :dependencies_installed
        ) else (
            echo Failed to install with %%P, trying alternative methods...
        )
    )
)

rem Try pip with the found Python command
echo Using Python module pip...
%PYTHON_CMD% -m pip --version > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo Installing with %PYTHON_CMD% -m pip...
    %PYTHON_CMD% -m pip install -r vsphere_reporter_requirements.txt
    if !ERRORLEVEL! equ 0 (
        echo Dependencies installed successfully with Python module pip.
        goto :dependencies_installed
    )
)

rem If requirements file is missing, install explicitly
echo Checking if requirements file exists...
if not exist vsphere_reporter_requirements.txt (
    echo vsphere_reporter_requirements.txt not found, installing dependencies explicitly...
    %PYTHON_CMD% -m pip install pyVmomi>=7.0.0 PyQt5>=5.15.0 reportlab>=3.6.0 python-docx>=0.8.11 jinja2>=3.0.0 humanize>=3.0.0 six>=1.16.0 requests>=2.25.0
) else (
    rem Try installing each dependency individually
    echo Attempting to install dependencies individually...
    for /F "tokens=*" %%i in (vsphere_reporter_requirements.txt) do (
        echo Installing %%i...
        %PYTHON_CMD% -m pip install %%i
    )
)

:dependencies_installed
rem Setup complete
echo.
echo Setup complete!
echo You can now run the VMware vSphere Reporter:
echo - GUI: %PYTHON_CMD% vsphere_reporter.py
echo.
echo For more information, see the documentation in the docs/ directory.
pause