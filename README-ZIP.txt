# VMware vSphere Reporter - Windows-Version
## ZIP-Archiv für Windows-Benutzer

Dieses ZIP-Archiv wurde speziell für Windows-Benutzer erstellt, um Probleme bei der Extraktion von TAR.GZ-Archiven zu vermeiden.

### Hinweise zur Installation unter Windows:

1. Entpacken Sie das ZIP-Archiv in einen beliebigen Ordner
2. Führen Sie die Datei `setup.bat` aus, um die Abhängigkeiten zu installieren
3. Nach erfolgreicher Installation führen Sie die Anwendung mit `run.bat` aus

### Verbesserungen in Version 8:

- Umfassende Erkennung verschiedener Python-Installationen unter Windows
- Automatische Suche nach Python in allen üblichen Installationspfaden
- Unterstützung für Windows Store Python-Installationen
- Fallback-Mechanismus für die Installation von Abhängigkeiten, falls die Anforderungsdatei fehlt
- Bessere Fehlerbehandlung und informative Fehlermeldungen

### Bei Problemen:

Falls bei der Installation der Python-Abhängigkeiten Probleme auftreten, versuchen Sie folgende Schritte:

1. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist
2. Führen Sie die Installation manuell durch:
   ```
   pip install pyVmomi PyQt5 reportlab python-docx jinja2 humanize six requests
   ```
3. Überprüfen Sie, ob die Abhängigkeiten erfolgreich installiert wurden
4. Starten Sie die Anwendung mit `run.bat`

Bei weiteren Fragen wenden Sie sich an Ihren Bechtle-Ansprechpartner.