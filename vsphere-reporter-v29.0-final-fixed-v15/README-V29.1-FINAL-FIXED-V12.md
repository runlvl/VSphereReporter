# VMware vSphere Reporter - Version 29.1 Final Fixed v12

## Überblick
Der VMware vSphere Reporter ist ein umfassendes Berichtswerkzeug für VMware vSphere-Umgebungen. Es bietet detaillierte Einblicke in den Status Ihrer virtuellen Infrastruktur, einschließlich VMware Tools-Status, Snapshots und verwaiste VMDK-Dateien.

## Neue Funktionen in Version 29.1 (v12)
- Verbesserte visuelle Hervorhebung mit vollständiger Zeilen-Einfärbung für Statusindikatoren
- Sortierbare Tabellen in allen Berichten
- Verbesserte Erkennung von verwaisten VMDKs durch umfassende VMX-Datei-Analyse
- Korrigierter Demo-Modus-Button für einfachere Demonstration
- Aktualisierte Entwicklerinformationen

## Installationsanleitung

### Windows
1. Entpacken Sie die ZIP-Datei in ein beliebiges Verzeichnis
2. Führen Sie `setup.bat` aus, um alle Abhängigkeiten zu installieren
3. Starten Sie die Anwendung mit `run.bat`
4. Öffnen Sie einen Webbrowser und navigieren Sie zu `http://localhost:5000`

### Linux
1. Entpacken Sie die ZIP-Datei in ein beliebiges Verzeichnis
2. Führen Sie `chmod +x setup.sh run.sh` aus, um Ausführungsrechte zu setzen
3. Führen Sie `./setup.sh` aus, um alle Abhängigkeiten zu installieren
4. Starten Sie die Anwendung mit `./run.sh`
5. Öffnen Sie einen Webbrowser und navigieren Sie zu `http://localhost:5000`

## Systemanforderungen
- Python 3.8 oder höher
- Unterstützte Betriebssysteme: Windows, Linux (getestet auf OpenSuse Tumbleweed)
- Internetverbindung für die initiale Paketinstallation
- Netzwerkzugriff zum vCenter-Server
- Mindestens 2 GB RAM und 100 MB freier Festplattenspeicher

## Hauptfunktionen
- **Dashboard**: Übersicht über Ihre vSphere-Umgebung
- **VMware Tools-Bericht**: Status und Version der VMware Tools für alle VMs
- **Snapshot-Bericht**: Detaillierte Informationen zu VM-Snapshots mit Altersangaben
- **Verwaiste VMDKs**: Verbesserte Identifizierung und Überwachung verwaister VMDK-Dateien
- **Exportfunktionen**: Export von Berichten in HTML, PDF und DOCX-Format
- **Demo-Modus**: Testen der Anwendung ohne vCenter-Verbindung (jetzt vollständig funktionsfähig)

## Verbesserte Benutzerfreundlichkeit
- Vollständige Zeilen-Einfärbung für bessere Statuserkennung auf einen Blick
- Intuitive farbliche Kennzeichnung (grün für gut, orange für Warnung, rot für kritisch)
- Sortierbare Tabellenspalten für flexibles Daten-Management
- Responsives Design für verschiedene Bildschirmgrößen

## Bekannte Probleme
- Bei sehr großen vCenter-Umgebungen (> 1000 VMs) kann das Laden der Daten länger dauern

## Fehler melden
Bitte melden Sie Fehler und Verbesserungsvorschläge an Ing. Johann Kiss, Bechtle Austria GmbH.

## Lizenz
Proprietär - © 2025 Bechtle Austria GmbH