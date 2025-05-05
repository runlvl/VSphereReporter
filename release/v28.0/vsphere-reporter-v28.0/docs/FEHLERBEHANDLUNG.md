# Fehlerbehandlung und Diagnose für VMware vSphere Reporter v28.0

Dieses Dokument bietet Anleitungen zur Fehlerbehandlung und Diagnose bei häufig auftretenden Problemen mit dem VMware vSphere Reporter.

## Berichtgenerierungsfehler

### Problem: Report-Generator stürzt ab oder hängt

Der VMware vSphere Reporter v28.0 enthält ein verbessertes mehrstufiges Fallback-System für die Berichtgenerierung, das automatisch aktiviert wird, wenn der primäre Berichtsgenerator fehlschlägt.

#### Fehlerbehandlungsstufen:

1. **Primärer HTML-Exporter**: Versucht zuerst, einen vollständigen HTML-Bericht mit interaktiven Diagrammen zu erstellen
2. **Temporärer Speicherort-Fallback**: Wenn der Schreibzugriff auf das Berichtsverzeichnis fehlschlägt, wird versucht, in ein temporäres Verzeichnis zu schreiben
3. **Einfacher HTML-Exporter**: Wenn die komplexe HTML-Generierung fehlschlägt, wird ein einfacher HTML-Bericht ohne JavaScript-Abhängigkeiten generiert

#### Mögliche Ursachen:

- Unzureichende Berechtigungen für das Berichtsverzeichnis
- Fehler bei der Datenverarbeitung komplexer Topologiediagramme
- JavaScript-Fehler bei der Diagrammgenerierung

#### Lösungen:

1. Aktivieren Sie den Debug-Modus mit `VSPHERE_REPORTER_DEBUG=1`
2. Überprüfen Sie die Logs im Verzeichnis `logs/`
3. Stellen Sie sicher, dass ausreichend Speicherplatz verfügbar ist
4. Versuchen Sie, ein anderes Ausgabeverzeichnis zu verwenden

### Problem: Fehlende Daten in Berichten

#### Mögliche Ursachen:

- Unzureichende Berechtigungen für den vCenter-Benutzer
- Zeitüberschreitung bei der Datensammlung in großen Umgebungen
- Fehler beim Parsen bestimmter Datenstrukturen

#### Lösungen:

1. Verwenden Sie einen vCenter-Benutzer mit ausreichenden Berechtigungen (mindestens Read-Only)
2. Erhöhen Sie den Timeout-Wert in den Einstellungen
3. Überprüfen Sie die Protokolle auf spezifische Fehler bei der Datensammlung

## Verbindungsprobleme

### Problem: Verbindung zum vCenter fehlgeschlagen

#### Mögliche Ursachen:

- Falsche vCenter-Adresse oder Anmeldedaten
- Netzwerkprobleme oder Firewall-Einschränkungen
- SSL-Zertifikatsprobleme

#### Lösungen:

1. Überprüfen Sie die eingegebene vCenter-Adresse und Anmeldedaten
2. Aktivieren Sie die Option "SSL-Zertifikat ignorieren" bei selbst-signierten Zertifikaten
3. Überprüfen Sie die Netzwerkverbindung und Firewall-Regeln
4. Verwenden Sie `ping` oder `telnet`, um die Erreichbarkeit zu testen

### Problem: Zeitüberschreitung bei der Verbindung

#### Mögliche Ursachen:

- Langsame Netzwerkverbindung
- Hohe Auslastung des vCenter-Servers
- Zu viele gleichzeitige Anfragen

#### Lösungen:

1. Erhöhen Sie den Verbindungs-Timeout in den Einstellungen
2. Versuchen Sie die Verbindung zu einer Zeit mit geringerer vCenter-Last
3. Reduzieren Sie die Anzahl der zu sammelnden Datenpunkte

## VMDK-Erkennung

### Problem: Falsche Kennzeichnung von VMDKs als "potenziell verwaist"

#### Mögliche Ursachen:

- Spezielle Konfigurationen von VMs mit nicht-standard Pfadnamen
- VMDKs von Templates werden manchmal fälschlicherweise als verwaist erkannt
- Probleme mit der Groß-/Kleinschreibung in Dateipfaden

#### Lösungen:

1. Verwenden Sie die erweiterte VMDK-Ansicht, die alle VMDKs mit Statusinformationen anzeigt
2. Überprüfen Sie die "Erklärung"-Spalte für Details, warum eine VMDK als verwaist erkannt wurde
3. Bei falschen Erkennungen prüfen Sie, ob die VM aktiv ist und tatsächlich diese VMDK verwendet

## Speicherprobleme

### Problem: Hohe Speicherauslastung bei großen Umgebungen

#### Mögliche Ursachen:

- Sammlung großer Datenmengen aus umfangreichen vSphere-Umgebungen
- Topologie-Rendering mit vielen Knoten
- Ineffiziente Verarbeitung von vSphere-Objekten

#### Lösungen:

1. Begrenzen Sie die Datensammlung auf bestimmte Rechenzentren oder Cluster
2. Aktivieren Sie die inkrementelle Datensammlung für große Umgebungen
3. Schließen Sie bestimmte VM-Typen von der Datensammlung aus

## Installations- und Umgebungsprobleme

### Problem: Fehlende Bibliotheken oder Python-Module

#### Mögliche Ursachen:

- Unvollständige Installation der Abhängigkeiten
- Inkompatibilitäten zwischen Bibliotheken
- Falsche Python-Version

#### Lösungen:

1. Führen Sie `setup.bat` (Windows) oder `setup.sh` (Linux) erneut aus
2. Installieren Sie fehlende Abhängigkeiten manuell mit `pip install -r requirements.txt`
3. Überprüfen Sie, ob Python 3.8 oder höher verwendet wird

## Erweiterte Diagnose

### Aktivieren des Debug-Modus

Der Debug-Modus bietet detailliertere Protokollierung und kann bei der Diagnose komplexer Probleme helfen.

**Windows:**
```batch
set VSPHERE_REPORTER_DEBUG=1
run.bat
```

**Linux:**
```bash
VSPHERE_REPORTER_DEBUG=1 python vsphere_reporter.py
```

### Log-Dateien analysieren

Die wichtigsten Log-Dateien befinden sich im Verzeichnis `logs/`:

- `vsphere_debug_YYYYMMDD_HHMMSS.log`: Enthält detaillierte Debuginformationen
- `vsphere_error_YYYYMMDD_HHMMSS.log`: Enthält nur Fehlermeldungen
- `vsphere_reporter.log`: Enthält allgemeine Anwendungsprotokolle

### Fehlerberichte einreichen

Bei nicht lösbaren Problemen können Sie einen Fehlerbericht mit folgenden Informationen einreichen:

1. Genaue Versionsnummer des VMware vSphere Reporters
2. Beschreibung der Schritte zur Reproduktion des Problems
3. Log-Dateien aus dem `logs/`-Verzeichnis
4. Screenshots relevanter Fehlermeldungen
5. vCenter-Version und Umgebungsinformationen (Anzahl der VMs, Hosts, etc.)

### Wichtige Umgebungsvariablen

- `VSPHERE_REPORTER_DEBUG=1`: Aktiviert den Debug-Modus
- `VSPHERE_REPORTER_LOG_DIR=/pfad/zu/logs`: Ändert das Verzeichnis für Log-Dateien
- `VSPHERE_REPORTER_TIMEOUT=300`: Ändert den Timeout-Wert für vCenter-Anfragen (in Sekunden)
- `VSPHERE_REPORTER_MAX_THREADS=4`: Begrenzt die Anzahl paralleler Threads für die Datensammlung