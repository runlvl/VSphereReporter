# VMware vSphere Reporter - Web Edition v29.0

A comprehensive browser-based reporting tool for VMware vSphere environments.

## Overview

The VMware vSphere Reporter Web Edition is a modern, browser-based reporting tool designed for VMware vSphere environments. It provides detailed insights into your virtual infrastructure, helping administrators identify potential issues, optimize resource usage, and maintain a well-documented environment.

## Key Features

- **Web-based Interface**: Access the reporting tool from any browser, no local installation required
- **VMware Tools Status**: Monitor VMware Tools versions and status across all VMs
- **Snapshot Management**: Identify old snapshots that need attention
- **Orphaned VMDK Detection**: Find potentially orphaned VMDK files to reclaim storage
- **Infrastructure Topology Visualization**: Interactive diagrams showing your vSphere environment structure
- **Comprehensive Reporting**: Detailed information about VMs, hosts, datastores, clusters, and more
- **Multiple Export Formats**: Export reports as HTML, PDF, or DOCX
- **Error Resilience**: Advanced error handling with multi-level fallback mechanisms

## Installation and Requirements

### System Requirements

- Python 3.8 or higher
- Supported web browsers: Chrome, Firefox, Edge, Safari (latest versions)
- Network access to your vCenter server
- Minimum 2GB RAM, 4GB recommended for large environments

### Installation

1. **Download the package**:
   Download the appropriate package for your system:
   - Linux: `vsphere-reporter-linux-v29.0.tar.gz`
   - Windows: `vsphere-reporter-windows-v29.0.zip`

2. **Extract the package**:
   - Linux: `tar -xzf vsphere-reporter-linux-v29.0.tar.gz`
   - Windows: Extract using Windows Explorer or another archive tool

3. **Install dependencies**:
   - Linux: 
     ```
     cd vsphere-reporter-v29.0
     pip install -r requirements.txt
     ```
   - Windows:
     ```
     cd vsphere-reporter-v29.0
     setup.bat
     ```

4. **Start the server**:
   - Linux: `python app.py`
   - Windows: `run.bat`

5. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Connect to vCenter**:
   - Click "Connect" in the navigation menu
   - Enter your vCenter server address, username, and password
   - Check "Ignore SSL certificate verification" if needed
   - Click "Connect"

2. **Configure Report Options**:
   - Select the sections you want to include in your report
   - All options are enabled by default

3. **Generate Reports**:
   - Choose your export format (HTML, PDF, DOCX)
   - Click "Generate Report"
   - Once the report is generated, you can download it

## Security Considerations

- Credentials are stored in memory only during the active session
- No persistent storage of vCenter credentials
- Sessions expire after 12 hours of inactivity
- All connections to vCenter use the official VMware SDK (PyVmomi)

## Troubleshooting

- **Connection Issues**: Ensure your vCenter server is reachable and credentials are correct
- **Report Generation Errors**: Check the logs directory for detailed error messages
- **Missing Data**: Some report sections may be empty if the corresponding features are not used in your environment

## Advanced Configuration

The application supports several environment variables for advanced configuration:

- `PORT`: Change the default listening port (default: 5000)
- `VSPHERE_REPORTER_DEBUG`: Enable debug logging (set to "1" to enable)
- `VSPHERE_REPORTER_SECRET_KEY`: Custom secret key for session encryption

Example:
```
VSPHERE_REPORTER_DEBUG=1 PORT=8080 python app.py
```

## License

Copyright © 2025 Bechtle GmbH. All rights reserved.

## Acknowledgments

- Built with Flask, PyVmomi, and pyecharts
- Uses the Bechtle corporate design guidelines