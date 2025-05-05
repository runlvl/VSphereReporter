# VMware vSphere Reporter v27.0

## Übersicht

VMware vSphere Reporter ist ein leistungsstarkes Tool zur Erstellung umfassender Berichte über Ihre VMware vSphere-Umgebung. Diese Version enthält erhebliche Verbesserungen bei der Visualisierung und VMDK-Berichterstattung.

## Neue Funktionen in Version 27.0

### Interaktive Topologie-Visualisierung

Die Version 27.0 führt eine interaktive grafische Darstellung Ihrer vSphere-Umgebung ein. Diese Topologie-Visualisierung bietet:

- Hierarchische Darstellung von vCenter, Datacenters, Clustern, Hosts und VMs
- Farbkodierte und formbasierte Unterscheidung verschiedener Komponententypen
- Interaktives Ein- und Ausklappen von Umgebungselementen
- Detailansicht per Mauszeiger-Hover
- Optimierte Darstellung auch bei großen Umgebungen

### Verbesserter VMDK-Bericht mit Statusanzeigen

Der VMDK-Bericht wurde grundlegend überarbeitet:

- Anzeige ALLER VMDKs mit Statusindikator (AKTIV, TEMPLATE, POTENTIALLY ORPHANED)
- Farbkodierte Unterscheidung der verschiedenen VMDK-Status
- Verbesserte Erkennung verwaister VMDKs mit detaillierten Erklärungen
- Bessere Übersichtlichkeit durch klare visuelle Hervorhebungen

### Optimierte Berichtsstruktur

- Neuanordnung der Berichtsabschnitte mit Topologie-Übersicht am Anfang
- Verbesserte Navigation zwischen den Abschnitten
- Performanceoptimierungen für schnelleres Laden großer Berichte

## Installation

### Windows

1. Laden Sie das Installationspaket `vsphere-reporter-windows-v27.0.zip` herunter
2. Entpacken Sie die Datei in ein beliebiges Verzeichnis
3. Führen Sie `setup.exe` aus und folgen Sie den Anweisungen des Installationsassistenten

### Linux (OpenSuse Tumbleweed)

1. Laden Sie das Paket `vsphere-reporter-linux-v27.0.tar.gz` herunter
2. Entpacken Sie es mit `tar -xzf vsphere-reporter-linux-v27.0.tar.gz`
3. Wechseln Sie in das Verzeichnis und führen Sie `./setup.sh` aus

## Voraussetzungen

- Python 3.11 oder höher
- Netzwerkzugriff auf den vCenter Server
- Benutzeranmeldeinformationen mit mindestens Lesezugriff auf die vSphere-Umgebung
- Moderne Webbrowser für optimale Darstellung der interaktiven Berichtselemente (Chrome oder Edge empfohlen)

## Dokumentation

Die vollständige Dokumentation finden Sie im Ordner `docs`:
- `TOPOLOGY_FEATURE_GUIDE.md` - Detaillierte Anleitung zur Verwendung der Topologie-Visualisierung
- `INSTALLATIONSANLEITUNG.md` - Ausführliche Installationsanleitung für alle Plattformen
- `BENUTZERHANDBUCH.md` - Umfassendes Handbuch zur Verwendung des Tools

## Bekannte Probleme

- Bei sehr großen Umgebungen (>1000 VMs) kann die Topologie-Visualisierung zu Verzögerungen führen
- Die interaktive Topologie ist derzeit nur im HTML-Bericht verfügbar, nicht in DOCX oder PDF
- Firefox zeigt unter bestimmten Umständen ein abweichendes Verhalten bei der Bericht-Navigation

Vollständige Details finden Sie in `CHANGELOG-v27.0.txt`

## Lizenz

Dieses Produkt ist urheberrechtlich geschützt durch die Bechtle GmbH. Alle Rechte vorbehalten.

Copyright © 2025 Bechtle GmbH