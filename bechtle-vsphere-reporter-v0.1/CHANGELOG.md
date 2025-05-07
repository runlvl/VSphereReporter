# Changelog - Bechtle vSphere Reporter

## Version 0.1 (2025-05-07)

**Erste Release-Version mit folgenden Funktionen:**

### Allgemeine Features
- Webbasierte Benutzeroberfläche mit Bechtle-Design
- Responsive UI für verschiedene Geräte
- Einfache Navigation und Bedienung
- Demo-Modus für Präsentationen ohne vCenter-Verbindung
- Export von Berichten in verschiedenen Formaten (HTML, PDF, DOCX)

### VMware-Infrastrukturberichte
- VMware Tools Status-Bericht mit Versionsinformationen
- Snapshot-Bericht mit Altersinformationen und Risikobewertung
- Erkennung und Anzeige verwaister VMDK-Dateien
- Aggregierte Dashboard-Ansicht für schnellen Überblick

### Technik & Optimierungen
- Verbesserte VMDK-Erkennung mit intelligenten Fallback-Mechanismen
- Stabile Verbindungsverwaltung zu vCenter-Servern
- Umfangreiche Fehlerbehandlung bei Verbindungsproblemen
- Implementierung des Bechtle-Designs nach Corporate-Richtlinien
- Optimierte Datenverarbeitung für große vSphere-Umgebungen

### Installation & Deployment
- Einfache Installation unter Windows und Linux
- Automatische Abhängigkeitsinstallation
- ZIP-Paket für einfache Verteilung
- Minimalanforderungen: Python 3.8 oder höher
- Intelligente Starter-Skripte (start.bat/start.sh) mit automatischer Portauswahl
- Verbesserte Fehlererkennung und -behandlung während des Startups
- Automatischer Browser-Start nach Programminitialisierung