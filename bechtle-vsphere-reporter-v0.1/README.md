# Bechtle vSphere Reporter v0.1

Ein umfassendes Berichtswerkzeug für VMware vSphere-Umgebungen, das detaillierte Berichte über den Status Ihrer virtuellen Infrastruktur generiert.

## Funktionen

- **VMware Tools Status**: Überprüfen Sie den Installationsstatus und die Version der VMware Tools auf allen VMs
- **Snapshot-Analyse**: Identifizieren Sie alte oder potenziell problematische Snapshots
- **Verwaiste VMDK-Erkennung**: Finden Sie verwaiste virtuelle Festplatten, die Speicherplatz verschwenden
- **Mehrere Berichtsformate**: HTML, PDF und DOCX für einfaches Teilen und Archivieren
- **Demo-Modus**: Testen Sie die Anwendung ohne vCenter-Verbindung

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- Webbrowser (Chrome, Firefox, Edge oder Safari empfohlen)
- Internetzugang für die Installation von Abhängigkeiten

### Windows

1. Entpacken Sie die ZIP-Datei in ein Verzeichnis Ihrer Wahl
2. Führen Sie `start.bat` aus, um den intelligenten Starter mit automatischer Port-Auswahl zu verwenden (empfohlen)
3. Alternativ können Sie `app.py` direkt mit Python ausführen: `python app.py`

### Linux

1. Entpacken Sie die ZIP-Datei in ein Verzeichnis Ihrer Wahl
2. Führen Sie `start.sh` aus, um den intelligenten Starter mit automatischer Port-Auswahl zu verwenden (empfohlen)
   ```
   chmod +x start.sh
   ./start.sh
   ```
3. Alternativ können Sie `app.py` direkt mit Python ausführen: `python3 app.py`

### Abhängigkeiten installieren

Wenn die Abhängigkeiten nicht automatisch installiert werden, können Sie sie manuell installieren:

```
pip install -r requirements.txt
```

## Verwendung

1. Starten Sie die Anwendung mit einem der oben genannten Befehle
2. Ein Webbrowser öffnet sich automatisch mit der Anwendung
3. Melden Sie sich mit Ihren vCenter-Zugangsdaten an oder verwenden Sie den Demo-Modus
4. Wählen Sie die gewünschten Berichtsoptionen und Formate aus
5. Generieren Sie den Bericht und laden Sie ihn herunter

## Fehlerbehebung

- **Port bereits in Verwendung**: Der intelligente Starter versucht automatisch, einen verfügbaren Port zu finden. Sollte dies fehlschlagen, können Sie manuell einen Port angeben: `start.bat --port 5001` oder `./start.sh --port 5001`
- **Debug-Modus**: Für detailliertere Logs starten Sie im Debug-Modus: `start.bat --debug` oder `./start.sh --debug`
- **Logs**: Log-Dateien werden im Unterverzeichnis `logs` gespeichert

## Bekannte Probleme

- OpenSUSE Tumbleweed: Bei einigen OpenSUSE Tumbleweed-Installationen kann es zu Anzeigeproblemen bei der Berichtsdarstellung kommen. In diesem Fall versuchen Sie, einen alternativen Browser zu verwenden.

## Lizenz

© 2025 Bechtle GmbH. Alle Rechte vorbehalten.