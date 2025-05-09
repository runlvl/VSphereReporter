# Bechtle vSphere Reporter v0.2 - Changelog

## Version 0.2 (09.05.2025)

### Neue Funktionen
- Interaktive Infrastruktur-Topologie mit ECharts.js für verbesserte Visualisierung
- Umfassender Report Generator mit Unterstützung für mehrere Exportformate:
  - HTML: Strukturierte Präsentation mit Bechtle-Branding
  - PDF: Formatierte Tabellen mit Farbcodierung
  - DOCX: Editierbare Dokumentation im MS Word Format
- Verbesserte Demo-Daten für Tests ohne vCenter-Verbindung
- Download-Seite für erstellte Berichte mit Format-Icons

### Verbesserungen
- Optimierte Datenabrufroutinen für zuverlässigere Ergebnisse
- Konsistente Darstellung der Versionsnummer v0.2 in allen Oberflächen
- Verbessertes Dashboard mit direkten Exportoptionen
- Einheitliches Bechtle-Design für alle generierten Berichte

### Korrekturen
- Behoben: Probleme beim Zugriff auf Datenattribute im VSphereClient
- Behoben: Fehler in der Darstellung verwaister VMDK-Dateien
- Behoben: Falsche Größenanzeige in den Snapshot-Berichten
- Verbessert: Fehlerbehandlung während der Datenerfassung

### Technische Änderungen
- Demo-Datenmodul eingeführt zur Entkopplung von Testdaten und Produktionscode
- Jinja2-Templates für konsistente Berichtsdarstellung
- Verbesserte Logging-Funktionen für einfachere Fehlerbehebung
- Neue basename-Filter-Funktion für verbesserte Dateianzeige