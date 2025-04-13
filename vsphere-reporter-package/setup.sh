#!/bin/bash

# VMware vSphere Reporter Setup Script for Linux
# This script helps to set up the VMware vSphere Reporter on Linux systems
# Tested on OpenSuse Tumbleweed

echo "VMware vSphere Reporter - Setup Script"
echo "======================================="
echo

# Detect distro
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    echo "Detected Linux distribution: $PRETTY_NAME"
else
    echo "Unable to detect Linux distribution. Assuming generic Linux."
    DISTRO="unknown"
fi

# Create directories
echo "Creating directory structure..."
mkdir -p logs

# Check Python installation
echo "Checking Python installation..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo "Found $PYTHON_VERSION"
else
    echo "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Install dependencies based on distro
echo "Installing required system packages..."
case $DISTRO in
    "opensuse"*)
        echo "Installing packages for OpenSUSE..."
        sudo zypper install -y python3-tk python3-pip
        ;;
    "ubuntu"|"debian")
        echo "Installing packages for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-pip
        ;;
    "fedora"|"rhel"|"centos")
        echo "Installing packages for Fedora/RHEL/CentOS..."
        sudo dnf install -y python3-tkinter python3-pip
        ;;
    *)
        echo "Unknown distribution. Please manually install Tkinter for Python 3."
        echo "For OpenSuse: sudo zypper install python3-tk"
        echo "For Debian/Ubuntu: sudo apt-get install python3-tk"
        echo "For Fedora/RHEL/CentOS: sudo dnf install python3-tkinter"
        ;;
esac

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r vsphere_reporter_requirements.txt

# Make scripts executable
echo "Making scripts executable..."
chmod +x vsphere_reporter_linux.py
chmod +x vsphere_reporter_cli.py

# Setup complete
echo
echo "Setup complete!"
echo "You can now run the VMware vSphere Reporter:"
echo "- GUI: ./vsphere_reporter_linux.py"
echo "- CLI: ./vsphere_reporter_cli.py --help"
echo
echo "For more information, see the documentation in the docs/ directory."