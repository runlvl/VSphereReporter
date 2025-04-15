# VMware vSphere Reporter - Debug Tool

Dieses Diagnose-Tool wurde speziell entwickelt, um Probleme bei der Erkennung von Snapshots und verwaisten VMDK-Dateien in VMware vSphere-Umgebungen zu identifizieren und zu lösen.

## Funktionen

- Detaillierte Diagnose von VM-Snapshots mit vollständiger Protokollierung
- Gründliche Identifikation verwaister VMDK-Dateien
- Ausführliche Fehlerbehandlung mit Traceback-Informationen
- Export aller gefundenen Daten in JSON-Format
- Erweiterte Logging-Funktionalität mit Datei- und Konsolenausgabe

## Voraussetzungen

- Python 3.8 oder höher
- pyVmomi-Bibliothek (Python-Schnittstelle für das VMware vSphere API)
- Zugriff auf einen VMware vSphere-Server (vCenter)
- Benutzeranmeldedaten mit Leserechten für die vSphere-Umgebung

## Installation

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Installieren Sie die benötigten Abhängigkeiten:

```bash
pip install pyVmomi
```

## Verwendung

```bash
python vsphere_debug_collector.py --server VCENTER_SERVER --username USERNAME [--password PASSWORD] [--ignore-ssl] [--diagnostic-type {snapshots,orphaned-vmdks,all}]
```

### Parameter

- `--server`, `-s`: vCenter-Server-Adresse (erforderlich)
- `--username`, `-u`: vCenter-Benutzername (erforderlich)
- `--password`, `-p`: vCenter-Passwort (optional, wenn nicht angegeben, wird sicher danach gefragt)
- `--ignore-ssl`, `-k`: SSL-Zertifikatvalidierung ignorieren (optional)
- `--diagnostic-type`, `-t`: Art der Diagnose (snapshots, orphaned-vmdks, oder all [Standard])

### Beispiele

Sammle Informationen über Snapshots:

```bash
python vsphere_debug_collector.py --server vcenter.example.com --username administrator@vsphere.local --diagnostic-type snapshots
```

Sammle Informationen über verwaiste VMDK-Dateien:

```bash
python vsphere_debug_collector.py --server vcenter.example.com --username administrator@vsphere.local --diagnostic-type orphaned-vmdks
```

Sammle alle Diagnose-Informationen und ignoriere SSL-Zertifikatvalidierung:

```bash
python vsphere_debug_collector.py --server vcenter.example.com --username administrator@vsphere.local --ignore-ssl
```

## Ausgabe

Das Tool erzeugt:

1. Eine detaillierte Log-Datei im Format `vsphere_debug_YYYYMMDD_HHMMSS.log`
2. JSON-Ausgabedateien für gefundene Snapshots und/oder verwaiste VMDKs:
   - `snapshots_diagnosis_YYYYMMDD_HHMMSS.json`
   - `orphaned_vmdks_diagnosis_YYYYMMDD_HHMMSS.json`

## Fehlerbehandlung

Wenn das Tool keine Snapshots oder verwaisten VMDKs findet, überprüfen Sie:

1. Die Log-Datei auf detaillierte Fehlermeldungen
2. Ob Ihr Benutzer ausreichende Berechtigungen hat
3. Ob Ihre vCenter-Version mit pyVmomi kompatibel ist
4. Die Netzwerkverbindung zum vCenter-Server

## Hinweise zur Sicherheit

- Speichern Sie keine Passwörter in Skripten oder Command-Line-Befehlen
- Verwenden Sie den `--password`-Parameter nicht in produktiven Umgebungen
- Erstellen Sie einen dedizierten Benutzer mit minimalen Berechtigungen für dieses Tool

## Fehlerbehebung

Wenn bei der Diagnose Probleme auftreten, stellen Sie sicher, dass:

1. Die richtige Python-Version verwendet wird (3.8+)
2. Die aktuelle pyVmomi-Version installiert ist
3. Der vCenter-Server erreichbar ist
4. Die Benutzeranmeldedaten korrekt sind
5. Die erforderlichen Berechtigungen vorhanden sind

## Support

Bei Fragen oder Problemen wenden Sie sich an Ihren VMware vSphere-Administrator oder eröffnen Sie ein Issue im GitHub-Repository.

---

© 2025 Bechtle GmbH