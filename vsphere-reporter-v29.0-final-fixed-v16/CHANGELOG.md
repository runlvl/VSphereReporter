# Änderungsprotokoll für VMware vSphere Reporter v29.0 (Build 16)

## Version 29.0 Build 16 (2025-05-06)

### EXTREME DEBUG-MODUS für VMDK-Erkennung
- Sehr detailliertes Logging auf DEBUG-Level für alle Funktionen hinzugefügt
- Stack-Traces für alle auftretenden Ausnahmen werden in die Log-Datei geschrieben
- Extra Informationen zur Fehlerbehebung für die VMDK-Erkennung
- Verbesserte Fehlerbehandlung und Statusanzeigen auf der Weboberfläche
- Zusätzliche Überprüfung, ob Datastores einen funktionierenden Browser haben
- Umfangreiche Validierung der zurückgegebenen Werte bei allen API-Aufrufen
- Zeigt Debug-Banner mit hilfreichen Informationen für Administratoren

### Debugging-Hilfestellung
- Debug-Version für die Fehlersuche bei verwaisten VMDK-Dateien
- Unterscheidet zwischen verschiedenen VMDK-Typen mit farblicher Hervorhebung
- Zeigt alle VMDK-Dateien ohne Filterung, um die vollständige Dateiliste zu überprüfen
- Verbesserte Fehlermeldungen im Frontend, wenn keine VMDKs gefunden werden