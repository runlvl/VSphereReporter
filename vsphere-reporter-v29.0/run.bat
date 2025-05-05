@echo off
echo Starting VMware vSphere Reporter Web Edition v29.0...
echo.
echo This command window will remain open while the application is running.
echo Press Ctrl+C to stop the application.
echo.

rem Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3.8 or higher and try again.
    echo.
    pause
    exit /b 1
)

rem Get the port number from environment or use default
set PORT=5000
if not "%VSPHERE_REPORTER_PORT%"=="" set PORT=%VSPHERE_REPORTER_PORT%

echo Opening your browser to http://localhost:%PORT% when the server is ready...
echo.

rem Open browser after a short delay
start "" timeout /t 3 /nobreak > NUL && start http://localhost:%PORT%

rem Start the application
set PORT=%PORT%
python app.py

echo.
echo Application stopped.