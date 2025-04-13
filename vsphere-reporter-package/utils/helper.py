#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper utilities for vSphere Reporter
"""

import os
import sys
import platform
import logging
from PyQt5.QtWidgets import QFileDialog, QMessageBox

logger = logging.getLogger(__name__)

def get_save_directory(parent=None):
    """
    Show a directory selection dialog to get the save location
    
    Args:
        parent: Parent widget for the dialog
        
    Returns:
        str: Selected directory or None if canceled
    """
    try:
        # Get the default documents directory
        default_dir = get_documents_directory()
        
        # Show directory selection dialog
        directory = QFileDialog.getExistingDirectory(
            parent,
            "Select Directory to Save Report",
            default_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        # Check if directory was selected
        if directory:
            # Validate write permissions
            if not os.access(directory, os.W_OK):
                QMessageBox.warning(
                    parent,
                    "Directory Not Writable",
                    f"You do not have write permissions for the selected directory:\n{directory}\n\nPlease select another directory."
                )
                return get_save_directory(parent)
            
            return directory
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting save directory: {str(e)}")
        QMessageBox.critical(
            parent,
            "Error",
            f"An error occurred while selecting the save directory:\n{str(e)}"
        )
        return None

def get_documents_directory():
    """
    Get the user's documents directory based on platform
    
    Returns:
        str: Path to the documents directory
    """
    try:
        # Windows
        if platform.system() == 'Windows':
            import winreg
            shell_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            )
            documents_dir = winreg.QueryValueEx(shell_key, 'Personal')[0]
            return documents_dir
            
        # macOS
        elif platform.system() == 'Darwin':
            return os.path.join(os.path.expanduser('~'), 'Documents')
            
        # Linux and others
        else:
            return os.path.expanduser('~')
            
    except Exception as e:
        logger.error(f"Error getting documents directory: {str(e)}")
        return os.path.expanduser('~')

def human_readable_size(size_bytes):
    """
    Convert bytes to human-readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Human-readable size string
    """
    if size_bytes == 0:
        return "0 B"
        
    size_names = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
        
    return f"{size_bytes:.2f} {size_names[i]}"

def get_application_path():
    """
    Get the application base path
    
    Returns:
        str: Application base path
    """
    if getattr(sys, 'frozen', False):
        # Running as executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
