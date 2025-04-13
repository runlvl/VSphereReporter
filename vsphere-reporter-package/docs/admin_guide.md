# VMware vSphere Reporter - Administrator Guide

## Overview

VMware vSphere Reporter is a comprehensive tool for generating detailed reports about VMware vSphere environments. This guide provides instructions for installing and configuring the tool on both Windows and Linux operating systems.

## System Requirements

### Hardware Requirements
- Processor: 2 GHz dual-core processor or higher
- Memory: 4 GB RAM minimum (8 GB recommended)
- Disk Space: 500 MB for application and dependencies
- Display: 1280x720 resolution or higher (for GUI versions)

### Windows Software Requirements
- Operating System: Windows Server 2016/2019/2022 or Windows 10/11
- Python 3.8 or higher
- Internet connection (for initial package installation)
- Network connectivity to vCenter Server

### Linux Software Requirements
- Operating System: Major Linux distributions (Ubuntu, Debian, RHEL, CentOS, OpenSuse)
- Python 3.8 or higher
- Tkinter package (for GUI version)
- Internet connection (for initial package installation)
- Network connectivity to vCenter Server

### vSphere Environment Requirements
- vCenter Server 6.5, 6.7, 7.0, or 8.0
- User account with read permissions to the vSphere environment

## Installation

### Windows Installation

1. **Install Python (if not already installed)**:
   - Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/windows/)
   - During installation, make sure to check "Add Python to PATH"
   - Verify installation by opening Command Prompt and running:
     ```
     python --version
     ```

2. **Download the Application**:
   - Download the latest release from the official repository
   - Extract the ZIP file to a directory of your choice (e.g., `C:\Program Files\VSphereReporter`)

3. **Install Dependencies**:
   - Open Command Prompt as Administrator
   - Navigate to the application directory:
     ```
     cd "C:\Program Files\VSphereReporter"
     ```
   - Install required Python packages:
     ```
     pip install -r requirements.txt
     ```

4. **Launch the Application**:
   - Double-click on `vsphere_reporter.py` to launch
   - Alternatively, run the application from Command Prompt:
     ```
     python vsphere_reporter.py
     ```

### Linux Installation

1. **Install Python and Tkinter (if not already installed)**:
   - For Debian/Ubuntu:
     ```
     sudo apt update
     sudo apt install python3 python3-pip python3-tk
     ```
   - For Red Hat/CentOS:
     ```
     sudo dnf install python3 python3-pip python3-tkinter
     ```
   - For OpenSuse:
     ```
     sudo zypper install python3 python3-pip python3-tk
     ```
   - Verify installation by running:
     ```
     python3 --version
     ```

2. **Download the Application**:
   - Download the latest release from the official repository
   - Extract the archive to a directory of your choice:
     ```
     mkdir -p ~/vsphere-reporter
     tar -xzf vsphere-reporter.tar.gz -C ~/vsphere-reporter
     cd ~/vsphere-reporter
     ```

3. **Install Dependencies**:
   - Install required Python packages:
     ```
     pip3 install -r requirements.txt
     ```

4. **Launch the Application**:
   - For GUI version:
     ```
     python3 vsphere_reporter_linux.py
     ```
   - For command-line version:
     ```
     python3 vsphere_reporter_cli.py --help
     ```

## Configuration

The application does not require configuration files for basic operation. All settings are configured through the user interface or command-line arguments.

### Command-Line Arguments (Linux CLI Version)

The command-line version supports the following arguments:

```
usage: vsphere_reporter_cli.py [-h] --server SERVER --username USERNAME
                             [--password PASSWORD] [--ignore-ssl]
                             [--output-dir OUTPUT_DIR]
                             [--format {html,docx,pdf,all}] [--include-all]
                             [--vms] [--hosts] [--datastores] [--clusters]
                             [--resource-pools] [--networks]

options:
  -h, --help            show this help message and exit
  --server SERVER, -s SERVER
                        vCenter server address
  --username USERNAME, -u USERNAME
                        vCenter username
  --password PASSWORD, -p PASSWORD
                        vCenter password (omit for secure prompt)
  --ignore-ssl, -k      Ignore SSL certificate validation
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Output directory for reports
  --format {html,docx,pdf,all}, -f {html,docx,pdf,all}
                        Report format (html, docx, pdf, or all)
  --include-all, -a     Include all optional sections in the report
  --vms                 Include virtual machines section
  --hosts               Include hosts section
  --datastores          Include datastores section
  --clusters            Include clusters section
  --resource-pools      Include resource pools section
  --networks            Include networks section
```

## Security Considerations

### Credentials Management

The application does not store vCenter credentials. They must be provided each time the application is launched. For the command-line version, it is recommended to omit the password parameter and enter it when prompted to avoid leaving credentials in command history.

### Network Access

The application requires network access to the vCenter Server. Ensure that the machine running the application has appropriate network connectivity and firewall rules to allow this communication.

## Troubleshooting

### Common Issues

1. **Connection Failures**:
   - Verify network connectivity to the vCenter Server
   - Check that the provided credentials are correct
   - Ensure that the user account has sufficient permissions

2. **Export Failures**:
   - Verify that the application has write permissions to the output directory
   - Check that enough disk space is available

3. **GUI Issues on Linux**:
   - If the Tkinter GUI doesn't display properly, verify that python3-tk is installed
   - As a fallback, use the command-line version (vsphere_reporter_cli.py)

### Log Files

The application logs detailed information to:
- Windows: `C:\Users\<Username>\AppData\Local\VSphereReporter\logs\vsphere_reporter.log`
- Linux: `~/vsphere-reporter/logs/vsphere_reporter.log`

Review these logs for detailed error information when troubleshooting.
     