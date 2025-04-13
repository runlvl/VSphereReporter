#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for VMware vSphere Reporter
"""

from setuptools import setup, find_packages

setup(
    name="vsphere-reporter",
    version="1.0.0",
    description="VMware vSphere Environment Reporting Tool",
    author="Administrator",
    packages=find_packages(),
    install_requires=[
        "pyVmomi>=7.0.0",
        "PyQt5>=5.15.0",
        "reportlab>=3.6.0",
        "python-docx>=0.8.11",
        "jinja2>=3.0.0",
        "humanize>=3.0.0",
        "cx_Freeze>=6.10.0"
    ],
    entry_points={
        "console_scripts": [
            "vsphere-reporter=vsphere_reporter:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: System Administrators",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
)
