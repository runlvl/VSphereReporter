# VMware vSphere Reporter v25.2

## Überblick

Der VMware vSphere Reporter ist ein umfassendes Tool zur Erstellung von Berichten über VMware vSphere-Umgebungen. Version 25.2 konzentriert sich auf eine grundlegend verbesserte Erkennung verwaister VMDKs mit PowerShell-inspirierter Methodik.

## Vollständig überarbeitete VMDK-Erkennung

Diese Version bietet eine komplett neu implementierte Methode zur Erkennung verwaister VMDKs:

1. **PowerShell-inspirierter Ansatz**
   - Vollständig neuer Algorithmus basierend auf dem erfolgreichen PowerShell-Skript
   - VM-zentrierter Ansatz zur Erfassung aller Festplatten
   - Mehrstufige Vergleichslogik für maximale Präzision

2. **Verbesserte Pfadvergleiche**
   - Mehrere unterschiedliche Pfadnormalisierungen zum Abgleich
   - Vergleich von vollständigen Pfaden, relativen Pfaden und Dateinamen
   - Umfassende Fallback-Mechanismen für verschiedene VMDK-Pfadformate

3. **Präzisere Identifikation**
   - Verbesserte Filter für Hilfsdateien (flat, delta, ctk, rdm)
   - Erkennung versteckter Abhängigkeiten zwischen VMDKs
   - Direkte Überprüfungen auf VM-Referenzen

4. **Ausführliches Logging**
   - Detaillierte Debug-Ausgaben zu allen Entscheidungsprozessen
   - Transparent nachvollziehbare Kriterien für die VMDK-Klassifizierung
   - Umfassende Erklärungen im Bericht

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

3. Verbinden Sie sich mit Ihrem vCenter-Server und geben Sie dabei Ihre Anmeldedaten ein.

4. Wählen Sie im Berichtsoptionen-Bereich die gewünschten Berichte aus, einschließlich "Verwaiste VMDKs".

5. Wählen Sie das gewünschte Exportformat und klicken Sie auf "Bericht generieren".

## Problembehebung

Sollten keine oder zu wenige verwaiste VMDKs angezeigt werden:

1. Starten Sie die Anwendung im Debug-Modus, um detaillierte Ausgaben zu erhalten
2. Überprüfen Sie die Logs unter "logs/" für genaue Informationen zur VMDK-Erkennung
3. Stellen Sie sicher, dass die Berechtigungen des angemeldeten Benutzers ausreichend sind

## Unterschied zu früheren Versionen

Version 25.2 verwendet eine vollständig neue, PowerShell-inspirierte Methode zur VMDK-Erkennung, die eine noch zuverlässigere Identifikation verwaister VMDKs bietet als frühere Versionen. Der Fokus liegt auf echter Präzision statt auf der Anzeige potenziell falscher Ergebnisse.