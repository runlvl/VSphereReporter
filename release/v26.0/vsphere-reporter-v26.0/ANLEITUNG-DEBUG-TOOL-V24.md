# Anleitung zum VMware vSphere Reporter Debug-Tool v24

Diese Anleitung beschreibt, wie Sie das Debug-Tool verwenden, um Probleme mit der Erkennung von Snapshots und verwaisten VMDK-Dateien zu beheben.

## Hintergrund

In einigen vSphere-Umgebungen können die Standard-Datenerfassungsmethoden für VM-Snapshots und verwaiste VMDK-Dateien nicht alle Informationen korrekt erfassen. Das Debug-Tool ist speziell für die Diagnose und Lösung dieser Probleme konzipiert.

## Installation

1. Laden Sie das Archiv `vsphere-reporter-debug-tool-v24.zip` herunter
2. Entpacken Sie das Archiv in ein beliebiges Verzeichnis
3. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
4. Installieren Sie die benötigten Abhängigkeiten:

```bash
pip install pyVmomi
```

## Verwendung

### Windows

1. Navigieren Sie zum Verzeichnis des entpackten Debug-Tools
2. Doppelklicken Sie auf `run_debug_tool.bat`
3. Folgen Sie den Anweisungen auf dem Bildschirm:
   - Geben Sie die vCenter-Server-Adresse ein
   - Geben Sie Ihren vCenter-Benutzernamen ein
   - Wählen Sie den Diagnosetyp (Snapshots, verwaiste VMDKs oder beides)
   - Entscheiden Sie, ob die SSL-Zertifikatvalidierung ignoriert werden soll
4. Geben Sie Ihr Passwort ein, wenn Sie dazu aufgefordert werden
5. Warten Sie, bis die Diagnose abgeschlossen ist

### Linux

1. Öffnen Sie ein Terminal und navigieren Sie zum Verzeichnis des entpackten Debug-Tools
2. Machen Sie das Skript ausführbar, falls noch nicht geschehen:

```bash
chmod +x run_debug_tool.sh
```

3. Führen Sie das Skript aus:

```bash
./run_debug_tool.sh
```

4. Folgen Sie den Anweisungen auf dem Bildschirm, wie bei der Windows-Version

## Ergebnisse verstehen

Nach Abschluss der Diagnose erstellt das Tool:

1. Eine detaillierte Log-Datei (`vsphere_debug_*.log`)
2. JSON-Dateien mit den gefundenen Snapshots und/oder verwaisten VMDKs

### Die Log-Datei enthält:

- Detaillierte Informationen über die Verbindung zum vCenter
- Die bei der Datenerfassung ausgeführten Schritte
- Gefundene VM-Snapshots und deren Eigenschaften
- Identifizierte verwaiste VMDK-Dateien
- Eventuelle Fehler und deren Stacktraces

### Die JSON-Dateien enthalten:

- Strukturierte Daten zu Snapshots oder verwaisten VMDKs
- Alle relevanten Eigenschaften wie Pfade, Größen, Erstellungsdaten usw.
- Diese Dateien können für eine weitere Analyse verwendet werden

## Fehlerbehebung

Wenn das Tool Probleme meldet oder keine Ergebnisse liefert:

1. Überprüfen Sie die Log-Datei auf spezifische Fehlermeldungen
2. Stellen Sie sicher, dass Ihre vCenter-Anmeldedaten korrekt sind
3. Überprüfen Sie, ob Sie ausreichende Berechtigungen haben
4. Stellen Sie sicher, dass Ihre Netzwerkverbindung zum vCenter funktioniert
5. Überprüfen Sie, ob der SSL-Zertifikatstatus korrekt konfiguriert ist

## Weitere Schritte

Nachdem Sie die Daten mit dem Debug-Tool gesammelt haben:

1. Vergleichen Sie die vom Debug-Tool gefundenen Snapshots/VMDKs mit denen, die in den regulären Berichten erscheinen
2. Identifizieren Sie eventuelle Diskrepanzen
3. Verwenden Sie die im Debug-Tool implementierten verbesserten Methoden als Referenz für Updates in der Hauptanwendung

## Support

Bei Fragen oder Problemen mit dem Debug-Tool wenden Sie sich bitte an:

- Technischer Support: support@example.com
- Dokumentation: https://example.com/vsphere-reporter-docs

---

© 2025 Bechtle GmbH