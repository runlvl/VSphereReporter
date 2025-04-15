# VMware vSphere Reporter v25.2 - Installationsanleitung

## Windows-Installation

1. Laden Sie das Windows-Paket herunter: `vsphere-reporter-windows-v25.2.zip`
2. Entpacken Sie die ZIP-Datei in einen Ordner Ihrer Wahl
3. Starten Sie die Anwendung mit:
   - Doppelklick auf `run.bat`
   - Für den Debug-Modus: Ausführen von `run.bat --debug` in der Eingabeaufforderung

### Erforderliche Komponenten für Windows

- Python 3.8 oder höher (Download: [python.org](https://www.python.org/downloads/))
- Die erforderlichen Python-Bibliotheken werden beim ersten Start automatisch installiert

## Linux-Installation (OpenSuse Tumbleweed)

1. Laden Sie das Linux-Paket herunter: `vsphere-reporter-linux-v25.2.tar.gz`
2. Entpacken Sie die TAR-Datei mit dem Befehl:
   ```
   tar -xzf vsphere-reporter-linux-v25.2.tar.gz
   ```
3. Navigieren Sie in das entpackte Verzeichnis:
   ```
   cd vsphere-reporter-linux-v25.2
   ```
4. Starten Sie die Anwendung mit:
   ```
   ./run.sh
   ```
   Für den Debug-Modus:
   ```
   ./run.sh --debug
   ```

### Erforderliche Komponenten für Linux (OpenSuse Tumbleweed)

- Python 3.8 oder höher:
  ```
  sudo zypper install python3 python3-pip
  ```
  
- Qt-Abhängigkeiten (für die GUI):
  ```
  sudo zypper install libqt5-qtbase libqt5-qtsvg python3-qt5
  ```
  
- Die Python-Bibliotheken werden beim ersten Start automatisch installiert

## Hinweise zur ersten Verwendung

1. Beim ersten Start müssen Sie sich mit Ihrem vCenter verbinden:
   - Geben Sie die vCenter-IP oder den Hostnamen ein
   - Geben Sie Ihren Benutzernamen und Ihr Passwort ein
   - Falls erforderlich, aktivieren Sie die Option, unsichere SSL-Verbindungen zuzulassen

2. Wählen Sie die gewünschten Berichtsoptionen aus:
   - VMware Tools (sortiert nach ältester Version)
   - Snapshots (sortiert nach Alter, älteste zuerst)
   - Verwaiste VMDK-Dateien

3. Wählen Sie das gewünschte Exportformat (HTML, DOCX oder PDF)

4. Klicken Sie auf "Bericht generieren"

## Problembehandlung

Bei Fehlern prüfen Sie bitte:

1. Die Log-Dateien im Verzeichnis `logs/`
2. Starten Sie die Anwendung im Debug-Modus
3. Stellen Sie sicher, dass Ihr Benutzer ausreichende Berechtigungen im vCenter hat

## Update von früheren Versionen

Die Version 25.2 bietet eine vollständig überarbeitete VMDK-Erkennung mit verbesserter Zuverlässigkeit. Wir empfehlen, alte Versionen vollständig zu deinstallieren, bevor Sie diese Version installieren.