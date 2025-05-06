# Änderungsprotokoll für VMware vSphere Reporter v29.0 (Build 17)

## Version 29.0 Build 17 (2025-05-06)

### ALTERNATIVE METHODE für VMDK-Erkennung
- Völlig neue Implementierung der VMDK-Erkennung 
- Zweistufiger Ansatz für Konsistenz und Genauigkeit:
  - Sammelt zuerst alle registrierten VMDKs direkt von VM-Konfigurationen
  - Durchsucht dann alle Datastores separat mit SearchDatastoreSubFolders_Task API
  - Vergleicht die Pfade für genaue Statusbestimmung
- Verwendet einen subfolderübergreifenden Suchalgorithmus für bessere Abdeckung
- Unterscheidung zwischen "In Verwendung" und "Möglicherweise verwaist" für alle gefundenen VMDKs

### Verbesserte Fehlererkennung und Debugging
- Detaillierte Protokollierung aller API-Aufrufe für Fehlerbehebung
- Try-Except Blöcke auf mehreren Ebenen der API-Verarbeitung
- Umfassendere Fehlerbehandlung in wait_for_task Funktion
- Kontrollierte Rückgabe im Fehlerfall, um Abstürze zu vermeiden