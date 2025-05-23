# VMware vSphere Reporter - User Guide

## Introduction

VMware vSphere Reporter is a comprehensive tool for generating detailed reports about VMware vSphere environments. This guide explains how to use the application to connect to vCenter servers and generate reports with various options.

## Getting Started

### Launching the Application

#### Windows
1. Double-click on the application shortcut or run `vsphere_reporter.py` from the application directory
2. The main application window will open, showing the VMware vSphere Reporter interface

#### Linux GUI Version
1. Open a terminal and navigate to the application directory
2. Run `python3 vsphere_reporter_linux.py`
3. The Tkinter-based GUI will open, showing the VMware vSphere Reporter interface

#### Linux Command Line Version
1. Open a terminal and navigate to the application directory
2. Run `python3 vsphere_reporter_cli.py --help` to see available options
3. Use command-line parameters to specify connection details and report options

### Application Interface

#### Windows and Linux GUI
The main application window consists of the following sections:

- **Connection Status**: Shows if you're connected to a vCenter server
- **Report Options**: Checkboxes to select what to include in the report
- **Export Options**: Controls for selecting report format and generating the report

## Connecting to vCenter

### Establishing a Connection

1. Click the "Connect to vCenter" button in the top-right corner
2. In the connection dialog, enter the following information:
   - **vCenter Server**: The hostname or IP address of your vCenter server (e.g., `vcenter.example.com`)
   - **Username**: Your vCenter username (e.g., `administrator@vsphere.local`)
   - **Password**: Your vCenter password
   - **Ignore SSL certificate verification**: Check this box if your vCenter uses a self-signed certificate

3. Click "Connect" to establish the connection
4. If successful, the connection status will change to show you're connected

### Connection Troubleshooting

If you cannot connect to vCenter:

- Verify the server address is correct
- Check your username and password
- Ensure the vCenter server is accessible from your network
- If using a self-signed certificate, make sure "Ignore SSL certificate verification" is checked
- Consult your vSphere administrator if problems persist

## Selecting Report Options

### Required Report Options

The following report options are always included and cannot be deselected:

- **VMware Tools Versions**: Lists all VMs ordered by VMware Tools version (oldest first)
- **Snapshot Age**: Lists all VM snapshots ordered by age (oldest first)
- **Orphaned VMDK Files**: Lists potentially orphaned VMDK files with explanations

### Additional Report Options

Select any of the following additional options to include in your report:

- **Virtual Machines**: Includes detailed VM information
- **ESXi Hosts**: Includes host information
- **Datastores**: Includes datastore capacity and usage
- **Clusters**: Includes cluster configuration and capacity
- **Resource Pools**: Includes resource pool allocation settings
- **Networks**: Includes network configuration information

## Generating Reports

### Export Format Selection

Select one of the following export formats:

- **HTML**: Creates a web page report that can be viewed in any browser
- **DOCX**: Creates a Microsoft Word document
- **PDF**: Creates a PDF document
- **All Formats**: Generates the report in all three formats

### Generate the Report

1. Select the desired report options
2. Choose your preferred export format
3. Click "Generate Report"
4. In the directory selection dialog, choose where to save the report
5. Wait for the report generation to complete
6. A message will appear showing the location of the generated files

### Report Generation Progress

During report generation:

- A progress dialog shows the current status
- The first phase collects data from vCenter
- The second phase creates the actual report file(s)
- Larger environments may take longer to process

## Understanding the Reports

### Report Sections

Each report contains the following sections:

1. **Executive Summary**: Overview of the environment with key statistics
2. **VMware Tools Versions**: VMs with details about their VMware Tools version
3. **VM Snapshots**: List of all snapshots with age information
4. **Orphaned VMDK Files**: Potential orphaned disk files with explanations
5. **Additional sections**: Based on your selected options

### Recommendations

The report includes recommendations for potential issues, such as:

- Outdated VMware Tools that need upgrading
- Snapshots older than 7 days that should be removed
- Orphaned VMDKs that can be deleted to reclaim space
- Datastores with usage above 85%

### Report Navigation

- **HTML reports**: Use the table of contents at the top to navigate
- **DOCX reports**: Use the document's table of contents
- **PDF reports**: Use bookmarks or the table of contents

## Tips for Effective Reporting

### Best Practices

1. **Run reports during off-peak hours** to minimize impact on vCenter Server
2. **Be selective with options** for large environments to improve performance
3. **Review the recommendations** section for important action items
4. **Save reports regularly** to track changes over time

### Scheduling Regular Reports

For regular health checks, consider:

1. Creating a scheduled task to run the report automatically
2. Running weekly reports to track VM sprawl and resource usage
3. Keeping historical reports to track growth and trends

## Command Line Usage

The application can also be run from the command line for automated reporting. This is especially useful on Linux systems where you might want to schedule regular reports.

### Command Line Syntax

```
python3 vsphere_reporter_cli.py --server <vcenter_address> --username <username> [--password <password>] [options]
```

### Required Parameters

- `--server` or `-s`: vCenter server address
- `--username` or `-u`: vCenter username

### Optional Parameters

- `--password` or `-p`: vCenter password (omit for secure prompt)
- `--ignore-ssl` or `-k`: Ignore SSL certificate validation
- `--output-dir` or `-o`: Output directory for reports (default: current directory)
- `--format` or `-f`: Report format (html, docx, pdf, or all)
- `--include-all` or `-a`: Include all optional sections in the report

### Report Section Flags

- `--vms`: Include virtual machines section
- `--hosts`: Include hosts section
- `--datastores`: Include datastores section
- `--clusters`: Include clusters section
- `--resource-pools`: Include resource pools section
- `--networks`: Include networks section

### Example Commands

Generate a complete report in all formats:
```
python3 vsphere_reporter_cli.py --server vcenter.example.com --username admin@vsphere.local --include-all --format all
```

Generate a minimal report with only required sections in HTML format:
```
python3 vsphere_reporter_cli.py --server vcenter.example.com --username admin@vsphere.local --format html
```

Generate a custom report with specific sections in PDF format:
```
python3 vsphere_reporter_cli.py --server vcenter.example.com --username admin@vsphere.local --vms --hosts --datastores --format pdf
```

### Using in Scripts

When using the CLI version in scripts, you can provide the password in a secure way by using environment variables or a secure prompt:

```bash
#!/bin/bash
# Example script to generate weekly reports

# Get password securely
read -s -p "Enter vCenter password: " VC_PASS
echo

# Run report
python3 vsphere_reporter_cli.py --server vcenter.example.com --username admin@vsphere.local --password "$VC_PASS" --include-all --format all --output-dir /path/to/reports/$(date +%Y-%m-%d)
```

