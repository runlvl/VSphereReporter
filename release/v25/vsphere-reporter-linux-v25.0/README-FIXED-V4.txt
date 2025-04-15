VMware vSphere Reporter - Version 23.1 mit verbesserter Fehlerbehandlung

WICHTIGE ÄNDERUNGEN UND VERBESSERUNGEN:

1. Behebung des Methodennamenkonflikts in der Reportgenerierung:
   - Behoben: AttributeError in main_window.py (Zeile 670) bzgl. 'get_selected_formats'
   - Methode 'self.report_options.get_selected_formats()' durch korrekten Aufruf von 'get_selected_options()' ersetzt
   - Rückgabewerte werden nun korrekt aus dem Ergebnisdictionary extrahiert

2. Verbesserte Fehlerbehandlung mit dreistufigem Fallback-System:
   - Original-Exporter → SimpleHTMLExporter → DummyExporter
   - Effizientere Exception-Behandlung zur Verhinderung von Programmabstürzen
   - Verbesserte Protokollierung zur Fehlerdiagnose

3. Vereinfachte HTML-Exportierung:
   - Alternativer SimpleHTMLExporter funktioniert ohne externe Abhängigkeiten wie Jinja2
   - Robustere Darstellung, die auch mit fehlenden Daten umgehen kann
   - Verbesserte Fehlerunterdrückung mit detaillierten Protokolleinträgen

4. Verbesserte GUI und Benutzerfreundlichkeit:
   - Feste Navigationsleiste in HTML-Berichten
   - Verbesserte Sprungmarken für VM-Snapshots und verwaiste VMDKs
   - Konsistentes Bechtle-Branding

5. Korrigierte Initialisierung der DataCollector-Klasse:
   - Robuste Fehlerbehandlung bei der Datensammlung
   - Automatische Erstellung leerer Datenstrukturen als Fallback
   - Minimierte Abstürze durch überarbeitetes Exception-Handling

INSTALLATIONSHINWEISE:

1. Extraktion:
   Entpacken Sie die ZIP-Datei in ein Verzeichnis Ihrer Wahl.

2. Ausführung:
   a. Windows: Doppelklicken Sie auf die Datei "run.bat" oder führen Sie sie über die Eingabeaufforderung aus.
   b. Linux: Führen Sie das Skript "python3 vsphere_reporter.py" im Terminal aus.

3. Verbindung und Berichtgenerierung:
   a. Klicken Sie auf die Schaltfläche "Verbinden", um eine Verbindung zu Ihrem vCenter herzustellen.
   b. Geben Sie die Verbindungsdaten ein und klicken Sie auf "Verbinden".
   c. Wählen Sie die zu generierenden Berichtsformate aus.
   d. Klicken Sie auf die Schaltfläche "Report generieren", um die Berichte zu erstellen.

WICHTIGE HINWEISE:

1. Diese Version (23.1) korrigiert einen kritischen Fehler, der in früheren Versionen zu Abstürzen bei der Berichtgenerierung führte.
2. Die Anwendung verwendet einen simplen HTML-Fallback-Exporter, wenn der ursprüngliche HTML-Export fehlschlägt.
3. Fehler bei der Berichtsgenerierung führen nicht mehr zum Absturz der Anwendung, sondern werden abgefangen und protokolliert.
4. Bei Problemen überprüfen Sie bitte das Log-Widget in der Anwendung für weitere Informationen.

SYSTEMVORAUSSETZUNGEN:

- Python 3.7 oder höher
- PyQt5
- PyVmomi 7.0.0 oder höher
- Weitere Abhängigkeiten finden Sie in der Datei "requirements.txt"

FEHLERBEHEBUNG:

Falls bei der Berichtgenerierung Probleme auftreten sollten:
1. Überprüfen Sie die Log-Ausgabe in der Anwendung (Log-Level auf DEBUG stellen für detailliertere Informationen).
2. Stellen Sie sicher, dass Sie eine Verbindung zum vCenter hergestellt haben.
3. Versuchen Sie, den Debug-Modus über "debug_mode.bat" (Windows) oder mit der Umgebungsvariablen VSPHERE_REPORTER_DEBUG=1 zu aktivieren.

Bei weiteren Fragen oder Problemen wenden Sie sich bitte an den Bechtle Support.