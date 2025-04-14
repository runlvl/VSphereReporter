VSPHERE REPORTER DEBUG-MODUS
============================

Der Debug-Modus verbessert die Fehlerdiagnose, indem er:
1. PyVmomi-Fehlermeldungen anzeigt statt sie zu unterdrücken
2. Detaillierte Traceback-Informationen für Fehler ausgibt
3. Zusätzliche Diagnose-Informationen im HTML-Report anzeigt

AKTIVIEREN DES DEBUG-MODUS:

Unter Linux:
------------
1. Starten Sie die Anwendung mit dem bereitgestellten Skript:
   ./debug_mode.sh

2. Oder setzen Sie die Umgebungsvariable manuell:
   VSPHERE_REPORTER_DEBUG=1 python vsphere_reporter_linux.py
   VSPHERE_REPORTER_DEBUG=1 python vsphere_reporter_cli.py [parameter]

Unter Windows:
--------------
1. Starten Sie die Anwendung mit dem Debug-Parameter:
   run.bat -debug

2. Oder setzen Sie die Umgebungsvariable manuell:
   set VSPHERE_REPORTER_DEBUG=1
   python vsphere_reporter.py

ANALYSIEREN VON FEHLERN:
-----------------------
Im Debug-Modus werden detaillierte Fehlermeldungen in der Konsole und 
in der Protokolldatei (logs/vsphere_reporter_*.log) ausgegeben.

Bei Problemen mit der Datenerfassung zeigt der HTML-Report zusätzliche 
Debug-Informationen an, die bei der Diagnose helfen können.
