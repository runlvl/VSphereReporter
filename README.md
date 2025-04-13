# VMware vSphere Reporter

Ein umfassendes Tool zur Berichterstellung für VMware vSphere-Umgebungen.

## Überblick

VMware vSphere Reporter ist ein leistungsstarkes Tool zur Generierung detaillierter Berichte über VMware vSphere-Umgebungen. Es bietet sowohl eine grafische Benutzeroberfläche (GUI) als auch eine Kommandozeilenschnittstelle (CLI) für maximale Flexibilität.

## Funktionen

- Verbindung zu vCenter-Servern über API
- Erfassung detaillierter Informationen zu Ihrer vSphere-Umgebung
- Berichterstellung mit anpassbaren Optionen
- Berichte in mehreren Formaten (HTML, DOCX, PDF)
- Plattformübergreifende Unterstützung (Windows und Linux)

## Systemanforderungen

### Windows
- Windows 10/11 oder Windows Server 2016/2019/2022
- Python 3.8 oder höher
- PyQt5 für die GUI-Version

### Linux (inkl. OpenSuse Tumbleweed)
- Python 3.8 oder höher
- Tkinter für die GUI-Version
- Kann im Headless-Modus mit der CLI-Version betrieben werden

## Installation

### Windows
1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Entpacken Sie das Archiv
3. Führen Sie `setup.bat` aus, um Abhängigkeiten zu installieren
4. Starten Sie die Anwendung mit `vsphere_reporter.py`

### Linux
1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Entpacken Sie das Archiv
3. Führen Sie `setup.sh` aus, um Abhängigkeiten zu installieren
4. Starten Sie die GUI-Version mit `vsphere_reporter_linux.py` oder die CLI-Version mit `vsphere_reporter_cli.py`

### OpenSuse Tumbleweed (spezifisch)
1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Installieren Sie Tkinter: `sudo zypper install python3-tk`
3. Entpacken Sie das Archiv
4. Führen Sie `setup.sh` aus, um Abhängigkeiten zu installieren
5. Starten Sie die GUI-Version mit `vsphere_reporter_linux.py`

## Verwendung

### GUI-Version (Windows / Linux)
1. Starten Sie die Anwendung
2. Klicken Sie auf "Connect to vCenter"
3. Geben Sie Ihre vCenter-Serveradresse, Benutzername und Passwort ein
4. Wählen Sie die gewünschten Berichtsoptionen
5. Wählen Sie das gewünschte Exportformat
6. Klicken Sie auf "Generate Report"

### CLI-Version (Linux)
Beispiele für die Verwendung der CLI-Version:

```bash
# Hilfe anzeigen
python3 vsphere_reporter_cli.py --help

# Vollständigen Bericht in HTML-Format erstellen
python3 vsphere_reporter_cli.py --server vcenter.beispiel.de --username administrator@vsphere.local --include-all --format html

# Minimalen Bericht in PDF-Format erstellen
python3 vsphere_reporter_cli.py --server vcenter.beispiel.de --username administrator@vsphere.local --format pdf
```

## Berichtsbereiche

### Obligatorische Abschnitte
- VMware Tools-Versionen (älteste zuerst)
- VM-Snapshots (älteste zuerst)
- Verwaiste VMDK-Dateien

### Optionale Abschnitte
- Virtuelle Maschinen
- ESXi-Hosts
- Datastores
- Cluster
- Resource Pools
- Netzwerke

## Dokumentation

Ausführliche Dokumentation finden Sie im `docs/`-Verzeichnis:
- `admin_guide.md` - Installationsanleitung für Administratoren
- `user_guide.md` - Benutzerhandbuch

## Fehlerbehebung

Bei Problemen überprüfen Sie bitte die Log-Dateien im `logs/`-Verzeichnis.

Typische Probleme und Lösungen:
- **GUI-Fehler auf Linux**: Stellen Sie sicher, dass Tkinter installiert ist oder verwenden Sie die CLI-Version
- **Verbindungsfehler**: Überprüfen Sie Ihre Netzwerkverbindung und vCenter-Anmeldeinformationen
- **Export-Fehler**: Überprüfen Sie die Schreibberechtigungen für das Ausgabeverzeichnis

## Lizenz

© 2025 Alle Rechte vorbehalten.