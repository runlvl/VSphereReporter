# VMware vSphere Reporter - Installationsanleitung für OpenSuse Tumbleweed

## Überblick

Diese Anleitung erklärt, wie Sie den VMware vSphere Reporter auf Ihrem OpenSuse Tumbleweed-System installieren und einrichten.

## Dateien herunterladen

Da Replit keine direkte Möglichkeit bietet, das gesamte Projekt als ZIP-Datei herunterzuladen, müssen Sie alle Dateien manuell herunterladen oder klonen. Hier sind beide Optionen:

### Option 1: Manueller Download

1. Laden Sie folgende Dateien aus dem Hauptverzeichnis herunter:
   - `vsphere_reporter.py`
   - `vsphere_reporter_cli.py`
   - `vsphere_reporter_linux.py`
   - `vsphere_reporter_requirements.txt`
   - `setup.sh`
   - `setup.bat`
   - `README.md`

2. Erstellen Sie die Verzeichnisstruktur auf Ihrem System:
   ```bash
   mkdir -p ~/vsphere-reporter/{core/{exporters},gui,logs,templates,utils,docs}
   ```

3. Laden Sie die Dateien für jedes Unterverzeichnis herunter:

   **Core-Verzeichnis:**
   - `core/__init__.py`
   - `core/vsphere_client.py`
   - `core/data_collector.py`
   - `core/report_generator.py`

   **Exporters-Verzeichnis:**
   - `core/exporters/__init__.py`
   - `core/exporters/docx_exporter.py`
   - `core/exporters/html_exporter.py`
   - `core/exporters/pdf_exporter.py`

   **GUI-Verzeichnis:**
   - `gui/__init__.py`
   - `gui/connection_dialog.py`
   - `gui/main_window.py`
   - `gui/progress_dialog.py`
   - `gui/report_options.py`

   **Utils-Verzeichnis:**
   - `utils/__init__.py`
   - `utils/helper.py`
   - `utils/logger.py`

   **Templates-Verzeichnis:**
   - `templates/report_template.html`
   - `templates/styles.css`

   **Docs-Verzeichnis:**
   - `docs/admin_guide.md`
   - `docs/user_guide.md`

4. Speichern Sie jede Datei im entsprechenden Verzeichnis auf Ihrem System.

### Option 2: Git Clone (falls das Projekt in GitHub verfügbar ist)

Wenn Sie das Projekt auf GitHub hochgeladen haben, können Sie es einfach clonen:

```bash
git clone https://github.com/username/vsphere-reporter.git ~/vsphere-reporter
cd ~/vsphere-reporter
```

## Installation

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist:
   ```bash
   python3 --version
   ```

2. Installieren Sie Tkinter für die GUI-Version:
   ```bash
   sudo zypper install python3-tk
   ```

3. Führen Sie das Setup-Skript aus, um alle Abhängigkeiten zu installieren:
   ```bash
   cd ~/vsphere-reporter
   chmod +x setup.sh
   ./setup.sh
   ```

4. Überprüfen Sie, ob das Installationsskript erfolgreich ausgeführt wurde.

## Starten der Anwendung

### GUI-Version starten (empfohlen für OpenSuse Tumbleweed)

```bash
cd ~/vsphere-reporter
python3 vsphere_reporter_linux.py
```

Die Tkinter-basierte GUI sollte jetzt erscheinen und Sie können:
- Sich mit Ihrem vCenter verbinden
- Die gewünschten Berichtsoptionen auswählen
- Das Exportformat wählen
- Den Bericht generieren

### Kommandozeilenversion starten (Alternative)

```bash
cd ~/vsphere-reporter
python3 vsphere_reporter_cli.py --server VCENTER_SERVER --username USERNAME --ignore-ssl --format all
```

Ersetzen Sie `VCENTER_SERVER` und `USERNAME` durch Ihre tatsächlichen Werte.

## Fehlerbehebung

### Häufige Probleme und Lösungen

1. **Tkinter-Fehler:**
   ```
   ModuleNotFoundError: No module named 'tkinter'
   ```
   Lösung: Installieren Sie Tkinter mit:
   ```bash
   sudo zypper install python3-tk
   ```

2. **Abhängigkeitsfehler:**
   ```
   ModuleNotFoundError: No module named 'package_name'
   ```
   Lösung: Installieren Sie die fehlende Abhängigkeit mit:
   ```bash
   pip3 install package_name
   ```

3. **Berechtigungsfehler:**
   ```
   PermissionError: [Errno 13] Permission denied: '/path/to/file'
   ```
   Lösung: Prüfen Sie die Berechtigungen und korrigieren Sie sie mit:
   ```bash
   chmod +x /path/to/file
   ```

4. **Displayfehler:**
   ```
   _tkinter.TclError: couldn't connect to display ":0"
   ```
   Lösung: Stellen Sie sicher, dass Sie in einer grafischen Umgebung arbeiten oder verwenden Sie die CLI-Version.

## Weitere Informationen

Für detailliertere Informationen schauen Sie bitte in die Dokumentationsdateien:
- `docs/admin_guide.md` - Installationsanleitung für Administratoren
- `docs/user_guide.md` - Benutzerhandbuch

Bei weiteren Fragen oder Problemen können Sie sich an Ihren Administrator wenden.