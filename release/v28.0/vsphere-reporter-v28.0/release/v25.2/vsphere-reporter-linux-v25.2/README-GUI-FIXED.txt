VMWARE VSPHERE REPORTER - KORRIGIERTE GUI-VERSION 22
==================================================

Dieses Paket enthält die vollständige Windows-Version des VMware vSphere Reporters
mit allen erforderlichen GUI-Modulen und verbesserter Fehlerbehandlung für die 
Erkennung von Snapshots und verwaisten VMDK-Dateien.

WICHTIGE ÄNDERUNGEN
-----------------
- Hinzugefügt: Fehlende GUI-Module, die für den Start der Anwendung erforderlich sind
- Verbessert: Fehlerbehandlung für Snapshots und orphaned VMDKs
- Neu: Debug-Modus für detaillierte Fehlerdiagnose

VERWENDUNG
---------
1. Führen Sie run.bat aus, um die Anwendung zu starten
2. Wenn Sie detaillierte Fehlerinformationen sehen möchten, verwenden Sie debug_mode.bat

VORAUSSETZUNGEN
-------------
- Python 3.8 oder höher
- PyQt5
- pyVmomi
- reportlab
- python-docx
- jinja2
- humanize

Wenn eine dieser Abhängigkeiten fehlt, installieren Sie sie mit:
pip install PyQt5 pyVmomi reportlab python-docx jinja2 humanize