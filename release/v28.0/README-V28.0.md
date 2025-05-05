# VMware vSphere Reporter v28.0

## Übersicht

VMware vSphere Reporter ist ein umfassendes Tool zur Analyse und Berichterstattung von VMware vSphere-Umgebungen. Die Version 28.0 baut auf den Verbesserungen der Version 27.0 auf und bietet erweiterte Funktionen für Topologie-Visualisierung und VMDK-Management.

## Neue und verbesserte Funktionen in Version 28.0

### Erweiterte Topologie-Visualisierung

- **Umfassendere Darstellung**: Vollständige hierarchische Visualisierung der vSphere-Infrastruktur von vCenter bis zu den VMs
- **Filterfunktionen**: Komponententypen können individuell ein- und ausgeblendet werden
- **Exportmöglichkeiten**: Topologie-Diagramme können als SVG oder PNG exportiert werden
- **Verbesserte Detailansicht**: Tooltip-Informationen zeigen nun auch Ressourcenauslastung und Konfigurationsdetails

### Erweiterte VMDK-Management-Funktionen

- **Suchfunktion**: Filtern und Suchen nach VMDK-Namen, Größe oder Status
- **CSV-Export**: VMDK-Listen können für Dokumentation oder Analyse exportiert werden
- **Verbesserte Klassifizierung**: Detailliertere Statusangaben und Erklärungen zu potenziell verwaisten VMDKs
- **Gruppierungsmöglichkeiten**: Gruppierung nach Datastore oder VM für bessere Übersicht

### PDF-Berichte mit Topologie-Diagrammen

- **Statische Topologie-Visualisierungen**: PDF-Berichte enthalten nun auch Topologie-Diagramme
- **Anpassbare Detailtiefe**: Kontrolle über den Umfang der exportierten Informationen
- **Verbesserte Formatierung**: Optimierte Tabellendarstellung in exportierten Berichten

## Installation

### Windows

1. Laden Sie das Installationspaket `vsphere-reporter-windows-v28.0.zip` herunter
2. Entpacken Sie die Datei in ein beliebiges Verzeichnis
3. Führen Sie `setup.exe` aus und folgen Sie den Anweisungen des Installationsassistenten

### Linux (OpenSuse Tumbleweed)

1. Laden Sie das Paket `vsphere-reporter-linux-v28.0.tar.gz` herunter
2. Entpacken Sie es mit `tar -xzf vsphere-reporter-linux-v28.0.tar.gz`
3. Wechseln Sie in das Verzeichnis und führen Sie `./setup.sh` aus

## Systemanforderungen

- **Betriebssystem**: Windows 10/11 oder OpenSuse Tumbleweed 
- **CPU**: Mindestens Dual-Core Prozessor (Quad-Core empfohlen für große Umgebungen)
- **RAM**: Mindestens 4 GB (8 GB empfohlen für große Umgebungen)
- **Python**: Version 3.11 oder höher (wird mit dem Installer mitgeliefert)
- **Netzwerk**: Zugriff auf den vCenter Server
- **Berechtigungen**: Benutzeraccount mit mindestens Read-Only-Zugriff auf die vSphere-Umgebung

## Dokumentation

Die vollständige Dokumentation finden Sie im Ordner `docs`:
- `ERWEITERTE_TOPOLOGIE_GUIDE.md` - Detaillierte Anleitung zur Nutzung der erweiterten Topologie-Funktionen
- `VMDK_MANAGEMENT.md` - Leitfaden zum VMDK-Management und zur Identifikation verwaister VMDKs
- `INSTALLATIONSANLEITUNG.md` - Ausführliche Installationsanleitung für alle Plattformen
- `BENUTZERHANDBUCH.md` - Umfassendes Handbuch zur Verwendung des Tools

## Bekannte Probleme und Einschränkungen

- Bei vSphere 6.7 stehen einige erweiterte VMDK-Suchfunktionen nicht zur Verfügung
- Die Linux-Version bietet derzeit noch nicht alle Barrierefreiheitsfunktionen
- Bei besonders komplexen Umgebungen mit mehr als 1000 VMs kann die Topologie-Visualisierung sehr ressourcenintensiv werden

Vollständige Details finden Sie in `CHANGELOG-v28.0.txt`.

## Lizenz und Urheberrecht

Dieses Produkt ist urheberrechtlich geschützt durch die Bechtle GmbH.
Alle Rechte vorbehalten.

Copyright © 2025 Bechtle GmbH