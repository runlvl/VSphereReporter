# MSI-Installer-Erstellung für VMware vSphere Reporter

Diese Anleitung erklärt, wie das MSI-Installationspaket für Windows erstellt wird.

## Voraussetzungen auf dem Build-System

Für die Erstellung des MSI-Installers benötigen Sie:

1. Windows 7/8/10/11 (64-Bit)
2. Python 3.8 oder höher (temporär für die Paketerstellung)
3. WiX Toolset (für MSI-Paket-Erstellung)

## Schnellstart-Anleitung

1. Entpacken Sie das Archiv `vsphere-reporter-windows-msi-installer-v10.zip` auf Ihrem Windows-System
2. Führen Sie die Datei `create_msi_installer.bat` aus
3. Folgen Sie den Anweisungen auf dem Bildschirm
4. Das fertige MSI-Installationspaket wird im Ordner `dist` erstellt

## Manuelle Installation der Voraussetzungen

Falls die automatische Installation nicht funktioniert, können Sie die Voraussetzungen manuell installieren:

### Python installieren:
1. Laden Sie Python von https://www.python.org/downloads/ herunter
2. Aktivieren Sie bei der Installation die Option "Add Python to PATH"
3. Installieren Sie die erforderlichen Pakete:
   ```
   pip install cx_Freeze setuptools wheel pywin32
   ```

### WiX Toolset installieren:
1. Laden Sie WiX Toolset von https://wixtoolset.org/releases/ herunter
2. Installieren Sie das Toolset
3. Fügen Sie den Installationspfad zu Ihrer PATH-Umgebungsvariable hinzu (normalerweise `C:\Program Files (x86)\WiX Toolset v3.11\bin`)

## Manuelle MSI-Erstellung

Sie können das MSI-Paket auch manuell erstellen:

1. Öffnen Sie eine Kommandozeile im entpackten Archivverzeichnis
2. Führen Sie folgenden Befehl aus:
   ```
   python windows_package_builder.py
   ```
3. Das MSI-Paket wird im Ordner `dist` erstellt

## Ausgabeoptionen

Der Erstellungsprozess kann verschiedene Ausgabeformate erzeugen:

1. **MSI-Installationspaket** (Standard, benötigt WiX Toolset):  
   `dist/VMwareVSphereReporter_Setup_1.0.0.msi`

2. **Portable Version** (wird immer erstellt):  
   `dist/VMware vSphere Reporter_Portable_1.0.0.zip`

## Erklärung der Dateien

- `windows_package_builder.py` - Hauptskript zur Erstellung des MSI-Pakets
- `create_msi_installer.bat` - Hilfsskript zur einfachen Ausführung
- `README-MSI-INSTALLER.md` - Dokumentation zum MSI-Installer
- Weitere Projektdateien für den VMware vSphere Reporter

## Nach der Erstellung

Nach erfolgreicher Erstellung können Sie:

1. Das MSI-Paket auf beliebigen Windows-Systemen installieren
2. Das MSI-Paket an Benutzer verteilen
3. Die temporäre Build-Umgebung entfernen

## Hinweise

- Die Erstellung erfordert eine Internetverbindung, um Python-Abhängigkeiten herunterzuladen
- Der Erstellungsprozess kann je nach Systemleistung einige Minuten dauern
- Das finale MSI-Paket ist ca. 50-100 MB groß
- Benutzer benötigen zum Installieren keine Python-Kenntnisse oder -Installation

Bei Fragen wenden Sie sich bitte an Ihren Bechtle-Ansprechpartner.