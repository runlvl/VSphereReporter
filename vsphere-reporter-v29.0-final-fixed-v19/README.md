# VMware vSphere Reporter v19.0

Ein umfassendes Tool zur Berichterstellung und Überwachung von VMware vSphere-Umgebungen.

## Übersicht

Der VMware vSphere Reporter ist ein leistungsstarkes Tool für Systemadministratoren, um wichtige Informationen aus ihrer VMware vSphere-Umgebung zu sammeln und zu analysieren. Die Anwendung bietet Berichte zu VMware Tools-Status, VM-Snapshots und verwaisten VMDK-Dateien.

Version 19.0 bietet eine verbesserte Benutzeroberfläche mit robuster VMDK-Erkennung, basierend auf dem erfolgreichen Ansatz von Version 18.

## Funktionen

- **VMware Tools-Status**: Überwachung der VMware Tools-Version und des Installationsstatus für virtuelle Maschinen
- **Snapshot-Altersanalyse**: Identifizierung und Überwachung von VM-Snapshots nach Alter und Größe
- **Erkennung verwaister VMDKs**: Zuverlässige Identifikation von VMDK-Dateien, die keiner VM zugeordnet sind
- **Exportformate**: Unterstützung für HTML, PDF und DOCX-Berichtsformate
- **Fehlertoleranz**: Verbesserte Fehlerbehandlung für stabile Datenerfassung
- **Demo-Modus**: Möglichkeit, die Anwendung mit Beispieldaten zu testen

## Systemvoraussetzungen

- Python 3.8 oder höher
- Internetverbindung für den initialen Download von Abhängigkeiten
- Zugriff auf einen VMware vCenter-Server (nicht erforderlich für Demo-Modus)

## Installation

### Windows

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Entpacken Sie das Archiv in ein beliebiges Verzeichnis
3. Führen Sie `setup.bat` aus, um alle erforderlichen Abhängigkeiten zu installieren
4. Starten Sie die Anwendung mit `run.bat`

### Linux

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Entpacken Sie das Archiv in ein beliebiges Verzeichnis
3. Machen Sie die Setup- und Run-Skripte ausführbar: `chmod +x setup.sh run.sh`
4. Führen Sie `./setup.sh` aus, um alle erforderlichen Abhängigkeiten zu installieren
5. Starten Sie die Anwendung mit `./run.sh`

## Anwendung starten

Nach der Installation kann die Anwendung über die folgenden Methoden gestartet werden:

- **Windows**: Doppelklick auf `run.bat` oder Ausführen von `run.bat` in der Kommandozeile
- **Linux**: Ausführen von `./run.sh` im Terminal

Die Anwendung startet einen Webserver und öffnet automatisch einen Browser mit der Anwendung.

## Fehlerbehebung

Falls Probleme beim Start der Anwendung auftreten:

1. Überprüfen Sie, ob Python 3.8 oder höher installiert ist: `python --version`
2. Stellen Sie sicher, dass alle erforderlichen Abhängigkeiten installiert sind, indem Sie das Setup-Skript erneut ausführen
3. Überprüfen Sie die Protokolldateien im Verzeichnis `logs` für detaillierte Fehlerinformationen
4. Bei Netzwerkproblemen stellen Sie sicher, dass Ihre Firewall die Kommunikation auf dem verwendeten Port zulässt

## Versionshinweise v19.0

- Verbesserte Benutzeroberfläche mit Bootstrap 5
- Robuste VMDK-Erkennung basierend auf dem Ansatz von v18
- Erweiterte Fehlerbehandlung für stabilere Datenerfassung
- Optimierte Filterung für verwaiste VMDKs
- Verbesserte Berichtserstellung für alle Exportformate

---

© 2025 VMware vSphere Reporter