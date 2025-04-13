# VMware vSphere Reporter - Installationsanleitung für OpenSuse Tumbleweed

## Überblick

Diese Anleitung erklärt, wie Sie den VMware vSphere Reporter auf Ihrem OpenSuse Tumbleweed-System installieren und einrichten.

## Installation mit virtuellem Environment

OpenSuse Tumbleweed verwendet ein "externally managed environment", was bedeutet, dass pip-Installationen auf Systemebene blockiert sind. Wir verwenden daher ein virtuelles Python-Environment für die Installation.

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist:
   ```bash
   python3 --version
   ```

2. Installieren Sie benötigte Systempakete für OpenSuse Tumbleweed:
   ```bash
   sudo zypper install python3-tk python3-pip python3-venv python3-devel gcc patterns-devel-base-devel_basis
   ```

3. Führen Sie das Setup-Skript aus, um alle Abhängigkeiten zu installieren:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   Das Script erstellt ein virtuelles Environment und installiert alle nötigen Abhängigkeiten.

4. Verwenden Sie die erstellten Launcher-Skripte:
   ```bash
   # Für die GUI-Version:
   ./run_linux_gui.sh
   
   # Für die CLI-Version:
   ./run_cli.sh --help
   ```

## Manuelle Installation mit virtuellem Environment

Wenn das Setup-Skript Probleme verursacht, können Sie die Installation manuell durchführen:

1. Installieren Sie zuerst die grundlegenden Systempakete:
   ```bash
   sudo zypper install python3-tk python3-pip python3-venv python3-devel gcc patterns-devel-base-devel_basis
   ```

2. Erstellen Sie ein virtuelles Environment:
   ```bash
   python3 -m venv ./venv
   ```

3. Aktivieren Sie das virtuelle Environment:
   ```bash
   source ./venv/bin/activate
   ```

4. Aktualisieren Sie pip im virtuellen Environment:
   ```bash
   pip install --upgrade pip
   ```

5. Installieren Sie die Abhängigkeiten im virtuellen Environment:
   ```bash
   pip install pyVmomi six requests PyQt5>=5.15.0 reportlab>=3.6.0 python-docx>=0.8.11 jinja2>=3.0.0 humanize>=3.0.0
   ```

6. Machen Sie die Skripte ausführbar:
   ```bash
   chmod +x vsphere_reporter_linux.py vsphere_reporter_cli.py
   ```

7. Erstellen Sie Launcher-Skripte:
   ```bash
   # Erstellen Sie ein Launcher-Skript für die GUI
   echo '#!/bin/bash
   source "./venv/bin/activate"
   python3 vsphere_reporter_linux.py "$@"' > run_linux_gui.sh
   chmod +x run_linux_gui.sh
   
   # Erstellen Sie ein Launcher-Skript für die CLI
   echo '#!/bin/bash
   source "./venv/bin/activate"
   python3 vsphere_reporter_cli.py "$@"' > run_cli.sh
   chmod +x run_cli.sh
   ```

## Verwendung des Programms

### GUI-Version starten (empfohlen für OpenSuse Tumbleweed)

```bash
./run_linux_gui.sh
```

Die Tkinter-basierte GUI sollte jetzt erscheinen und Sie können:
- Sich mit Ihrem vCenter verbinden
- Die gewünschten Berichtsoptionen auswählen
- Das Exportformat wählen
- Den Bericht generieren

### Kommandozeilenversion starten (Alternative)

```bash
./run_cli.sh --server VCENTER_SERVER --username USERNAME --ignore-ssl --format all
```

Ersetzen Sie `VCENTER_SERVER` und `USERNAME` durch Ihre tatsächlichen Werte.

## Fehlerbehebung

### Häufige Probleme und Lösungen

1. **"externally-managed-environment" Fehler:**
   ```
   error: externally-managed-environment
   ```
   Lösung: Verwenden Sie ein virtuelles Environment:
   ```bash
   python3 -m venv ./venv
   source ./venv/bin/activate
   pip install ...
   ```

2. **Module nicht gefunden (wie pyVim oder pyVmomi):**
   ```
   ModuleNotFoundError: No module named 'pyVim'
   ```
   Lösung: Stellen Sie sicher, dass Sie das virtuelle Environment aktiviert haben:
   ```bash
   source ./venv/bin/activate
   pip install --upgrade pyVmomi six requests
   ```

3. **Tkinter-Fehler:**
   ```
   ModuleNotFoundError: No module named 'tkinter'
   ```
   Lösung: Installieren Sie Tkinter mit:
   ```bash
   sudo zypper install python3-tk
   ```

4. **Probleme mit C-Extension-Kompilierung:**
   ```
   error: command 'gcc' failed with exit status 1
   ```
   Lösung: Installieren Sie Entwicklungstools:
   ```bash
   sudo zypper install patterns-devel-base-devel_basis
   ```

5. **SSL-Zertifikat Probleme bei Verbindung zu vCenter:**
   Lösung: Verwenden Sie die Option `--ignore-ssl` bei der CLI-Version oder aktivieren Sie "SSL-Zertifikat ignorieren" in der GUI.

6. **Probleme mit dem virtuellen Environment:**
   Wenn das virtuelle Environment nicht richtig funktioniert, versuchen Sie es neu zu erstellen:
   ```bash
   rm -rf ./venv
   python3 -m venv ./venv
   ```

## Weitere Informationen

Für detailliertere Informationen schauen Sie bitte in die Dokumentationsdateien:
- `docs/admin_guide.md` - Installationsanleitung für Administratoren
- `docs/user_guide.md` - Benutzerhandbuch

Bei weiteren Fragen oder Problemen können Sie sich an Ihren Administrator wenden.