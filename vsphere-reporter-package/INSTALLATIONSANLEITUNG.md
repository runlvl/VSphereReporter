# VMware vSphere Reporter - Installationsanleitung für OpenSuse Tumbleweed

## Überblick

Diese Anleitung erklärt, wie Sie den VMware vSphere Reporter auf Ihrem OpenSuse Tumbleweed-System installieren und einrichten.

## Installation

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist:
   ```bash
   python3 --version
   ```

2. Installieren Sie benötigte Systempakete für OpenSuse Tumbleweed:
   ```bash
   sudo zypper install python3-tk python3-pip python3-devel gcc patterns-devel-base-devel_basis
   ```

3. Führen Sie das Setup-Skript aus, um alle Abhängigkeiten zu installieren:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. Überprüfen Sie, ob das Installationsskript erfolgreich ausgeführt wurde.

## Manuelle Installation (falls das Setup-Skript fehlschlägt)

Wenn das Setup-Skript Probleme verursacht, können Sie die Abhängigkeiten auch manuell installieren:

1. Installieren Sie zuerst die grundlegenden Systempakete:
   ```bash
   sudo zypper install python3-tk python3-pip python3-devel gcc patterns-devel-base-devel_basis
   ```

2. Aktualisieren Sie pip auf die neueste Version:
   ```bash
   python3 -m pip install --upgrade pip
   ```

3. Installieren Sie die PyVmomi-Bibliothek (wichtig für die VMware-Verbindung):
   ```bash
   pip3 install --upgrade pyVmomi
   ```

4. Installieren Sie die restlichen Python-Abhängigkeiten:
   ```bash
   pip3 install PyQt5>=5.15.0 reportlab>=3.6.0 python-docx>=0.8.11 jinja2>=3.0.0 humanize>=3.0.0
   ```

5. Machen Sie die Skripte ausführbar:
   ```bash
   chmod +x vsphere_reporter_linux.py vsphere_reporter_cli.py
   ```

## Starten der Anwendung

### GUI-Version starten (empfohlen für OpenSuse Tumbleweed)

```bash
python3 vsphere_reporter_linux.py
```

Die Tkinter-basierte GUI sollte jetzt erscheinen und Sie können:
- Sich mit Ihrem vCenter verbinden
- Die gewünschten Berichtsoptionen auswählen
- Das Exportformat wählen
- Den Bericht generieren

### Kommandozeilenversion starten (Alternative)

```bash
python3 vsphere_reporter_cli.py --server VCENTER_SERVER --username USERNAME --ignore-ssl --format all
```

Ersetzen Sie `VCENTER_SERVER` und `USERNAME` durch Ihre tatsächlichen Werte.

## Fehlerbehebung

### Häufige Probleme und Lösungen

1. **Module nicht gefunden (wie pyVim oder pyVmomi):**
   ```
   ModuleNotFoundError: No module named 'pyVim'
   ```
   Lösung: Installieren Sie PyVmomi erneut mit:
   ```bash
   pip3 install --upgrade pyVmomi
   ```

2. **Tkinter-Fehler:**
   ```
   ModuleNotFoundError: No module named 'tkinter'
   ```
   Lösung: Installieren Sie Tkinter mit:
   ```bash
   sudo zypper install python3-tk
   ```

3. **Probleme mit C-Extension-Kompilierung:**
   ```
   error: command 'gcc' failed with exit status 1
   ```
   Lösung: Installieren Sie Entwicklungstools:
   ```bash
   sudo zypper install patterns-devel-base-devel_basis
   ```

4. **SSL-Zertifikat Probleme bei Verbindung zu vCenter:**
   Lösung: Verwenden Sie die Option `--ignore-ssl` bei der CLI-Version oder aktivieren Sie "SSL-Zertifikat ignorieren" in der GUI.

5. **Berechtigungsfehler:**
   ```
   PermissionError: [Errno 13] Permission denied: '/path/to/file'
   ```
   Lösung: Prüfen Sie die Berechtigungen und korrigieren Sie sie mit:
   ```bash
   chmod +x /path/to/file
   ```

6. **PyQt5-Probleme:**
   Wenn Sie Probleme mit PyQt5 haben, können Sie die Tkinter-Version (vsphere_reporter_linux.py) verwenden, die speziell für Linux-Distributionen wie OpenSuse Tumbleweed entwickelt wurde.

## Weitere Informationen

Für detailliertere Informationen schauen Sie bitte in die Dokumentationsdateien:
- `docs/admin_guide.md` - Installationsanleitung für Administratoren
- `docs/user_guide.md` - Benutzerhandbuch

Bei weiteren Fragen oder Problemen können Sie sich an Ihren Administrator wenden.