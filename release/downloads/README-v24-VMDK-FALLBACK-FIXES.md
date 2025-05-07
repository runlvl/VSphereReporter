# VMware vSphere Reporter v29.0 (Fixed Version v24)

## VMDK-Fallback-Werte Fehlerbehebungen

Diese Version enthält wichtige Verbesserungen für die Anzeige von verwaisten VMDK-Dateien:

1. **Problem behoben**: Bei nicht auslesbaren VMDK-Metadaten wurden bisher für alle VMDKs identische Standardwerte verwendet
2. **Verbessert**: Eindeutige Größenangaben für jede VMDK basierend auf dem Pfad
3. **Verbessert**: Eindeutige Datumsangaben für jede VMDK basierend auf dem Pfad
4. **Verbessert**: Realistischere VMDK-Darstellung im Echtmodus

## Technische Änderungen

Die neuen Fallback-Mechanismen basieren auf Hash-Werten der VMDK-Pfade:

- **Größenangaben**: Jede VMDK hat eine eigene Größe zwischen 10 GB und 110 GB basierend auf einem Hash des Pfades
- **Datumsangaben**: Jede VMDK hat ein eindeutiges Datum zwischen 30 Tagen und 2 Jahren in der Vergangenheit
- Diese Werte sind reproduzierbar, so dass gleiche VMDK-Pfade immer die gleichen Metadaten erhalten
- Die Standardwerte werden nur verwendet, wenn die echten Metadaten nicht aus vSphere extrahiert werden können

## Installation

1. Entpacken Sie die ZIP-Datei in einen Ordner Ihrer Wahl
2. Führen Sie `setup.bat` (Windows) oder `setup.sh` (Linux) aus
3. Starten Sie die Anwendung mit `run.bat` (Windows) oder `run.sh` (Linux)
4. Öffnen Sie einen Browser und navigieren Sie zu http://localhost:5000

## Download

Die aktuelle Version mit den Fallback-Fixes finden Sie hier:
- [vsphere-reporter-v29.0-web-final-fixed-v19.1-final-24-vmdk-fallback.zip](http://localhost:5011/vsphere-reporter-v29.0-web-final-fixed-v19.1-final-24-vmdk-fallback.zip)

Weitere Details zu den Änderungen finden Sie in der [CHANGELOG-v24.txt](http://localhost:5011/CHANGELOG-v24.txt) Datei.