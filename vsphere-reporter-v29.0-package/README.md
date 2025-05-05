# VMware vSphere Reporter v29.0 - Web Edition

Eine umfassende Anwendung zur Analyse und Berichterstattung für VMware vSphere-Umgebungen.

**Copyright (c) 2025 Bechtle GmbH**

## Übersicht

Der VMware vSphere Reporter ist ein leistungsstarkes Tool zur Analyse und Berichterstattung von VMware vSphere-Umgebungen. Es ermöglicht die einfache Identifikation potenzieller Problembereiche wie veraltete VMware Tools, alte Snapshots und verwaiste VMDK-Dateien.

Version 29.0 wurde vollständig überarbeitet und bietet nun eine moderne, webbasierte Benutzeroberfläche, die von jedem Browser aus zugänglich ist. Diese neue Architektur eliminiert die Notwendigkeit einer lokalen GUI-Installation und verbessert die Plattformunabhängigkeit erheblich.

## Hauptfunktionen

- **Vollständig webbasiert**: Zugriff von jedem modernen Webbrowser aus ohne lokale Installation
- **VMware Tools-Analyse**: Identifizierung veralteter VMware Tools-Versionen, sortiert nach Alter
- **Snapshot-Management**: Erkennung und Analyse von VM-Snapshots mit detaillierten Alters- und Größeninformationen
- **Verwaiste VMDK-Erkennung**: Zuverlässige Identifikation potenziell verwaister VMDK-Dateien
- **Flexible Berichtsoptionen**: Anpassbare Berichte mit verschiedenen Abschnitten
- **Mehrere Exportformate**: Unterstützung für HTML, PDF und DOCX (Word)
- **Responsive Designkonzept**: Optimierte Benutzeroberfläche für Desktop und mobile Geräte
- **Demo-Modus**: Testen der Funktionalität ohne tatsächliche vCenter-Verbindung

## Systemanforderungen

- **Python**: Version 3.8 oder höher
- **Betriebssystem**: Windows 10/11 oder Linux (OpenSuse Tumbleweed empfohlen)
- **Browser**: Chrome, Firefox, Edge oder Safari (neueste Version)
- **Netzwerk**: Verbindung zum vCenter Server
- **Benutzerrechte**: Lesezugriff auf die vSphere-Umgebung

## Installation

### Windows

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Entpacken Sie das Archiv in ein Verzeichnis Ihrer Wahl
3. Führen Sie `setup.bat` aus, um die Abhängigkeiten zu installieren
4. Starten Sie die Anwendung mit `run.bat`
5. Navigieren Sie zu http://localhost:5009 in Ihrem Webbrowser

### Linux

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Entpacken Sie das Archiv in ein Verzeichnis Ihrer Wahl
3. Führen Sie `chmod +x setup.sh run.sh` aus, um die Skripte ausführbar zu machen
4. Führen Sie `./setup.sh` aus, um die Abhängigkeiten zu installieren
5. Starten Sie die Anwendung mit `./run.sh`
6. Navigieren Sie zu http://localhost:5009 in Ihrem Webbrowser

### Virtuelle Umgebung (optional, aber empfohlen)

Die Installationsskripte bieten die Option, eine virtuelle Python-Umgebung zu erstellen, was empfohlen wird, um Abhängigkeitskonflikte zu vermeiden.

## Verwendung

1. **Verbinden**: Stellen Sie eine Verbindung zu Ihrem vCenter-Server her
2. **Berichtsoptionen auswählen**: Wählen Sie die gewünschten Berichtsabschnitte und das Exportformat
3. **Bericht generieren**: Starten Sie die Berichtsgenerierung
4. **Bericht anzeigen/herunterladen**: Der generierte Bericht wird im Browser angezeigt oder zum Download angeboten

## Demo-Modus

Der Demo-Modus ermöglicht es Ihnen, die Funktionalität der Anwendung ohne tatsächliche vCenter-Verbindung zu testen. Dieser Modus generiert Beispieldaten für alle Berichtsabschnitte. Sie können den Demo-Modus beim Start der Anwendung aktivieren.

## Fehlerbehebung

- **Port 5009 bereits belegt**: Die Startskripte bieten die Möglichkeit, einen alternativen Port zu wählen
- **Verbindungsprobleme**: Stellen Sie sicher, dass der vCenter-Server erreichbar ist und Sie gültige Anmeldeinformationen verwenden
- **SSL-Fehler**: Aktivieren Sie die Option "SSL-Zertifikatsprüfung deaktivieren" bei selbstsignierten Zertifikaten

## Weitere Informationen

Weitere Informationen und detaillierte Dokumentation finden Sie in der [Online-Dokumentation](https://www.bechtle.com/vsphere-reporter-docs) (Bitte beachten Sie, dass diese Dokumentation nur für registrierte Benutzer verfügbar ist).

## Lizenz

Copyright (c) 2025 Bechtle GmbH. Alle Rechte vorbehalten.

Die Nutzung dieser Software unterliegt den Lizenzbestimmungen der Bechtle GmbH. Die Software darf nur mit einer gültigen Lizenz verwendet werden.