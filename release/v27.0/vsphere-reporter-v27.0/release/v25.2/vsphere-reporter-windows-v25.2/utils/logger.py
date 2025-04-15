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

def get_logger(name=None):
    """
    Get the application logger
    
    Args:
        name (str, optional): Logger name. Defaults to None (root logger).
    
    Returns:
        logging.Logger: The application logger. If setup_logger hasn't been called,
                        it will be called with default settings.
    """
    global _logger
    if _logger is None:
        _logger = setup_logger()
    
    if name is None:
        return _logger
    else:
        # Gibt einen namensbasierten Logger zurück, der die Konfiguration des Root-Loggers verwendet
        return logging.getLogger(name)

def setup_logger(log_level=None):
    """
    Setup application logging
    
    This sets up logging to:
    1. Console (configurable level)
    2. Log file (DEBUG level)
    
    Args:
        log_level (int, optional): Logging level for console output. 
                                   If None, it will check for VSPHERE_REPORTER_DEBUG environment variable
                                   and use DEBUG level if set to '1', otherwise INFO level.
                                   
    Returns:
        logging.Logger: Configured logger instance
    """
    global _logger, _console_handler
    
    # Umfassende Fehlerbehandlung, um Abstürze zu vermeiden
    try:
        # Check for debug mode in environment variables if log_level is not specified
        if log_level is None:
            debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
            log_level = logging.DEBUG if debug_mode else logging.INFO
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception as e:
                # Fallback: Verwende temporäres Verzeichnis, wenn logs-Verzeichnis nicht erstellt werden kann
                import tempfile
                log_dir = tempfile.gettempdir()
                print(f"Warning: Could not create logs directory, using temp directory: {log_dir}")
        
        # Generate a unique log file name with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f'vsphere_reporter_{timestamp}.log')
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Root logger always at DEBUG to catch everything
        
        # Clear any existing handlers to avoid duplicates
        if logger.handlers:
            logger.handlers = []
        
        # Create formatters with Fehlerbehandlung für Malformatted Strings
        try:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s'
            )
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
        except Exception as e:
            # Einfachere Formatter als Fallback verwenden
            file_formatter = logging.Formatter('%(levelname)s - %(message)s')
            console_formatter = logging.Formatter('%(levelname)s - %(message)s')
            print(f"Warning: Using simplified log formatters due to error: {str(e)}")
        
        # Create file handler (with rotation)
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)  # File handler always at DEBUG
            file_handler.setFormatter(file_formatter)
            
            # Add file handler to logger
            logger.addHandler(file_handler)
        except Exception as e:
            # Protokollierung in Datei nicht möglich, nur Konsolenausgabe verwenden
            print(f"Warning: Could not create log file ({log_file}), using console only: {str(e)}")
        
        # Create console handler
        try:
            _console_handler = logging.StreamHandler(sys.stdout)
            _console_handler.setLevel(log_level)
            _console_handler.setFormatter(console_formatter)
            
            # Add handler to logger
            logger.addHandler(_console_handler)
        except Exception as e:
            # Notfall-Handler für Konsole
            _console_handler = logging.StreamHandler()
            _console_handler.setLevel(logging.WARNING)
            logger.addHandler(_console_handler)
            print(f"Warning: Using simplified console handler: {str(e)}")
        
        # Store reference to logger
        _logger = logger
        
        # Log startup information
        debug_mode = log_level == logging.DEBUG
        
        # Set debug mode environment variable for other modules to use
        if debug_mode:
            os.environ['VSPHERE_REPORTER_DEBUG'] = '1'
            try:
                logger.info("Debug mode enabled. Detailed logs will be saved to: %s", log_file)
                
                # Log Python version and platform info for debugging
                import platform
                logger.debug("Python version: %s", sys.version)
                logger.debug("Platform: %s", platform.platform())
                
                # Enable debug test data
                logger.debug("Test data will be used if no real data is available")
            except Exception as e:
                print(f"Warning: Error during debug logging: {str(e)}")
        else:
            try:
                logger.info("Application started. Log file: %s", log_file)
            except Exception as e:
                print(f"Warning: Error during startup logging: {str(e)}")
        
        return logger
        
    except Exception as e:
        # Absolute Notfall-Fallback, wenn alles andere fehlschlägt
        print(f"CRITICAL: Failed to set up logging system: {str(e)}")
        
        # Create a minimal logger that only prints to console
        minimal_logger = logging.getLogger()
        minimal_logger.setLevel(logging.WARNING)
        
        # Ensure there is at least one handler
        if not minimal_logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.WARNING)
            minimal_logger.addHandler(handler)
        
        # Store reference
        _logger = minimal_logger
        
        return minimal_logger

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
