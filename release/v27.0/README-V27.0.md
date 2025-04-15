# VMware vSphere Reporter v27.0

## Neuer Ansatz zur VMDK-Berichterstattung

Die Version 27.0 des VMware vSphere Reporters führt einen grundlegend neuen Ansatz zur VMDK-Berichterstattung ein. Anstatt nur "verwaiste" VMDK-Dateien zu identifizieren, zeigt der Reporter jetzt **ALLE** VMDK-Dateien in der Umgebung an, mit einer deutlichen Kennzeichnung jener Dateien, die potentiell verwaist sein könnten.

### Hauptmerkmale

- **Komplette VMDK-Übersicht**: Alle VMDKs werden angezeigt, nicht nur potenziell verwaiste
- **Status-Indikatoren**: Jede VMDK wird mit einem Status versehen:
  - `AKTIV`: In Verwendung durch eine VM
  - `TEMPLATE`: Teil eines VM-Templates
  - `POTENTIALLY ORPHANED`: Möglicherweise verwaist und sollte überprüft werden
- **Farbkodierung**: Intuitive visuelle Unterscheidung zwischen den verschiedenen VMDK-Typen
- **Detaillierte Erklärungen**: Verbesserte Beschreibungen, warum eine VMDK als potenziell verwaist eingestuft wurde

### Vorteile des neuen Ansatzes

1. **Bessere Entscheidungsgrundlage**: Administratoren sehen alle VMDKs und können fundierte Entscheidungen treffen
2. **Reduziertes Risiko**: Verhindert versehentliches Löschen wichtiger Dateien
3. **Verbesserte Ressourcenverwaltung**: Ermöglicht einen Überblick über alle VMDK-Ressourcen
4. **Höhere Genauigkeit**: Der VM-zentrierte Ansatz mit Datastore-Durchsuchung bietet präzisere Ergebnisse

### Technische Verbesserungen

- Multiple Pfadvergleiche für bessere Treffersicherheit
- Verbesserte Template-VM-Handhabung
- Erkennung von Helper-VMDK-Dateien
- Bessere Erkennung temporärer VMDKs durch Namensmusteranalyse

## Installation

### Windows

1. Laden Sie das neueste Windows-Paket herunter: `vsphere-reporter-windows-v27.0.zip`
2. Entpacken Sie das Paket in ein Verzeichnis Ihrer Wahl
3. Starten Sie die Anwendung über `vsphere_reporter.py` oder die erstellte Verknüpfung

### Linux

1. Laden Sie das neueste Linux-Paket herunter: `vsphere-reporter-linux-v27.0.tar.gz`
2. Entpacken Sie das Archiv: `tar -xzvf vsphere-reporter-linux-v27.0.tar.gz`
3. Wechseln Sie in das Verzeichnis: `cd vsphere-reporter-v27.0`
4. Führen Sie das Programm aus: `python vsphere_reporter.py`

## Kontakt

Bei Fragen, Feedback oder Problemen wenden Sie sich bitte an das Bechtle Cloud Solutions Team.

---

© 2025 Bechtle GmbH. Alle Rechte vorbehalten.