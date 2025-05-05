# VMware vSphere Reporter v29.1 (Bugfix-Edition)

Diese Version enthält wichtige Fehlerbehebungen für Version 29.0 des vSphere Reporters.

## Installationsanleitung

### Windows
1. Entpacken Sie die ZIP-Datei in ein Verzeichnis Ihrer Wahl
2. Führen Sie `setup.bat` aus, um die benötigten Abhängigkeiten zu installieren
3. Starten Sie die Anwendung mit `run.bat`
4. Greifen Sie über Ihren Browser auf die in der Konsole angezeigte URL zu (normalerweise http://localhost:5000)

### Linux
1. Entpacken Sie die ZIP-Datei in ein Verzeichnis Ihrer Wahl
2. Führen Sie `setup.sh` aus, um die benötigten Abhängigkeiten zu installieren
   ```
   chmod +x setup.sh
   ./setup.sh
   ```
3. Starten Sie die Anwendung mit `run.sh`
   ```
   chmod +x run.sh
   ./run.sh
   ```
4. Greifen Sie über Ihren Browser auf die in der Konsole angezeigte URL zu (normalerweise http://localhost:5000)

## Behobene Probleme in dieser Version

1. **VMware Tools Power-Status-Anzeige**
   - Der Power-Status wird nun korrekt in der VMware Tools-Übersicht angezeigt
   - Status wird als "Eingeschaltet" oder "Ausgeschaltet" dargestellt

2. **Verarbeitung von verwaisten VMDK-Dateien**
   - Robuste Behandlung von verwaisten VMDK-Dateien mit Null-Checks
   - Verbesserte Fehlerbehandlung und Protokollierung

3. **Export-Funktionalität**
   - Implementierung von HTML-Exporten mit Bechtle-Design
   - Implementierung von PDF-Exporten für Berichte
   - Implementierung von DOCX-Exporten für Berichte
   - Unterstützung für den Export einzelner Berichte und aller Berichte zusammen

## Demo-Modus

Die Anwendung bietet einen Demo-Modus, der keine Verbindung zu einem vCenter benötigt:

1. Starten Sie die Anwendung wie oben beschrieben
2. Auf der Login-Seite klicken Sie auf "Demo-Modus starten"
3. Sie können nun alle Funktionen mit simulierten Daten testen

## Unterstützte Browser

* Google Chrome (empfohlen)
* Mozilla Firefox
* Microsoft Edge
* Safari

## Lizenz

Copyright © 2025 Bechtle GmbH. Alle Rechte vorbehalten.