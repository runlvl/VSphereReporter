# VMware vSphere Reporter - Grafischer Installer

## Übersicht

Das Paket enthält einen grafischen Installer für den VMware vSphere Reporter im Bechtle-Design. Der Installer bietet folgende Funktionen:

- Vollständig grafische Benutzeroberfläche im Bechtle Corporate Design
- Automatische Python-Erkennung und Validierung
- Auswahl des Installationsverzeichnisses
- Automatische Installation aller Abhängigkeiten
- Erstellung von Desktop-Verknüpfungen und Startmenü-Einträgen
- Fortschrittsanzeige und detailliertes Installationsprotokoll

## Verwendung

### Option 1: Direktes Ausführen des GUI-Installers

1. Extrahieren Sie das ZIP-Archiv in einen beliebigen Ordner
2. Führen Sie `installer_gui.py` mit Python aus:
   ```
   python installer_gui.py
   ```
3. Folgen Sie den Anweisungen im Installationsassistenten

### Option 2: Erstellung eines ausführbaren Installers (Windows)

Für eine noch benutzerfreundlichere Installation kann ein eigenständiger EXE-Installer erstellt werden:

1. Installieren Sie cx_Freeze und pywin32 (optional für Windows-Verknüpfungen):
   ```
   pip install cx_Freeze pywin32
   ```

2. Führen Sie den Installer-Builder aus:
   ```
   python installer_builder.py
   ```

3. Der Builder erstellt je nach Verfügbarkeit von NSIS entweder:
   - Eine eigenständige `.exe`-Datei (mit NSIS)
   - Ein ZIP-Paket mit dem ausführbaren Installer (ohne NSIS)

4. Die erstellten Dateien befinden sich im Unterordner `build`

## Besonderheiten des Installers

### Python-Erkennung

Der Installer erkennt automatisch verschiedene Python-Installationen:
- Standard PATH-Einträge (python, python3)
- Windows Python-Launcher (py)
- Standard-Installationspfade unter Windows
- AppData-Installationen
- Windows Store Python

### Abhängigkeiten

Folgende Abhängigkeiten werden automatisch installiert:
- pyVmomi (VMware vSphere API)
- PyQt5 (GUI)
- reportlab (PDF-Erzeugung)
- python-docx (DOCX-Erzeugung)
- jinja2 (HTML-Templates)
- humanize (lesbare Dateigrößen)
- six und requests (Hilfsmodule)

### Systemvoraussetzungen

- Python 3.8 oder höher
- Pip (wird für die Installation der Abhängigkeiten verwendet)
- Windows 7/8/10/11 oder Linux (getestet auf OpenSuse Tumbleweed)

## Fehlerbehandlung

Der Installer bietet umfangreiche Protokollierung und Fehlerbehandlung:

- Detailliertes Installationsprotokoll im Assistenten
- Überprüfung der Python-Version
- Validierung des Installationspfads
- Prüfung des verfügbaren Speicherplatzes
- Möglichkeit zum Abbrechen der Installation

## Anpassung

Der Installer verwendet das Bechtle-Farbschema und -Logo:
- Dunkelblau: #00355e
- Orange: #da6f1e
- Grün: #23a96a
- Hellgrau: #f3f3f3
- Dunkelgrau: #5a5a5a

Das Logo wird automatisch aus dem `images`- oder `attached_assets`-Verzeichnis geladen.

© 2025 Bechtle GmbH