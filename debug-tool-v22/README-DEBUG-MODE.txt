VSPHERE REPORTER DEBUG-MODUS - SNAPSHOT UND VMDK PROBLEM LÖSEN
============================================================

HINTERGRUND DES PROBLEMS
-----------------------
Die Versionen des VMware vSphere Reporters vor Version 22 hatten ein Problem bei der Erfassung von
Snapshots und orphaned VMDKs. Das Problem lag in einer zu aggressiven Fehlerunterdrückung, die
verhinderte, dass diese Daten korrekt erfasst wurden. Diese speziellen Debug-Tools wurden entwickelt,
um dieses Problem zu beheben.

PROBLEMBESCHREIBUNG
------------------
- Snapshots: Snapshots werden nicht korrekt erkannt oder erscheinen nicht in Berichten
- Orphaned VMDKs: Verwaiste VMDK-Dateien werden nicht erkannt oder erscheinen nicht in Berichten
- Fehlermeldungen werden unterdrückt und nicht protokolliert, was die Diagnose erschwert

SCHNELLSTART - DIAGNOSE-TOOL
---------------------------
Die einfachste Möglichkeit, das Problem zu beheben, ist die Verwendung des separaten Diagnose-Tools:

1. Öffnen Sie die Kommandozeile (cmd.exe)
2. Wechseln Sie zum Verzeichnis mit den Debug-Tools
3. Führen Sie den folgenden Befehl aus:

   debug_cli.bat -s VCENTER_SERVER -u USERNAME -k

   Beispiel:
   debug_cli.bat -s vcenter.example.com -u administrator@vsphere.local -k

4. Geben Sie Ihr Passwort ein, wenn Sie dazu aufgefordert werden
5. Das Tool erfasst und zeigt Snapshots und orphaned VMDKs an
6. Ein detaillierter Bericht wird in debug_report.txt gespeichert

AKTIVIEREN DES DEBUG-MODUS FÜR DIE HAUPTANWENDUNG
------------------------------------------------
Wenn Sie die Debug-Funktionen in der Hauptanwendung verwenden möchten:

Unter Windows:
--------------
1. Verwenden Sie die Batch-Datei:
   debug_mode.bat

2. Oder starten Sie mit dem Debug-Parameter:
   run.bat -debug

3. Oder setzen Sie die Umgebungsvariable manuell:
   set VSPHERE_REPORTER_DEBUG=1
   python vsphere_reporter.py

Unter Linux:
------------
1. Verwenden Sie das bereitgestellte Skript:
   ./debug_mode.sh

2. Oder setzen Sie die Umgebungsvariable manuell:
   VSPHERE_REPORTER_DEBUG=1 python vsphere_reporter_linux.py

FEHLERBEHEBUNG UND LOGS
----------------------
- Debug-Logs werden in das Verzeichnis logs/ geschrieben
- Das eigenständige Diagnose-Tool schreibt in vsphere_debug.log
- Bei Fehlern überprüfen Sie die detaillierten Logs
- Die Ausgaben im Konsolenfenster zeigen im Debug-Modus Traceback-Informationen an

PROBLEMLÖSUNG MIT DEM CLI-TOOL (FÜR FORTGESCHRITTENE BENUTZER)
------------------------------------------------------------
Wenn Sie das eigenständige Diagnose-Tool verwenden möchten und es in Ihre eigenen Skripte integrieren:

1. Rufen Sie debug_cli.py direkt mit den benötigten Parametern auf:
   python debug_cli.py -s VCENTER_SERVER -u USERNAME [-p PASSWORD] [-k] [-o OUTPUT_FILE]

2. Parameter:
   -s, --server    : vCenter-Server (IP oder Hostname)
   -u, --user      : Benutzername
   -p, --password  : Passwort (optional, wird sonst abgefragt)
   -k, --insecure  : SSL-Zertifikatsprüfung ignorieren
   -o, --output    : Ausgabedatei (Standard: debug_report.txt)

3. Das Tool erzeugt eine Textdatei mit den gefundenen Informationen

HINWEISE
-------
- Der Debug-Modus hat eine geringfügig schlechtere Leistung aufgrund der detaillierten Protokollierung
- Für eine temporäre Diagnose empfehlen wir das eigenständige debug_cli.py Tool
- Für eine dauerhafte Lösung empfehlen wir ein Upgrade auf die neueste Version des VMware vSphere Reporters