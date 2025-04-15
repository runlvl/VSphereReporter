=====================================================
VMware vSphere Reporter - VMDK-Anzeige (v24.3-FINAL)
=====================================================

## Neuer Ansatz für VMDK-Anzeige (ab v24.3-FINAL)

Statt zu versuchen, "verwaiste" VMDK-Dateien zu identifizieren, zeigt die Anwendung jetzt
ALLE VMDK-Dateien in der Umgebung an, die auf den Datastores gefunden wurden.

Dies ist ein völlig neuer Ansatz gegenüber früheren Versionen, die versuchten, nur "verwaiste"
VMDKs anzuzeigen und komplexe Filterungskriterien verwendeten.

## Der neue Algorithmus

Die Implementierung folgt einem einfachen, direkten Ansatz:

1. Alle Datastores durchsuchen
2. Alle VMDK-Dateien sammeln (außer -flat.vmdk)
3. Alle gefundenen VMDKs anzeigen

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