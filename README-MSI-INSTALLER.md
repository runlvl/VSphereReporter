# VMware vSphere Reporter - Windows MSI-Installationspaket

## Übersicht

Dieses erweiterte Installationspaket für den VMware vSphere Reporter bietet eine vollständig automatisierte Installation für Windows-Benutzer. Das MSI-Paket enthält alle notwendigen Komponenten, einschließlich:

- Automatische Python-Installation im Hintergrund (keine separate Python-Installation erforderlich)
- Alle benötigten Abhängigkeiten (PyQt5, pyVmomi, etc.)
- Native Windows-EXE-Datei für die Ausführung ohne sichtbare Python-Umgebung
- Bechtle-Branding und Corporate Design

## Versionen

Das Paket ist in zwei Varianten verfügbar:

1. **MSI-Installer (empfohlen)**: Vollständige Windows-Installation mit Registry-Einträgen, Startmenü-Verknüpfungen und automatischen Updates
2. **Portable Version**: Keine Installation erforderlich, kann von einem USB-Stick oder Netzlaufwerk ausgeführt werden

## Installation

### Über das MSI-Installationspaket

1. Laden Sie das MSI-Installationspaket herunter
2. Führen Sie die Datei `VMwareVSphereReporter_Setup_1.0.0.msi` aus
3. Folgen Sie den Anweisungen des Windows-Installationsassistenten
4. Starten Sie die Anwendung über die Desktop-Verknüpfung oder das Startmenü

### Portable Version

1. Laden Sie das ZIP-Archiv der Portable Version herunter
2. Extrahieren Sie das Archiv in einen beliebigen Ordner
3. Führen Sie die Datei `VMware vSphere Reporter/VMwareVSphereReporter.bat` oder `VMware vSphere Reporter/VMwareVSphereReporter.exe` aus

## Funktionsweise

### Automatische Python-Installation

Das Installationspaket enthält eine eingebettete Python-Umgebung, die im Hintergrund ohne Benutzerinteraktion installiert wird. Diese Umgebung:

- Ist vollständig vom System isoliert
- Erfordert keine Administratorrechte für die Installation von Paketen
- Enthält alle benötigten Abhängigkeiten

### Native Windows-Integration

Die Anwendung startet als native Windows-EXE-Datei:
- Das Kommandozeilenfenster (Python-Interpreter) wird nicht angezeigt
- Die Anwendung verhält sich wie jede andere Windows-Anwendung
- Windows-Verknüpfungen und Installationsoptionen werden unterstützt

## Systemvoraussetzungen

- Windows 7/8/10/11 (64-Bit)
- Mindestens 200 MB freier Festplattenspeicher
- Internetverbindung für VMware vCenter-Zugriff

## Fehlerbehandlung

Sollten bei der Installation oder Ausführung Probleme auftreten:

1. Prüfen Sie, ob Sie über ausreichende Berechtigungen verfügen
2. Stellen Sie sicher, dass keine Antivirensoftware die Installation blockiert
3. Überprüfen Sie, ob genügend Festplattenspeicher zur Verfügung steht
4. Bei Problemen mit der MSI-Installation verwenden Sie die portable Version als Alternative

## Deinstallation

Die Anwendung kann über die Windows-Systemsteuerung (Programme und Features) deinstalliert werden.

## Technische Details

Das MSI-Installationspaket wurde mit folgenden Technologien erstellt:
- cx_Freeze für die Erstellung der Windows-EXE
- Eingebettete Python-Umgebung (Python 3.10)
- WiX Toolset für das MSI-Paket (sofern verfügbar)
- Benutzerdefinierte Launcher für nahtlose Python-Integration

© 2025 Bechtle GmbH