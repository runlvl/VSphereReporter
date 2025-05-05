#!/bin/bash

echo "VMware vSphere Reporter Web Edition v29.0 - Setup"
echo "===================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in your PATH."
    echo "Please install Python 3.8 or higher and try again."
    echo
    exit 1
fi

# Check Python version
PYVER=$(python3 --version 2>&1)
echo "Detected Python version: $PYVER"
echo

# Create virtual environment (optional)
read -p "Do you want to create a virtual environment? (y/n) " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ -d "venv" ]; then
        echo "Virtual environment created successfully."
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "Failed to create virtual environment. Continuing with system Python..."
    fi
fi

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "Error: Failed to install dependencies."
    echo "Please check the error messages above and try again."
    echo
    exit 1
fi

# Create reports and logs directories
mkdir -p reports logs

# Make script executable
chmod +x run.sh

echo
echo "Dependencies installed successfully!"
echo
echo "You can now run the application using './run.sh'"
echo