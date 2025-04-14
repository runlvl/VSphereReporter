#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bechtle logo as a string to be used in Tkinter applications.
This contains a SVG representation of the Bechtle logo that can be
converted to a Tkinter-compatible PhotoImage.
"""

# SVG representation of the Bechtle logo (can be used with tksvg library)
BECHTLE_LOGO_SVG = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 40">
    <path fill="#00355e" d="M31.5,10.2h-6.8c-4.5,0-6.9,2.5-6.9,7v5.6c0,4.5,2.4,7,6.9,7h6.8c4.5,0,6.9-2.5,6.9-7v-5.6 C38.4,12.7,36,10.2,31.5,10.2z M32.4,23.2c0,1.5-0.8,2.3-2.2,2.3h-4.3c-1.5,0-2.2-0.8-2.2-2.3v-6.4c0-1.5,0.8-2.3,2.2-2.3h4.3 c1.5,0,2.2,0.8,2.2,2.3V23.2z"/>
    <path fill="#00355e" d="M52.7,10.2h-6.8c-4.5,0-6.9,2.5-6.9,7v5.6c0,4.5,2.4,7,6.9,7h6.8c4.5,0,6.9-2.5,6.9-7v-5.6 C59.6,12.7,57.2,10.2,52.7,10.2z M53.6,23.2c0,1.5-0.8,2.3-2.2,2.3h-4.3c-1.5,0-2.2-0.8-2.2-2.3v-6.4c0-1.5,0.8-2.3,2.2-2.3h4.3 c1.5,0,2.2,0.8,2.2,2.3V23.2z"/>
    <path fill="#00355e" d="M84.2,15v-4.8h-5.8v4.8h-1.1v-4.8h-5.8v4.8h-1.1v-4.8h-5.8v14.6c0,4.5,2.4,7,6.9,7h6.8 c4.5,0,6.9-2.5,6.9-7V15H84.2z M78.3,23.2c0,1.5-0.8,2.3-2.2,2.3h-4.3c-1.5,0-2.2-0.8-2.2-2.3v-6.4c0-1.5,0.8-2.3,2.2-2.3h4.3 c1.5,0,2.2,0.8,2.2,2.3V23.2z"/>
    <path fill="#00355e" d="M105.4,10.2h-6.8c-4.5,0-6.9,2.5-6.9,7v7.6h5.8v-8.4c0-1.5,0.8-2.3,2.2-2.3h4.3c1.5,0,2.2,0.8,2.2,2.3 v8.4h5.8v-7.6C112.3,12.7,109.9,10.2,105.4,10.2z"/>
    <path fill="#00355e" d="M120.9,10.2h-5.8v19.6h13.7v-3.8h-7.9V10.2z"/>
    <path fill="#00355e" d="M147.2,14.5h-13.7v3.8h7.9v11.5h5.8V14.5z"/>
    <path fill="#00355e" d="M151.3,10.2v19.6h13.7v-3.8h-7.9V10.2H151.3z"/>
    <path fill="#00355e" d="M184.7,10.2h-13.7v19.6h13.7v-3.8H177v-4.3h7.7v-3.8H177v-3.8h7.7V10.2z"/>
    <path fill="#da6f1e" d="M18.4,10.2h-18v19.6h5.8v-8.4h12.2v-3.8H6.3v-3.8h12.2V10.2z"/>
</svg>'''

# Base64 encoded PNG version of the Bechtle logo (for Tkinter PhotoImage)
BECHTLE_LOGO_PNG = '''
iVBORw0KGgoAAAANSUhEUgAAAMgAAAAoCAYAAAC7HLUcAAAACXBIWXMAAAsTAAALEwEAmpwYAAAG
ymlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0w
TXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRh
LyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNy4xLWMwMDAgNzkuZGFiYWNiYiwgMjAyMS8wNC8x
NC0wMDozOTo0NCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9y
Zy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9
IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczpkYz0iaHR0
cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25z
LmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5j
b20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAv
c1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDIz
LjAgKE1hY2ludG9zaCkiIHhtcDpDcmVhdGVEYXRlPSIyMDIzLTA5LTIwVDE1OjM2OjEwKzAyOjAw
IiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMy0wOS0yMFQxNTo0MDo1OSswMjowMCIgeG1wOk1ldGFkYXRh
RGF0ZT0iMjAyMy0wOS0yMFQxNTo0MDo1OSswMjowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBo
b3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2
LTIuMSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo4ZGFiY2UxNS0wNTNmLTQ5YWMtYTM1Yi02
ZmZmODUzYjJkZTAiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDpiZmNk
M2MxYS0wZjU4LTg3NDAtODczMS1lNjg3NWJhOGNkMDIiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJ
RD0ieG1wLmRpZDoxMmMzYmEwMS01NTVlLTQ2MTQtYTM1ZS05MzljYTVlYWRiMjMiPiA8eG1wTU06
SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDpp
bnN0YW5jZUlEPSJ4bXAuaWlkOjEyYzNiYTAxLTU1NWUtNDYxNC1hMzVlLTkzOWNhNWVhZGIyMyIg
c3RFdnQ6d2hlbj0iMjAyMy0wOS0yMFQxNTozNjoxMCswMjowMCIgc3RFdnQ6c29mdHdhcmVBZ2Vu
dD0iQWRvYmUgUGhvdG9zaG9wIDIzLjAgKE1hY2ludG9zaCkiLz4gPHJkZjpsaSBzdEV2dDphY3Rp
b249InNhdmVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjFkM2RkZmExLWVlNWEtNGU2YS05
NDZmLWNmZDg0ODI0YmJkZiIgc3RFdnQ6d2hlbj0iMjAyMy0wOS0yMFQxNTo0MDo1OSswMjowMCIg
c3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIDIzLjAgKE1hY2ludG9zaCkiIHN0
RXZ0OmNoYW5nZWQ9Ii8iLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249InNhdmVkIiBzdEV2dDppbnN0
YW5jZUlEPSJ4bXAuaWlkOjhkYWJjZTE1LTA1M2YtNDlhYy1hMzViLTZmZmY4NTNiMmRlMCIgc3RF
dnQ6d2hlbj0iMjAyMy0wOS0yMFQxNTo0MDo1OSswMjowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0i
QWRvYmUgUGhvdG9zaG9wIDIzLjAgKE1hY2ludG9zaCkiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9y
ZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwv
eDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+1gFtYwAABuhJREFUeJztnV9y4zYMxr+ZvW/S
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
'''

def get_bechtle_logo_for_tkinter(root):
    """
    Get a Tkinter PhotoImage of the Bechtle logo that can be displayed
    in a Tkinter application.
    
    Args:
        root: Tkinter root or Toplevel where the image will be used
        
    Returns:
        PhotoImage: A Tkinter PhotoImage containing the Bechtle logo
    """
    import base64
    try:
        from PIL import Image, ImageTk
        import io
        
        # Use PIL/Pillow for better image handling
        image_data = base64.b64decode(BECHTLE_LOGO_PNG)
        image = Image.open(io.BytesIO(image_data))
        return ImageTk.PhotoImage(image)
    except ImportError:
        # Fallback to Tkinter's PhotoImage (limited format support)
        import tkinter as tk
        return tk.PhotoImage(data=BECHTLE_LOGO_PNG)