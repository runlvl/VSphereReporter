# Bechtle vSphere Reporter - Änderungsprotokoll

## Version 0.1 (Mai 2025)

### Neue Funktionen
- Vollständige Umbenennung und Bechtle Branding-Integration
- Verbesserte VMDK-Erkennung mit intelligenten Fallback-Mechanismen
- Intelligente Startskripte für Windows und Linux
- Optimierte Fehlerbehandlung bei der Datensammlung

### Technische Verbesserungen
- Zuverlässige Erkennung verwaister VMDK-Dateien
- Implementierung von Hash-basierten Fallback-Werten für VMDK-Größen und -Daten
- Erhöhte Stabilität durch erweiterte Fehlerbehandlung
- Verbesserte Leistung bei der Datenbankabfrage

### UI-Verbesserungen
- Konsistentes Bechtle-Farbschema
- Verbessertes Logging-System mit detaillierteren Meldungen
- Dateigrößen werden nun einheitlich in GB angezeigt
- Verbessertes Verhalten bei fehlenden Daten

## Bekannte Probleme
- Die Berichterstellung ist in dieser Version noch nicht implementiert
- Einige Metriken werden bei großen Umgebungen (>1000 VMs) langsam geladen

## Installationshinweise
- Für Windows wird empfohlen, die Anwendung mit `start.bat` zu starten
- Für Linux müssen die Startskripte ausführbar gemacht werden (`chmod +x start.sh`)
- Der automatische Portwechsel funktioniert nur, wenn der Standardport (5000) belegt ist