# VMware vSphere Reporter v29.1 Final Fixed v13

## Übersicht
Dies ist die Version 13 des VMware vSphere Reporters v29.1 mit folgenden Verbesserungen:
- Vollständig korrigierte Navigation mit grafischen Elementen und Icons
- Farbliche Kennzeichnung für VMware Tools Status
- Farbliche Kennzeichnung für Snapshot-Alter
- Optimierte Darstellung von verwaisten VMDK-Dateien

## Installation

### Windows
1. Entpacken Sie das Archiv in einen beliebigen Ordner
2. Führen Sie `setup.bat` aus, um alle Abhängigkeiten zu installieren
3. Starten Sie den Reporter mit `run.bat`
4. Öffnen Sie in Ihrem Browser die Adresse: http://localhost:5000

### Linux
1. Entpacken Sie das Archiv in einen beliebigen Ordner
2. Führen Sie `chmod +x setup.sh run.sh` aus, um die Skripte ausführbar zu machen
3. Führen Sie `./setup.sh` aus, um alle Abhängigkeiten zu installieren
4. Starten Sie den Reporter mit `./run.sh`
5. Öffnen Sie in Ihrem Browser die Adresse: http://localhost:5000

## Features
- **VMware Tools Status**: Übersicht über alle VMs mit Tool-Status (Up-to-date, Outdated, Not installed)
- **Snapshot Verwaltung**: Auflistung aller Snapshots nach Alter mit farblicher Kennzeichnung
- **Verwaiste VMDKs**: Identifikation von verwaisten VMDK-Dateien mit Größenangabe und Empfehlungen
- **Demo-Modus**: Für Testzwecke ohne vCenter-Verbindung

## Änderungen in V13
Bitte beachten Sie die Datei CHANGELOG-v13.txt für eine vollständige Liste der Änderungen.

## Bekannte Probleme
- Bei sehr großen vSphere-Umgebungen (>1000 VMs) kann die Datenerfassung länger dauern
- Import-Warnungen können ignoriert werden, sie haben keine Auswirkung auf die Funktionalität

## Kontakt
Bei Fragen oder Problemen wenden Sie sich bitte an den Support von Bechtle GmbH.