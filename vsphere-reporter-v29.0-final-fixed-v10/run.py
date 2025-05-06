#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter v29.0
Main Entry Point

Final Fixed Version 10 - Simplified Structure
Copyright (c) 2025 Bechtle GmbH
"""

import os
import sys
import logging
import socket
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_available_port(start_port=5000, max_attempts=100):
    """Find an available port starting from start_port"""
    logger.info("Suche nach verfügbarem Port...")
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                logger.info(f"Verfügbarer Port gefunden: {port}")
                return port
    logger.warning(f"Kein freier Port gefunden, verwende Standard-Port {start_port}")
    return start_port  # Fallback to start_port if no port is available

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description='VMware vSphere Reporter')
    parser.add_argument('--port', type=int, help='Port für den Webserver')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Hostadresse für den Webserver')
    parser.add_argument('--debug', action='store_true', help='Debug-Modus aktivieren')
    args = parser.parse_args()
    
    # Set debugging variable
    os.environ['VSPHERE_REPORTER_DEBUG'] = '1' if args.debug else '0'
    
    # Determine port
    port = args.port if args.port else get_available_port()
    
    # Set environment variable for Flask
    os.environ['PORT'] = str(port)
    os.environ['HOST'] = args.host
    
    logger.info(f"Starte vSphere Reporter auf Port {port}...")
    
    try:
        # Import here to avoid circular imports
        from app import app
        app.run(host=args.host, port=port, debug=args.debug)
    except ImportError as e:
        logger.error(f"Fehler beim Importieren der Anwendung: {str(e)}")
        logger.error("Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    logger.info("Starte vSphere Reporter...")
    main()