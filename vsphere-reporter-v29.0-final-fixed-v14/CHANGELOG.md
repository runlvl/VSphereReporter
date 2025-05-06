# Änderungsprotokoll für VMware vSphere Reporter v29.0 (Build 14)

## Version 29.0 Build 14 (2025-05-06)

### Behoben
- Verbesserte Erkennung von verwaisten VMDK-Dateien mit folgenden Kriterien:
  - Berücksichtigung von Templates und Template-VMDKs
  - Erweiterte Prüfung auf VM-zugehörige Verzeichnisse
  - Verbesserte Erkennung von Snapshot-bezogenen Dateien
  - Verbesserte Validierung durch Prüfung von VMX-Dateien
- Farbkodierung in allen Tabellen überarbeitet mit Bootstrap-Tabellenklassen:
  - VMware Tools-Status (grün, gelb, rot für Status)
  - Snapshot-Alter (grün, gelb, rot für Alter)
  - Verwaiste VMDK-Dateigrößen (info, gelb, rot für Größe)
- Tabellendarstellung mit besseren Rahmen und Formatierung

### Änderungen
- Bootstrap-Tabellenklassen für konsistente Darstellung in verschiedenen Browsern
- Verbesserte Empfehlungen für verwaiste VMDKs basierend auf Dateigröße
- Besseres Logging während der VMDK-Analyse