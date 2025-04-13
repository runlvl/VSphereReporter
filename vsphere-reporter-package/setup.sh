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

# Variable to track if we're using a virtual environment
USING_VENV=0
VENV_PATH="./venv"

# Create virtual environment
create_venv() {
    echo "Creating Python virtual environment..."
    python3 -m venv $VENV_PATH
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Trying to install venv module first..."
        case $DISTRO in
            "opensuse"*)
                sudo zypper install -y python3-venv
                ;;
            "ubuntu"|"debian")
                sudo apt-get install -y python3-venv
                ;;
            "fedora"|"rhel"|"centos")
                sudo dnf install -y python3-venv
                ;;
        esac
        
        python3 -m venv $VENV_PATH
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to create virtual environment. Please try manually:"
            echo "python3 -m venv ./venv"
            return 1
        fi
    fi
    
    echo "Virtual environment created at $VENV_PATH"
    USING_VENV=1
    return 0
}

# Install dependencies based on distro
echo "Installing required system packages..."
case $DISTRO in
    "opensuse"*)
        echo "Installing packages for OpenSUSE..."
        sudo zypper install -y python3-tk python3-pip python3-venv python3-devel gcc
        # OpenSUSE might need additional development tools for some Python packages
        sudo zypper install -y patterns-devel-base-devel_basis
        
        # For OpenSuse, we need to use a virtual environment due to the externally-managed-environment
        echo "OpenSuse uses externally-managed environment. Setting up virtual environment..."
        create_venv
        ;;
    "ubuntu"|"debian")
        echo "Installing packages for Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-pip python3-venv python3-dev build-essential
        
        # Check if externally-managed-environment exists
        if python3 -m pip install --upgrade pip 2>&1 | grep -q "externally-managed-environment"; then
            echo "Detected externally-managed environment. Setting up virtual environment..."
            create_venv
        fi
        ;;
    "fedora"|"rhel"|"centos")
        echo "Installing packages for Fedora/RHEL/CentOS..."
        sudo dnf install -y python3-tkinter python3-pip python3-venv python3-devel gcc
        
        # Check if externally-managed-environment exists
        if python3 -m pip install --upgrade pip 2>&1 | grep -q "externally-managed-environment"; then
            echo "Detected externally-managed environment. Setting up virtual environment..."
            create_venv
        fi
        ;;
    *)
        echo "Unknown distribution. Please manually install the following packages:"
        echo "- Tkinter for Python 3"
        echo "- Python development headers"
        echo "- C/C++ compiler (gcc)"
        echo
        echo "For OpenSuse: sudo zypper install python3-tk python3-devel python3-venv gcc"
        echo "For Debian/Ubuntu: sudo apt-get install python3-tk python3-dev python3-venv build-essential"
        echo "For Fedora/RHEL/CentOS: sudo dnf install python3-tkinter python3-devel python3-venv gcc"
        echo
        echo "Creating virtual environment as fallback..."
        create_venv
        ;;
esac

# Install Python dependencies
echo "Installing Python dependencies..."
echo "This may take a few minutes..."

# Setup the correct pip command based on virtual environment usage
if [ $USING_VENV -eq 1 ]; then
    echo "Using virtual environment at $VENV_PATH"
    PIP_CMD="$VENV_PATH/bin/pip"
    PYTHON_CMD="$VENV_PATH/bin/python"
    
    # Activate the virtual environment
    echo "Activating virtual environment..."
    source $VENV_PATH/bin/activate
else
    PIP_CMD="python3 -m pip"
    PYTHON_CMD="python3"
fi

# Upgrade pip to the latest version
echo "Upgrading pip to the latest version..."
$PIP_CMD install --upgrade pip

# Install PyVmomi first (explicitly) to ensure it's properly set up
echo "Installing PyVmomi (VMware vSphere Python SDK)..."
$PIP_CMD install --upgrade pyVmomi six requests

# Install all other dependencies
echo "Installing remaining dependencies..."
$PIP_CMD install --upgrade -r vsphere_reporter_requirements.txt

# Verify that critical packages were installed
echo "Verifying critical packages..."
if $PYTHON_CMD -c "import pyVim" 2>/dev/null; then
    echo "✓ PyVim module successfully installed"
else
    echo "⚠ WARNING: PyVim module not found. Try running manually: $PIP_CMD install pyVmomi"
fi

if $PYTHON_CMD -c "import pyVmomi" 2>/dev/null; then
    echo "✓ PyVmomi module successfully installed"
else
    echo "⚠ WARNING: PyVmomi module not found. Try running manually: $PIP_CMD install pyVmomi"
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x vsphere_reporter_linux.py
chmod +x vsphere_reporter_cli.py

# Create launcher scripts if using venv
if [ $USING_VENV -eq 1 ]; then
    echo "Creating launcher scripts for virtual environment..."
    
    # Create launcher for Linux GUI
    echo '#!/bin/bash
# Launcher for VMware vSphere Reporter Linux GUI
source "'$VENV_PATH/bin/activate'"
python3 vsphere_reporter_linux.py "$@"
' > run_linux_gui.sh
    chmod +x run_linux_gui.sh
    
    # Create launcher for CLI
    echo '#!/bin/bash
# Launcher for VMware vSphere Reporter CLI
source "'$VENV_PATH/bin/activate'"
python3 vsphere_reporter_cli.py "$@"
' > run_cli.sh
    chmod +x run_cli.sh
    
    echo "Created launcher scripts: run_linux_gui.sh and run_cli.sh"
fi

# Setup complete
echo
echo "Setup complete!"
echo "You can now run the VMware vSphere Reporter:"

if [ $USING_VENV -eq 1 ]; then
    echo "Using virtual environment launcher scripts:"
    echo "- GUI (recommended): ./run_linux_gui.sh"
    echo "- CLI: ./run_cli.sh --help"
    echo
    echo "Alternatively, you can activate the virtual environment and run directly:"
    echo "  source $VENV_PATH/bin/activate"
    echo "  python3 ./vsphere_reporter_linux.py"
else
    echo "- GUI (recommended): python3 ./vsphere_reporter_linux.py"
    echo "- CLI: python3 ./vsphere_reporter_cli.py --help"
fi

echo
echo "For more information, see the documentation in the docs/ directory."