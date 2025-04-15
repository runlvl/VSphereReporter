# VMware vSphere Reporter v26.0 - Installationsanleitung

Diese Anleitung beschreibt die Installation und Einrichtung des VMware vSphere Reporters für Windows und Linux.

## Systemvoraussetzungen

### Windows
- Windows 10 oder neuer / Windows Server 2016 oder neuer
- Python 3.8 oder höher
- Internetverbindung für die Installation der Abhängigkeiten
- Zugriff auf einen VMware vSphere/ESXi-Server (vCenter empfohlen)

### Linux
- Aktuelle Linux-Distribution (Ubuntu 20.04+, Debian 10+, RHEL/CentOS 8+, OpenSUSE Tumbleweed)
- Python 3.8 oder höher
- PyQt5 (für die grafische Oberfläche)
- Internetverbindung für die Installation der Abhängigkeiten
- Zugriff auf einen VMware vSphere/ESXi-Server (vCenter empfohlen)

## Installation unter Windows

### Methode 1: Windows-Installer (empfohlen)
1. Laden Sie die neueste Version des Windows-Installers herunter: `vsphere-reporter-windows-installer-v26.0.exe`
2. Führen Sie den Installer aus und folgen Sie den Anweisungen auf dem Bildschirm
3. Nach Abschluss der Installation können Sie den VMware vSphere Reporter über das Startmenü oder Desktop-Verknüpfung starten

### Methode 2: ZIP-Paket
1. Laden Sie das ZIP-Paket `vsphere-reporter-windows-v26.0.zip` herunter
2. Entpacken Sie das ZIP-Paket an einen Ort Ihrer Wahl
3. Öffnen Sie eine Eingabeaufforderung und navigieren Sie zum entpackten Verzeichnis
4. Führen Sie `setup.bat` aus, um die erforderlichen Abhängigkeiten zu installieren
5. Starten Sie die Anwendung mit `run.bat`

## Installation unter Linux

### Methode 1: Installationsskript (empfohlen)
1. Laden Sie das Tarball `vsphere-reporter-linux-v26.0.tar.gz` herunter
2. Entpacken Sie das Archiv: `tar -xzf vsphere-reporter-linux-v26.0.tar.gz`
3. Navigieren Sie zum entpackten Verzeichnis: `cd vsphere-reporter-v26.0`
4. Führen Sie das Installationsskript aus: `./setup.sh`
5. Starten Sie die Anwendung: `python vsphere_reporter.py` (GUI) oder `python vsphere_reporter_cli.py --help` (CLI)

### Methode 2: Manuelle Installation
1. Laden Sie das Tarball `vsphere-reporter-linux-v26.0.tar.gz` herunter
2. Entpacken Sie das Archiv: `tar -xzf vsphere-reporter-linux-v26.0.tar.gz`
3. Navigieren Sie zum entpackten Verzeichnis: `cd vsphere-reporter-v26.0`
4. Installieren Sie die erforderlichen Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```
5. Starten Sie die Anwendung:
   - GUI-Modus: `python vsphere_reporter.py`
   - CLI-Modus: `python vsphere_reporter_cli.py --help`

## Problembehebung

### Häufige Probleme unter Windows
- **Fehler beim Starten**: Stellen Sie sicher, dass Python korrekt installiert ist und in der PATH-Umgebungsvariable vorhanden ist.
- **Abhängigkeitsfehler**: Führen Sie `setup.bat` erneut aus, um fehlende Abhängigkeiten zu installieren.
- **PyQt5-Fehler**: Führen Sie `pip install PyQt5` aus, um PyQt5 manuell zu installieren.

### Häufige Probleme unter Linux
- **GUI startet nicht**: Stellen Sie sicher, dass Sie die erforderlichen Qt-Abhängigkeiten installiert haben:
  - Ubuntu/Debian: `sudo apt-get install python3-pyqt5 python3-pyqt5.qtsvg`
  - RHEL/CentOS: `sudo dnf install python3-qt5`
  - OpenSUSE: `sudo zypper install python3-qt5`
- **Verbindungsprobleme mit vCenter**: Stellen Sie sicher, dass der vCenter-Server erreichbar ist und dass Ihre Benutzeranmeldedaten korrekt sind.

## Kontakt und Support

Bei Fragen oder Problemen mit dem VMware vSphere Reporter kontaktieren Sie bitte:
- E-Mail: support@bechtle.com
- Telefon: +49 123 456789