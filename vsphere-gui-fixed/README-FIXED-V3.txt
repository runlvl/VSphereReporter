VMware vSphere Reporter - Version 23 mit verbesserter Fehlerbehandlung

ÄNDERUNGEN UND VERBESSERUNGEN:

1. Fehlerbehandlung für HTML-Export stark verbessert:
   - Alternativer SimpleHTMLExporter implementiert, der ohne externe Abhängigkeiten wie Jinja2 arbeitet
   - Verbesserte Fehlerunterdrückung und Fehlermeldungen, die ins Log-Widget umgeleitet werden
   - Robuste Ausnahmebehandlung, die das Abstürzen der Anwendung verhindert

2. Verbesserte Berichtgenerierung mit Fallback-Mechanismen:
   - Dreistufiges Fallback-System: Original-Exporter → SimpleHTMLExporter → DummyExporter
   - Leere Datenstrukturen werden nun automatisch erstellt, anstatt zu Abstürzen zu führen
   - Detaillierte Diagnoseausgabe im Log zur einfacheren Fehlerbehebung

3. Verbesserte GUI:
   - Feste Navigationsleiste in HTML-Berichten
   - Verbesserte Sprungmarken für VM-Snapshots und verwaiste VMDKs
   - Bechtle-Branding konsistent angewendet
   - Korrigierte Initialisierung der DataCollector-Klasse

4. Allgemeine Robustheitsverbesserungen:
   - Verbesserte Fehlerbehandlung im Template-System
   - Gründlichere Exception-Handling
   - Verbesserte Protokollierung zur Fehlerdiagnose
   - Anpassungen an verschiedene Umgebungskonfigurationen

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

1. Die Anwendung verwendet einen simplen HTML-Fallback-Exporter, wenn der ursprüngliche HTML-Export fehlschlägt.
2. Fehler bei der Berichtsgenerierung führen nicht mehr zum Absturz der Anwendung, sondern werden abgefangen und protokolliert.
3. Bei Problemen überprüfen Sie bitte das Log-Widget in der Anwendung für weitere Informationen.

SYSTEMVORAUSSETZUNGEN:

- Python 3.7 oder höher
- PyQt5
- PyVmomi 7.0.0 oder höher
- Weitere Abhängigkeiten finden Sie in der Datei "requirements.txt"

FEHLERBEHEBUNG:

Falls bei der Berichtsgenerierung Probleme auftreten sollten:
1. Überprüfen Sie die Log-Ausgabe in der Anwendung (Log-Level auf DEBUG stellen für detailliertere Informationen).
2. Stellen Sie sicher, dass Sie eine Verbindung zum vCenter hergestellt haben.
3. Versuchen Sie, den Debug-Modus über "debug_mode.bat" (Windows) oder mit der Umgebungsvariablen VSPHERE_REPORTER_DEBUG=1 zu aktivieren.

Bei weiteren Fragen oder Problemen wenden Sie sich bitte an den Bechtle Support.