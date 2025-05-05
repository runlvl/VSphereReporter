# VMware vSphere Reporter v29.0 (Web Edition)

Copyright (c) 2025 Bechtle GmbH

## Beschreibung
Der VMware vSphere Reporter ist ein umfassendes Tool zur Analyse und Berichterstattung für VMware vSphere-Umgebungen. Diese Version 29.0 bietet eine vollständig webbasierte Oberfläche, die auf jedem modernen Browser läuft.

## Hauptfunktionen
- Erkennung veralteter VMware Tools-Versionen
- Identifizierung alter Snapshots
- Zuverlässige Erkennung von verwaisten VMDK-Dateien
- Umfassende Berichterstattung zu vSphere-Ressourcen
- Export in verschiedene Formate (HTML, PDF, DOCX)
- Moderne, responsive Benutzeroberfläche im Bechtle-Design

## Systemvoraussetzungen
- Python 3.8 oder höher
- Internetverbindung für die Installation der Abhängigkeiten
- Netzwerkzugriff auf den vCenter Server
- Unterstützte Betriebssysteme: Windows, Linux

## Installation
### Windows
1. Führen Sie `setup.bat` aus, um alle erforderlichen Abhängigkeiten zu installieren
2. Nach Abschluss der Installation führen Sie `run.bat` aus, um die Anwendung zu starten

### Linux
1. Führen Sie `setup.sh` aus, um alle erforderlichen Abhängigkeiten zu installieren
2. Nach Abschluss der Installation führen Sie `run.sh` aus, um die Anwendung zu starten

## Verwendung
1. Starten Sie die Anwendung mit dem entsprechenden Skript
2. Öffnen Sie einen Browser und navigieren Sie zu: http://localhost:5000
3. Geben Sie Ihre vCenter-Verbindungsdaten ein
4. Wählen Sie die gewünschten Berichtsoptionen
5. Generieren Sie den Bericht

## Berechtigungen
Der verwendete vCenter-Benutzer benötigt mindestens Leserechte auf die folgenden Objekte:
- Virtuelle Maschinen
- ESXi-Hosts
- Datastores
- Netzwerke

## Debug-Modus
Sie können den Debug-Modus aktivieren, indem Sie das entsprechende Skript mit dem Parameter `--debug` oder `-d` ausführen:
- Windows: `run.bat --debug`
- Linux: `run.sh --debug`

## Unterstützung
Bei Problemen oder Fragen wenden Sie sich bitte an den Bechtle-Support.
