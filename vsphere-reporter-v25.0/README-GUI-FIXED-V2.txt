# VMware vSphere Reporter - Korrigierte Windows GUI Version

## Version 22 - Update 2

### Änderungen
- Dynamische Importierung der Exporter-Module mit absoluten Pfaden
- Behebung des Fehlers "No module named 'core.exporters'"
- Vollständige Verzeichnisstruktur mit allen benötigten Dateien

### Behobene Fehler
- Korrektur des Problems mit fehlenden GUI-Modulen
- Korrektur des Problems mit fehlenden Exporter-Modulen
- Verbesserte Fehlerbehandlung durch dynamisches Laden von Modulen

## Installation

1. Entpacken Sie das ZIP-Archiv in ein beliebiges Verzeichnis
2. Führen Sie die Datei `run.bat` aus

## Debug-Modus

Wenn Sie detailliertere Fehlerinformationen benötigen, führen Sie die Datei `debug_mode.bat` aus.
Dieser Modus zeigt alle Protokollmeldungen an und deaktiviert die Fehlerunterdrückung.

## Anforderungen

- Windows 10 oder höher
- Python 3.8 oder höher (3.11 empfohlen)
- Folgende Python-Pakete:
  - PyQt5
  - PyVmomi
  - reportlab
  - python-docx
  - Jinja2
  - humanize

## Bekannte Probleme

Falls weiterhin Probleme beim Starten auftreten, prüfen Sie bitte:
1. Ob alle Python-Pakete installiert sind (durch Ausführen von `pip install -r requirements.txt`)
2. Ob die Importstruktur durch spezielle Windows-Umgebungen beeinflusst wird

Bei anhaltenden Problemen verwenden Sie bitte den Debug-Modus und senden Sie die Protokolldatei.