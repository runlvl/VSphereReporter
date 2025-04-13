# VMware vSphere Reporter - Installationsanleitung für OpenSuse Tumbleweed

## Überblick

Diese Anleitung erklärt, wie Sie den VMware vSphere Reporter auf Ihrem OpenSuse Tumbleweed-System installieren und einrichten.

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
   chmod +x setup.sh
   ./setup.sh
   ```

4. Überprüfen Sie, ob das Installationsskript erfolgreich ausgeführt wurde.

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