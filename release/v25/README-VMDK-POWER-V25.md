# VMware vSphere Reporter v25.0 - VMDK Power Collector

## Verbesserte VMDK-Erkennung für VMware vSphere Reporter

Diese Version enthält einen komplett überarbeiteten Ansatz zur Erkennung von VMDK-Dateien in VMware vSphere-Umgebungen. Die neue Implementierung orientiert sich stark an der Funktionsweise erfolgreicher PowerShell-Skripte und verbessert die Zuverlässigkeit erheblich.

### Hauptmerkmale

- **PowerShell-ähnlicher Ansatz**: Direkte Abfrage aller VMs und ihrer zugehörigen Festplatten.
- **VM-zentrierte Erkennung**: Statt nur in Datastores zu suchen, werden zuerst alle VMs und ihre Festplatten erfasst.
- **Verbesserte Erkennung verwaister VMDKs**: Alle Datastores werden nach VMDKs durchsucht, die keiner VM zugeordnet sind.
- **Mehrere Fallback-Methoden**: Drei verschiedene Ansätze zur VM-Erkennung für höchste Zuverlässigkeit.
- **Erweiterte Fehlerbehandlung**: Jeder Schritt enthält umfassende Fehlerbehandlung, um Abstürze zu vermeiden.

### Installation

Einfach das TAR.GZ-Archiv entpacken und wie gewohnt ausführen:

```bash
# Linux-Installation
tar -xzf vsphere-reporter-linux-v25.0.tar.gz
cd vsphere-reporter-linux-v25.0
python vsphere_reporter.py
```

### Debug-Modus aktivieren

Für eine detaillierte Protokollierung und bessere Fehlerbehebung kann der Debug-Modus aktiviert werden:

```bash
# Debug-Modus aktivieren
VSPHERE_REPORTER_DEBUG=1 python vsphere_reporter.py
```

### Technische Details

Der neue VMDK Collector verwendet folgende Ansätze:

1. **VM-Erkennung**: Alle VMs werden über drei alternative Methoden gefunden:
   - ViewManager: Der schnellste Weg, alle VMs zu finden
   - Datacenter-Traversal: Durchsucht alle Datacenters und ihre VM-Ordner rekursiv
   - PropertyCollector: Direkte Suche nach VM-Objekten über den Property Collector

2. **Disk-Erfassung**: Für jede VM werden alle angeschlossenen Festplatten erfasst, inkl. Pfad, Format und Größe.

3. **Erkennung verwaister VMDKs**: Alle Datastores werden nach VMDK-Dateien durchsucht, die nicht in der VM-Disk-Map enthalten sind.

### Bekannte Einschränkungen

- Erkennt keine flat-VMDKs, da diese immer zu einer Haupt-VMDK gehören
- Erkennt keine speziellen Delta-VMDKs, die für Snapshots verwendet werden

### Support

Bei Problemen oder Fragen wenden Sie sich bitte an das Bechtle-Team.