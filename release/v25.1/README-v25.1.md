# VMware vSphere Reporter v25.1

## Überblick

Der VMware vSphere Reporter ist ein umfassendes Tool zur Erstellung von Berichten über VMware vSphere-Umgebungen. Version 25.1 konzentriert sich auf eine erheblich verbesserte Erkennung verwaister VMDKs.

## Verbesserungen gegenüber v25.0

Diese Version bietet einen wesentlich verbesserten Mechanismus zur Erkennung verwaister VMDKs:

1. **Verbesserte Pfadnormalisierung**
   - VMDKs werden mit verschiedenen Pfadformaten verglichen
   - Groß-/Kleinschreibung wird bei der Suche ignoriert
   - Mehrere Normalisierungsvarianten für zuverlässigere Zuordnung

2. **Robustere Erkennung**
   - Mehrschichtige Prüfung von VMDK-Pfaden
   - Vergleich mit und ohne Datastore-Präfix
   - Umfassende Filterung von Helper-VMDKs (flat, delta, ctk, etc.)

3. **Intelligenter Fallback-Mechanismus**
   - Automatischer Wechsel zu weniger strikter Definition wenn nötig
   - Kennzeichnung von "möglicherweise verwaisten" VMDKs als Fallback
   - Aussagekräftige Erklärungen für jeden VMDK-Typ

4. **Optimierte Debug-Ausgaben**
   - Detaillierte Pfadvergleichsinformationen
   - Transparente Nachvollziehbarkeit der Erkennungsentscheidungen
   - Verbesserte Fehlerprotokollierung

## Systemanforderungen

- **Python**: 3.8 oder höher
- **Abhängigkeiten**: PyVmomi, PyQt5, Reportlab, python-docx, Jinja2, Humanize
- **Unterstützte Betriebssysteme**: Windows, Linux (einschließlich OpenSuse Tumbleweed)

## Nutzungshinweise

1. Starten Sie die Anwendung mit dem entsprechenden Skript für Ihr Betriebssystem:
   - Windows: `run.bat`
   - Linux: `./run.sh`

2. Für erweiterte Debug-Ausgaben starten Sie im Debug-Modus:
   - Windows: `run.bat --debug`
   - Linux: `./run.sh --debug`

3. Die VMDK-Erkennung verwendet nun mehrere Pfadnormalisierungen und Fallback-Strategien, um die Zuverlässigkeit der Erkennung zu verbessern, insbesondere in komplexen Umgebungen.

## Problembehebung

Sollten keine verwaisten VMDKs angezeigt werden, obwohl Sie welche erwarten:

1. Starten Sie im Debug-Modus, um detaillierte Ausgaben zu sehen
2. Der Fallback-Mechanismus sollte automatisch aktiviert werden
3. Überprüfen Sie die Logs im logs/-Verzeichnis auf detaillierte Informationen