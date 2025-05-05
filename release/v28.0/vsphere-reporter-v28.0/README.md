# VMware vSphere Reporter v28.0

## Übersicht
Der VMware vSphere Reporter ist ein umfassendes Tool zur Analyse und Berichterstattung von VMware vSphere-Umgebungen. Mit Version 28.0 bietet die Anwendung erweiterte Funktionen zur Topologie-Visualisierung, verbessertes VMDK-Management und eine robustere Fehlerbehandlung.

## Hauptfunktionen
- **Umfassende Umgebungsberichte**: Detaillierte Berichte zu VMware Tools, Snapshots, und VMDKs
- **Erweiterte Topologie-Visualisierung**: Interaktive Diagramme der vSphere-Infrastruktur
- **Verbessertes VMDK-Management**: Erweiterte Erkennung und Klassifizierung von VMDKs
- **Multi-Format-Export**: Export von Berichten in HTML, DOCX und PDF
- **Benutzerfreundliche Oberfläche**: Moderne GUI im Bechtle-Design für Windows und Linux

## Systemanforderungen
- Python 3.8 oder höher
- 4 GB RAM (empfohlen)
- 500 MB freier Festplattenspeicher
- Netzwerkverbindung zum vCenter Server

## Installation

### Windows
1. Laden Sie die aktuelle Windows-Version herunter
2. Entpacken Sie die ZIP-Datei in ein Verzeichnis Ihrer Wahl
3. Führen Sie `setup.bat` aus, um die Abhängigkeiten zu installieren
4. Starten Sie die Anwendung mit `run.bat`

### Linux (OpenSuse Tumbleweed)
1. Laden Sie die aktuelle Linux-Version herunter
2. Entpacken Sie die TAR.GZ-Datei: `tar -xzf vsphere-reporter-linux-v28.0.tar.gz`
3. Führen Sie `setup.sh` aus, um die Abhängigkeiten zu installieren
4. Starten Sie die Anwendung mit `python vsphere_reporter.py`

## Verwendung
1. Starten Sie die Anwendung
2. Geben Sie die vCenter-Server-Adresse ein
3. Geben Sie Ihre Anmeldedaten ein
4. Wählen Sie die gewünschten Berichtsoptionen
5. Klicken Sie auf "Verbinden und Daten sammeln"
6. Nach Abschluss der Datensammlung können Sie Berichte in verschiedenen Formaten generieren

## Fehlerbehebung
Falls bei der Berichterstellung Probleme auftreten:
- Prüfen Sie die Protokolldateien im `logs`-Verzeichnis
- Stellen Sie sicher, dass die Berechtigungen für den Zugriff auf den vCenter-Server ausreichend sind
- Aktivieren Sie den Debug-Modus mit der Umgebungsvariable `VSPHERE_REPORTER_DEBUG=1`
- Bei Abstürzen während der Berichterstellung verwendet die Anwendung automatisch einen einfachen HTML-Exporter als Fallback

## Dokumentation
Weitere Dokumentation finden Sie in den folgenden Dateien:
- `docs/ERWEITERTE_TOPOLOGIE_GUIDE.md` - Anleitung zur Topologie-Visualisierung
- `docs/VMDK_MANAGEMENT.md` - Details zum verbesserten VMDK-Management
- `docs/FEHLERBEHANDLUNG.md` - Informationen zur Fehlerdiagnose

## Lizenz
© 2025 Bechtle GmbH. Alle Rechte vorbehalten.