# VMware vSphere Reporter v25.0

## Überblick

Der VMware vSphere Reporter ist ein umfassendes Tool zur Erstellung von Berichten über VMware vSphere-Umgebungen. Diese Version bringt einen bahnbrechenden neuen Ansatz für die VMDK-Erkennung und verbesserte Stabilität.

## Hauptfunktionen

- **Umfassende Berichterstattung**: Erstellt detaillierte Berichte über VMware Tools, Snapshots und verwaiste VMDKs
- **Verbesserte VMDK-Erkennung**: Neuer VM-zentrierter Ansatz nach dem Vorbild erfolgreicher PowerShell-Skripte
- **Dreistufiger Fallback-Mechanismus**: Hohe Zuverlässigkeit auch in komplexen Umgebungen
- **Multi-Format-Export**: HTML, DOCX und PDF-Berichte mit professionellem Bechtle-Design
- **Plattformübergreifende Unterstützung**: Vollständige Funktionalität unter Windows und Linux

## Neue Features in v25.0

1. **Komplett überarbeiteter VMDK-Collector**
   - VM-zentrierter Ansatz für zuverlässigere Ergebnisse
   - PowerShell-ähnliche Implementierung für bessere Kompatibilität
   - Präzisere Definition und Erkennung verwaister VMDKs

2. **Verbesserte VM-Discovery-Methoden**
   - Dreistufiger Ansatz mit automatischem Fallback:
     * ViewManager (primär)
     * Datacenter-Traversal (Fallback)
     * PropertyCollector (erweiterte Fallback-Option)

3. **Optimierte Snapshot-Erkennung**
   - Verbesserte Erkennung und Altersberechnung
   - Korrekte Sortierung nach Alter (älteste zuerst)

4. **Benutzerfreundlichkeit**
   - Detaillierte Statusmeldungen während der Datensammlung
   - Verbesserte Fehlerbehandlung ohne Programmabbrüche
   - Konsistentes Bechtle-Design in allen Berichten und der Benutzeroberfläche

## Systemanforderungen

- **Python**: 3.8 oder höher
- **Abhängigkeiten**: PyVmomi, PyQt5, Reportlab, python-docx, Jinja2, Humanize
- **Unterstützte Betriebssysteme**: Windows, Linux (einschließlich OpenSuse Tumbleweed)

## Weitere Informationen

- Detaillierte Installationsanweisungen finden Sie in der `INSTALL-v25.0.txt`
- Vollständige Liste der Änderungen in `CHANGELOG-v25.0.txt`
- Demo-Modus zum Testen der Benutzeroberfläche ohne vSphere-Verbindung