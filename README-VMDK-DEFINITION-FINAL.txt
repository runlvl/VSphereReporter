=====================================================
VMware vSphere Reporter - VMDK-Erkennung (v24.3-FINAL)
=====================================================

## Neue Definition für verwaiste VMDKs (ab v24.3-FINAL)

Eine VMDK-Datei gilt als "verwaist", wenn sie keiner registrierten VM zugeordnet ist.

Dies ist eine stark vereinfachte Definition gegenüber früheren Versionen, die zusätzliche Kriterien 
wie das Vorhandensein einer VMX-Datei oder den Template-Status berücksichtigten.

## Der neue Erkennungsalgorithmus

Die Implementierung folgt einem klaren, dreistufigen Ansatz:

1. Sammeln aller in Verwendung befindlichen VMDK-Dateien von allen VMs (inkl. Templates)
2. Sammeln aller VMDK-Dateien von allen Datastores
3. Identifizieren der VMDKs, die nicht in Verwendung sind (verwaist)

## Verbesserter Pfadvergleich

Da VMDK-Dateien in verschiedenen Formaten referenziert werden können, berücksichtigt 
der Algorithmus mehrere Varianten für jeden Pfad:

- Vollständiger Pfad: "[datastore1] vm/disk.vmdk"
- Pfad ohne Datastore-Klammern: "vm/disk.vmdk"
- Nur Dateiname: "disk.vmdk"

Dies sorgt für eine zuverlässigere Erkennung in unterschiedlichen Umgebungen.

## Filterung von Hilfsdateien

Nur -flat.vmdk Dateien werden automatisch ausgeschlossen, da sie eine spezielle 
Funktion haben und immer mit einer anderen VMDK-Datei verknüpft sind.

Alle anderen VMDK-Typen (wie -delta.vmdk, -ctk.vmdk, etc.) werden jetzt als 
potenzielle verwaiste VMDKs betrachtet, wenn sie keiner VM zugeordnet sind.

## Debug-Modus und Demo-Daten

Im Debug-Modus (VSPHERE_REPORTER_DEBUG=1) werden ausführliche Log-Meldungen 
für jede Phase der VMDK-Erkennung ausgegeben. Wenn keine verwaisten VMDKs 
gefunden werden, wird automatisch eine Demo-VMDK angezeigt.

## Fehlerbehebung

Falls keine verwaisten VMDKs angezeigt werden:

1. Stellen Sie sicher, dass die Anwendung im Debug-Modus ausgeführt wird
2. Überprüfen Sie die Log-Dateien im logs/-Verzeichnis
3. Bestätigen Sie, dass der Benutzer Leserechte auf alle Datastores hat

## Anwendung in Ihrer Umgebung

Diese vereinfachte Definition kann dazu führen, dass mehr VMDKs als "verwaist" 
gemeldet werden als in früheren Versionen. Dies ist beabsichtigt, um alle
potenziell problematischen Dateien anzuzeigen, die eventuell bereinigt werden sollten.