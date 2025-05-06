# Änderungsprotokoll für VMware vSphere Reporter v29.0 (Build 15)

## Version 29.0 Build 15 (2025-05-06)

### Behoben
- Debugging-Modus für VMDK-Erkennung: Zeigt alle VMDK-Dateien ohne Filterung
  - Klassifikation nach VMDK-Typ (flat-file, delta-file, ctk-file, descriptor)
  - Vollständige Pfadanzeige
  - Sortierung nach Größe
  - Farbkodierung nach Typ für bessere Übersicht

### Debugging-Hilfestellung
- Debug-Version für die Fehlersuche bei verwaisten VMDK-Dateien
- Unterscheidet zwischen verschiedenen VMDK-Typen mit farblicher Hervorhebung
- Zeigt alle VMDK-Dateien ohne Filterung, um die vollständige Dateiliste zu überprüfen
- Keine Filterung verwaister Dateien in dieser Version