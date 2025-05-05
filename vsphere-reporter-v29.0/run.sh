#!/bin/bash

echo "Starting VMware vSphere Reporter Web Edition v29.0..."
echo
echo "This terminal will remain open while the application is running."
echo "Press Ctrl+C to stop the application."
echo

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in your PATH."
    echo "Please install Python 3.8 or higher and try again."
    echo
    exit 1
fi

# Get the port number from environment or use default
PORT=${PORT:-5000}

echo "Opening your browser to http://localhost:$PORT when the server is ready..."
echo

# Check the operating system to determine how to open the browser
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Try to detect the desktop environment and use appropriate browser opener
    if command -v xdg-open &> /dev/null; then
        (sleep 3 && xdg-open "http://localhost:$PORT") &
    elif command -v gnome-open &> /dev/null; then
        (sleep 3 && gnome-open "http://localhost:$PORT") &
    elif command -v kde-open &> /dev/null; then
        (sleep 3 && kde-open "http://localhost:$PORT") &
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    (sleep 3 && open "http://localhost:$PORT") &
fi

# Start the application
PORT=$PORT python3 app.py

echo
echo "Application stopped."