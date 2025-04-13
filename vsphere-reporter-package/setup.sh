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
        sudo zypper install -y python3-tk python3-pip python3-devel gcc
        # OpenSUSE might need additional development tools for some Python packages
        sudo zypper install -y patterns-devel-base-devel_basis
        ;;
    "ubuntu"|"debian")
        echo "Installing packages for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-pip python3-dev build-essential
        ;;
    "fedora"|"rhel"|"centos")
        echo "Installing packages for Fedora/RHEL/CentOS..."
        sudo dnf install -y python3-tkinter python3-pip python3-devel gcc
        ;;
    *)
        echo "Unknown distribution. Please manually install the following packages:"
        echo "- Tkinter for Python 3"
        echo "- Python development headers"
        echo "- C/C++ compiler (gcc)"
        echo
        echo "For OpenSuse: sudo zypper install python3-tk python3-devel gcc"
        echo "For Debian/Ubuntu: sudo apt-get install python3-tk python3-dev build-essential"
        echo "For Fedora/RHEL/CentOS: sudo dnf install python3-tkinter python3-devel gcc"
        ;;
esac

# Upgrade pip to the latest version
echo "Upgrading pip to the latest version..."
python3 -m pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
echo "This may take a few minutes..."

# Install PyVmomi first (explicitly) to ensure it's properly set up
echo "Installing PyVmomi (VMware vSphere Python SDK)..."
python3 -m pip install --upgrade pyVmomi

# Install all other dependencies
echo "Installing remaining dependencies..."
python3 -m pip install --upgrade -r vsphere_reporter_requirements.txt

# Verify that critical packages were installed
echo "Verifying critical packages..."
if python3 -c "import pyVim" 2>/dev/null; then
    echo "✓ PyVim module successfully installed"
else
    echo "⚠ WARNING: PyVim module not found. Try running manually: pip3 install pyVmomi"
fi

if python3 -c "import pyVmomi" 2>/dev/null; then
    echo "✓ PyVmomi module successfully installed"
else
    echo "⚠ WARNING: PyVmomi module not found. Try running manually: pip3 install pyVmomi"
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x vsphere_reporter_linux.py
chmod +x vsphere_reporter_cli.py

# Setup complete
echo
echo "Setup complete!"
echo "You can now run the VMware vSphere Reporter:"
echo "- GUI (recommended): python3 ./vsphere_reporter_linux.py"
echo "- CLI: python3 ./vsphere_reporter_cli.py --help"
echo
echo "NOTE: If you encounter any issues with missing modules, try running:"
echo "  pip3 install pyVmomi>=7.0.0 PyQt5>=5.15.0 reportlab>=3.6.0 python-docx>=0.8.11 jinja2>=3.0.0 humanize>=3.0.0"
echo
echo "For more information, see the documentation in the docs/ directory."