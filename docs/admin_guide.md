# VMware vSphere Reporter - Administrator Guide

## Overview

VMware vSphere Reporter is a comprehensive tool for generating detailed reports about VMware vSphere environments. This guide provides instructions for installing and configuring the tool on Windows servers.

## System Requirements

### Hardware Requirements
- Processor: 2 GHz dual-core processor or higher
- Memory: 4 GB RAM minimum (8 GB recommended)
- Disk Space: 500 MB for application and dependencies
- Display: 1280x720 resolution or higher

### Software Requirements
- Operating System: Windows Server 2016/2019/2022 or Windows 10/11
- Python 3.8 or higher
- Internet connection (for initial package installation)
- Network connectivity to vCenter Server

### vSphere Environment Requirements
- vCenter Server 6.5, 6.7, 7.0, or 8.0
- User account with read permissions to the vSphere environment

## Installation

### Installation Steps

1. **Install Python (if not already installed)**:
   - Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/windows/)
   - During installation, make sure to check "Add Python to PATH"
   - Verify installation by opening Command Prompt and running:
     ```
     python --version
     