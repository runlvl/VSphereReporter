# VMware vSphere Reporter - Verwaiste VMDK-Debugging-Anleitung

## Anleitung für Administratoren

Wenn die Software keine verwaisten VMDKs findet, obwohl Sie wissen, dass welche existieren sollten, können folgende Maßnahmen hilfreich sein:

### 1. Debug-Modus aktivieren

Der Debug-Modus liefert detaillierte Informationen über den Erkennungsprozess und kann helfen, Probleme zu identifizieren:

Unter Windows:
```
set VSPHERE_REPORTER_DEBUG=1
vsphere_reporter.py
```

Unter Linux:
```
export VSPHERE_REPORTER_DEBUG=1
python3 vsphere_reporter.py
```

### 2. Debuggen mit dem CLI-Tool

Das CLI-Tool kann zusätzliche Informationen liefern:

```
python vsphere_reporter_cli.py --server VCENTER-SERVER --username ADMIN --ignore-ssl --output-dir ./reports
```

### 3. Häufige Gründe für fehlende VMDKs im Bericht

1. **Filterkriterien zu streng**: Die Software filtert bestimmte VMDK-Typen aus, wie -flat.vmdk, -delta.vmdk, etc.
   
2. **VMX-Zuordnung**: Wenn eine VMDK im gleichen Verzeichnis wie eine VMX-Datei liegt und ähnliche Namen haben, wird die VMDK nicht als verwaist betrachtet.
   
3. **Berechtigungen**: Die Software benötigt ausreichende Berechtigungen, um alle Datastores zu durchsuchen.

### 4. Lösungsansätze

1. Prüfen Sie, ob die VMDK-Dateien in den Log-Dateien erscheinen. Diese finden Sie im `logs`-Verzeichnis.

2. Verwenden Sie das Debug-Flag und suchen Sie nach Einträgen wie "Found VMDK" oder "Skipping auxiliary VMDK".

3. Prüfen Sie, ob es VMX-Dateien im gleichen Verzeichnis gibt, die als zugehörig erkannt werden könnten.

### 5. Manuelle Überprüfung

Wenn Sie eine bestimmte VMDK-Datei überprüfen möchten:

1. Notieren Sie den vollständigen Pfad der VMDK (inkl. Datastore).
2. Suchen Sie im Debug-Log nach diesem Pfad.
3. Überprüfen Sie ob die Datei als "in use" oder als "auxiliary" eingestuft wurde.

### 6. Kontakt zum Support

Sollten Sie weiterhin Probleme haben, senden Sie bitte die Debug-Logs an den Support unter:
support@bechtle.com

---
© Bechtle GmbH 2025