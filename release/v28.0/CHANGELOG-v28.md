# VMware vSphere Reporter v28.0 - Changelog

## Neue Funktionen
- **Erweiterte Topologie-Visualisierung**: Verbesserte hierarchische Darstellung der vSphere-Umgebung mit interaktiven Diagrammen und Filtermöglichkeiten
- **Optimiertes VMDK-Management**: Neue VM-zentrierte Ansicht für VMDK-Dateien mit klaren Status-Indikatoren (AKTIV, TEMPLATE, POTENTIELL VERWAIST)
- **Responsive Design**: Verbesserte Darstellung auf verschiedenen Bildschirmgrößen und mobilen Geräten

## Verbesserte Fehlerbehandlung & Stabilität
- **Robuster Report-Generator**: Mehrstufiges Fallback-System zum zuverlässigen Erstellen von Berichten auch bei Fehlern
- **Einfacher HTML-Exporter**: Neuer Fallback-Exporter als Notlösung bei Problemen mit dem komplexen HTML-Exporter
- **Zentralisierte Fehlerbehandlung**: Neues Fehlerbehandlungsmodul für konsistente und benutzerfreundliche Fehlermeldungen
- **Verbesserte Protokollierung**: Erweiterte Fehlerdiagnostik mit ausführlichen Fehlerprotokollen

## UI-Verbesserungen
- **Optimierte Berichtsformatierung**: Bessere Tabellendarstellung und Hervorhebung wichtiger Informationen
- **Erweiterte Filteroptionen**: Zusätzliche Filtermöglichkeiten für Snapshots und VMDKs nach Alter, Größe und Status
- **Verbesserte Farbcodierung**: Intuitive Farbkennzeichnung für kritische Zustände (rot für kritisch, orange für Warnungen)

## Behobene Fehler
- **Berichtgenerierung**: Behoben - Absturz bei der Erstellung von HTML-Berichten mit komplexen Topologiedaten
- **VMDK-Erkennung**: Verbessert - Zuverlässigere Erkennung von potentiell verwaisten VMDKs
- **Datensammlung**: Optimiert - Robusterer Mechanismus zur Sammlung von VM-Daten und Snapshot-Informationen
- **Memory-Leaks**: Behoben - Verbesserte Speicherverwaltung bei der Verarbeitung großer Datenmengen

## Dokumentation
- **Neue Administrationsanleitung**: Umfassende Anleitung zur Installation und Konfiguration
- **VMDK-Management-Guide**: Detaillierte Erläuterung des neuen VMDK-Status-Systems
- **Topologie-Visualisierungshandbuch**: Anleitung zur Nutzung der erweiterten Topologie-Funktionen

## Download-Links
- [Windows-Version (ZIP-Archiv)](vsphere-reporter-windows-v28.0.zip)
- [Linux-Version (TAR.GZ-Archiv)](vsphere-reporter-linux-v28.0.tar.gz)

## Systemanforderungen
- Python 3.8 oder höher
- 4 GB RAM (mind.)
- 500 MB freier Festplattenspeicher
- Netzwerkverbindung zum vCenter Server