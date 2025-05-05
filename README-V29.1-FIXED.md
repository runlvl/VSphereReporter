# VMware vSphere Reporter v29.1 (FIXED)

Ein umfassendes Web-basiertes Reporting-Tool für VMware vSphere Umgebungen

## Überblick

Der VMware vSphere Reporter ist ein professionelles Diagnosetool für VMware-Umgebungen, das detaillierte Berichte zu VMware Tools, Snapshots und verwaisten VMDK-Dateien erstellt. Die Version 29 bringt eine vollständig webbasierte Oberfläche, die von jedem modernen Browser aus zugänglich ist.

## Neue Funktionen und Fixes in v29.1

- **Behoben**: Export-Funktionalität für HTML, PDF und DOCX vollständig implementiert
- **Behoben**: VMware Tools Power-Status wird nun korrekt angezeigt 
- **Behoben**: Verbesserter Schutz vor Abstürzen bei der VMDK-Erkennung
- **Behoben**: Demo-Modus funktioniert nun einwandfrei ohne "NoneType"-Fehler
- **Behoben**: Demo-Modus-Button wird immer angezeigt für einfachen Zugang
- **Behoben**: Konflikte zwischen ReportGenerator-Implementierungen beseitigt
- **Verbessert**: Zuverlässigkeit und Fehlerbehandlung in allen Modulen

## Installation

### Windows
1. Entpacken Sie das ZIP-Archiv in ein Verzeichnis Ihrer Wahl
2. Führen Sie `setup.bat` aus, um Abhängigkeiten zu installieren
3. Starten Sie die Anwendung mit `run.bat`
4. Öffnen Sie einen Browser und navigieren Sie zu `http://localhost:5000`

### Linux (OpenSuse Tumbleweed)
1. Entpacken Sie das ZIP-Archiv in ein Verzeichnis Ihrer Wahl
2. Führen Sie `setup.sh` aus, um Abhängigkeiten zu installieren
3. Starten Sie die Anwendung mit `run.sh`
4. Öffnen Sie einen Browser und navigieren Sie zu `http://localhost:5000`

## Demo-Modus

Der Demo-Modus ermöglicht Ihnen, die Funktionalität der Anwendung ohne Verbindung zu einem vCenter zu testen. Klicken Sie auf den "Demo-Modus" Button auf der Login-Seite, um simulierte Daten zu sehen.

## Systemanforderungen

- Python 3.8 oder höher
- Moderne Browser (Chrome, Firefox, Edge)
- Internetverbindung für die Installation der Abhängigkeiten

## Kontakt und Support

Bei Fragen oder Problemen wenden Sie sich bitte an Ihren Bechtle-Ansprechpartner oder den technischen Support.

Copyright © 2025 Bechtle GmbH
