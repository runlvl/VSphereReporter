#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bechtle logo module for Tkinter applications.
This provides functions to load the Bechtle logo from file
and convert it to a Tkinter-compatible PhotoImage.
"""

import os
import logging

def get_bechtle_logo_for_tkinter(root):
    """
    Get a Tkinter PhotoImage of the Bechtle logo that can be displayed
    in a Tkinter application. Tries to load the logo from a file in the
    images directory.
    
    Args:
        root: Tkinter root or Toplevel where the image will be used
        
    Returns:
        PhotoImage: A Tkinter PhotoImage containing the Bechtle logo
    """
    # Try to load from file first - this is more reliable
    logo_path = 'images/logo_bechtle.png'
    
    if os.path.exists(logo_path):
        try:
            # First try using PIL for better image handling
            try:
                from PIL import Image, ImageTk
                image = Image.open(logo_path)
                return ImageTk.PhotoImage(image)
            except ImportError:
                # Fallback to Tkinter's PhotoImage
                import tkinter as tk
                return tk.PhotoImage(file=logo_path)
        except Exception as e:
            logging.warning(f"Error loading logo from file: {str(e)}")
    else:
        logging.warning(f"Logo file not found at {logo_path}")
    
    # If we couldn't load from file, show a text label instead
    logging.warning("Using text label as logo fallback")
    return None