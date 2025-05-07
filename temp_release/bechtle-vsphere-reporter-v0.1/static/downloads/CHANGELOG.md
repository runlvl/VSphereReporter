# Bechtle vSphere Reporter - Änderungsprotokoll

## Version 0.1 (Mai 2025)

### Neue Funktionen
- Vollständige Umbenennung und Bechtle Branding im Corporate Design
- Verbesserte VMDK-Erkennung mit intelligenten Fallback-Mechanismen
- Intelligente Startskripte für Windows und Linux mit automatischer Porterkennung
- Optimierte Fehlerbehandlung bei der Datensammlung ohne Abstürze
- Browserbasierte Oberfläche für plattformübergreifende Nutzung

### Technische Verbesserungen
- Zuverlässige Erkennung verwaister VMDK-Dateien mit verbessertem Algorithmus
- Implementierung von Hash-basierten Fallback-Werten für VMDK-Größen und -Daten
- Erhöhte Stabilität durch umfassende Fehlerbehandlung und Logging
- Verbesserte Leistung bei der Datenbankabfrage
- Automatische Wiederverbindung bei Verbindungsabbrüchen

### UI-Verbesserungen
- Konsistentes Bechtle-Farbschema (#00355e, #da6f1e, #23a96a, #f3f3f3, #5a5a5a)
- Überarbeitetes Navigationssystem mit verbesserten Tooltips
- Verbessertes Logging-System mit detaillierteren Meldungen
- Dateigrößen werden nun einheitlich in GB angezeigt (10-110 GB)
- Verbesserte Datumsdarstellung mit relativen Zeitangaben (30-730 Tage)

## Systemanforderungen
- Python 3.8 oder höher
- Unterstützte Betriebssysteme: Windows 10/11, Windows Server 2019/2022, OpenSUSE Tumbleweed
- Mindestens 2 GB RAM und 500 MB freier Festplattenspeicher
- Netzwerkverbindung zu einem vCenter Server 6.5 oder höher

## Installationshinweise
- **Windows**: Führen Sie nach dem Entpacken `start.bat` aus (empfohlen)
- **Linux**: Führen Sie nach dem Entpacken `chmod +x start.sh` und dann `./start.sh` aus
- Anwendung ist nach dem Start über einen Webbrowser unter der angezeigten URL erreichbar
- Standardport ist 5000, wird aber automatisch angepasst, wenn dieser bereits belegt ist

## Bekannte Probleme
- Die Berichterstellung (PDF/DOCX) ist in dieser Version noch nicht vollständig implementiert
- Einige Metriken werden bei großen Umgebungen (>1000 VMs) langsamer geladen