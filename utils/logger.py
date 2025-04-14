#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logging configuration module
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Singleton logger instance
_logger = None
_console_handler = None

def setup_logger(log_level=logging.INFO):
    """
    Setup application logging
    
    This sets up logging to:
    1. Console (configurable level)
    2. Log file (DEBUG level)
    
    Args:
        log_level (int): Logging level for console output
    """
    global _logger, _console_handler
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Log file path
    log_file = os.path.join(log_dir, 'vsphere_reporter.log')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create file handler (with rotation)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Create console handler
    _console_handler = logging.StreamHandler(sys.stdout)
    _console_handler.setLevel(log_level)
    _console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(_console_handler)
    
    # Store reference to logger
    _logger = logger
    
    return logger

def set_log_level(level):
    """
    Update the console log level
    
    Args:
        level (int): New logging level
    """
    global _console_handler
    
    if _console_handler:
        _console_handler.setLevel(level)
        
    # Also update all StreamHandlers to the same level
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and handler is not _console_handler:
            handler.setLevel(level)
            
def get_log_level_name(level):
    """
    Get the string name of a log level
    
    Args:
        level (int): Logging level
        
    Returns:
        str: Level name
    """
    if level == logging.DEBUG:
        return "DEBUG"
    elif level == logging.INFO:
        return "INFO"
    elif level == logging.WARNING:
        return "WARNING"
    elif level == logging.ERROR:
        return "ERROR"
    elif level == logging.CRITICAL:
        return "CRITICAL"
    else:
        return "UNKNOWN"
        
def get_log_level_from_name(name):
    """
    Get log level from string name
    
    Args:
        name (str): Level name
        
    Returns:
        int: Logging level
    """
    name = name.upper()
    if name == "DEBUG":
        return logging.DEBUG
    elif name == "INFO":
        return logging.INFO
    elif name == "WARNING":
        return logging.WARNING
    elif name == "ERROR":
        return logging.ERROR
    elif name == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO
