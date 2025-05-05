# CHANGELOG für VMware vSphere Reporter v29.0

## Version 29.0 (Mai 2025)

### Hauptänderungen
- **Vollständig neue browserbasierte Benutzeroberfläche**
  - Zugriff über jeden modernen Webbrowser möglich
  - Keine lokale Installation von PyQt5 oder anderen GUI-Bibliotheken erforderlich
  - Responsive Design für Desktop- und Tablet-Nutzung

### Neue Funktionen
- **Web-basierte Benutzeroberfläche**
  - Modernes, responsives Design basierend auf Bootstrap
  - Verbesserte Benutzerfreundlichkeit mit intuitiver Navigation
  - Unterstützung für mehrere gleichzeitige Benutzer

- **Verbesserte Berichterstellung**
  - Interaktive Topologie-Visualisierung direkt im Browser
  - Verbesserte Export-Optionen für HTML, PDF und DOCX
  - Erweiterte Filteroptionen für Berichte

- **Verbesserte Fehlerbehandlung**
  - Robustes Fehlerbehandlungssystem mit Fallback-Mechanismen
  - Detaillierte Fehlerdiagnose und -protokollierung
  - Verbessertes Benutzerfeedback bei Verbindungsproblemen

### Technische Verbesserungen
- **Neue Architektur**
  - Flask-basiertes Backend für die Weboberfläche
  - Verbesserte Skalierbarkeit durch Trennung von Frontend und Backend
  - Performanceoptimierung für große vSphere-Umgebungen

- **Verbesserte Datenerfassung**
  - Optimierte Algorithmen für die Erkennung verwaister VMDKs
  - Schnellere Snapshot-Analyse
  - Verbesserte VM-Hardware-Informationssammlung

- **Sicherheitsverbesserungen**
  - Keine dauerhafte Speicherung von vCenter-Anmeldedaten
  - Sitzungsverwaltung mit automatischem Timeout
  - Verbesserte SSL-Zertifikatsprüfung

### Behobene Fehler
- Beseitigung von Abstürzen bei der VMDK-Analyse in großen Umgebungen
- Behebung von Darstellungsproblemen bei der Topologie-Visualisierung
- Korrektur der Snapshot-Zeitberechnungen für bessere Genauigkeit
- Behebung von Problemen bei der PDF-Generierung mit großen Berichten

### Sonstiges
- Vollständig neue Dokumentation mit detaillierten Installationsanleitungen
- Verbesserte README-Dateien und Benutzerhandbücher
- Neue Setup-Skripte für einfachere Installation auf Linux und Windows