# VMware vSphere Reporter v29.0 (Fixed Version v23.1)

## VMDK-Erkennungs-Fehlerbehebungen

Diese Version enthält wichtige Fehlerbehebungen für die Erkennung und Anzeige von verwaisten VMDK-Dateien:

1. **Problem behoben**: Fehler 500 bei der Anzeige von verwaisten VMDK-Dateien im Demo-Modus
2. **Problem behoben**: Fehlende Zeitstempel und Größenangaben bei VMDK-Dateien durch korrekten Import von datetime.timedelta
3. **Problem behoben**: Inkonsistente Datenstrukturen zwischen Demo-Modus und Echtdaten, was zu Anzeigeproblemen führte

## Installation

1. Entpacken Sie die ZIP-Datei in einen Ordner Ihrer Wahl
2. Führen Sie `setup.bat` (Windows) oder `setup.sh` (Linux) aus
3. Starten Sie die Anwendung mit `run.bat` (Windows) oder `run.sh` (Linux)
4. Öffnen Sie einen Browser und navigieren Sie zu http://localhost:5000

## Alternative Startmethode (bei Problemen)

Wenn die Startskripte nicht funktionieren, können Sie die Anwendung auch direkt über Python starten:

```
cd Installationsverzeichnis
python app.py
```

## Fehlerdiagnose

- Logs werden im Verzeichnis `logs/` gespeichert
- Für ausführliche Debug-Ausgaben setzen Sie die Umgebungsvariable `VSPHERE_REPORTER_DEBUG=1`

## Download

Die aktuelle Version finden Sie als ZIP-Datei unter:
- [vsphere-reporter-v29.0-web-final-fixed-v19.1-final-23-vmdk.zip](http://localhost:5011/vsphere-reporter-v29.0-web-final-fixed-v19.1-final-23-vmdk.zip)

## Änderungshistorie

Weitere Details zu den Änderungen finden Sie in der [CHANGELOG-v23.1.txt](http://localhost:5011/CHANGELOG-v23.1.txt) Datei.