# Erweiterte Topologie-Funktionen Guide

## Übersicht

Die Version 28.0 des VMware vSphere Reporters enthält erweiterte Topologie-Visualisierungsfunktionen, die es ermöglichen, die gesamte vSphere-Infrastruktur als interaktives hierarchisches Diagramm darzustellen. Diese Funktion gibt Administratoren und Entscheidungsträgern einen schnellen visuellen Überblick über die Strukturen der virtualisierten Umgebung.

## Funktionen der erweiterten Topologie-Visualisierung

### Hierarchische Darstellung

Die Topologie-Visualisierung stellt die gesamte vSphere-Infrastruktur als hierarchischen Baum dar:

1. **vCenter Server** - Die Wurzel des Baums, mit Version und Verbindungsinformationen
2. **Datacenters** - Die logischen Gruppierungen innerhalb des vCenters
3. **Cluster** - Mit Informationen zur Host- und VM-Anzahl
4. **Hosts** - Mit CPU- und Speicherdetails
5. **VMs** - Mit Status und Ressourcenverbrauch
6. **Datastores** - Mit Kapazitäts- und Auslastungsinformationen
7. **Netzwerke** - Mit Typ- und Nutzungsinformationen

### Farbkodierung und Symbole

Jeder Knotentyp in der Topologie wird durch ein eigenes Symbol und eine eigene Farbe dargestellt:

- **vCenter/Datacenter**: Rechteckig, Dunkelblau (Bechtle-Blau)
- **Cluster**: Raute, Orange (Bechtle-Orange)
- **Hosts**: Kreis, Grün (Bechtle-Grün)
- **VMs**: Leerer Kreis, Dunkelgrau
- **Templates**: Pin, Dunkelgrau
- **Datastores**: Rechteckig, Lila
- **Netzwerke**: Abgerundetes Rechteck, Türkis

Bei Datastores wird zusätzlich eine dynamische Färbung basierend auf der Speicherauslastung angewendet:
- **< 75% belegt**: Standard-Lila
- **75-90% belegt**: Orange
- **> 90% belegt**: Rot

### Interaktive Funktionen

Die Topologie-Visualisierung bietet verschiedene interaktive Funktionen:

1. **Expandieren/Kollabieren**: Klicken Sie auf einen Knoten, um seine untergeordneten Elemente ein- oder auszublenden.
2. **Zoomen und Verschieben**: Verwenden Sie das Mausrad zum Zoomen und ziehen Sie mit der Maus, um den sichtbaren Bereich zu verschieben.
3. **Tooltips**: Bewegen Sie den Mauszeiger über einen Knoten, um detaillierte Informationen anzuzeigen.
4. **Speichern als Bild**: Über die Werkzeugleiste können Sie das Diagramm als PNG- oder SVG-Datei exportieren.
5. **Datenansicht**: Zeigt die zugrunde liegenden Daten in tabellarischer Form an.

### Filterfunktionen

In Version 28.0 können Sie die Darstellung der Topologie nach verschiedenen Kriterien filtern:

1. **Komponententypen ein-/ausblenden**: 
   - VMs anzeigen/ausblenden
   - Datastores anzeigen/ausblenden
   - Netzwerke anzeigen/ausblenden

2. **Detailtiefe steuern**:
   - Maximalanzahl der angezeigten VMs pro Host beschränken
   - Maximalanzahl der angezeigten Datastores begrenzen

Diese Filter können über die Filteroptionen im HTML-Bericht oder über entsprechende Parameter in der API angewendet werden.

## Nutzung der Topologie in Berichten

### HTML-Berichte

In HTML-Berichten wird die Topologie-Visualisierung als erster Abschnitt vor den tabellarischen Daten angezeigt. Die interaktiven Funktionen stehen direkt im Bericht zur Verfügung.

### PDF-Berichte

In PDF-Berichten wird eine statische Version der Topologie als Bild eingebettet. Da PDF keine interaktiven Elemente unterstützt, wird hier ein optimierter Ausschnitt mit einer begrenzten Anzahl von Elementen dargestellt.

### DOCX-Berichte

Ähnlich wie bei PDF-Berichten wird in DOCX-Dokumenten eine statische Version der Topologie eingebettet.

## Technische Details

### Anforderungen

Die interaktive Topologie-Visualisierung basiert auf folgenden Technologien:

- **pyecharts**: Für die Generierung der interaktiven Diagramme
- **ECharts**: JavaScript-Bibliothek für interaktive Visualisierungen (wird automatisch eingebunden)
- **Moderner Webbrowser**: Für optimale Darstellung wird ein aktueller Browser empfohlen

### Performance-Hinweise

Die Topologie-Visualisierung ist für folgende Umgebungsgrößen optimiert:

- **Klein (< 100 VMs)**: Vollständige Darstellung aller Komponenten
- **Mittel (100-500 VMs)**: Standardmäßig werden pro Host maximal 10 VMs angezeigt
- **Groß (> 500 VMs)**: Es werden nur die wichtigsten Komponenten angezeigt, mit reduzierten Details

Bei besonders großen Umgebungen (> 1000 VMs) kann die Darstellung langsamer werden. In diesem Fall empfiehlt es sich, die Filter zu nutzen, um nur bestimmte Teile der Infrastruktur anzuzeigen.

## Beispiele und Anwendungsfälle

### Infrastrukturübersicht

Die Topologie-Visualisierung eignet sich hervorragend, um einen schnellen Überblick über die gesamte vSphere-Umgebung zu erhalten. Sie können sofort erkennen:

- Wie viele Cluster vorhanden sind
- Wie Hosts auf Cluster verteilt sind
- Wie VMs auf Hosts verteilt sind
- Welche Datastores zur Verfügung stehen

### Ressourcenplanung

Mithilfe der farblichen Hervorhebung können Sie schnell kritische Ressourcen identifizieren:

- Datastores mit hoher Auslastung
- Ungleichmäßige Verteilung von VMs auf Hosts
- Überblick über die Gesamtkapazität

### Dokumentation

Durch den Export als Bild können Sie die Topologie leicht in Präsentationen oder andere Dokumente einbinden, um die Infrastruktur zu dokumentieren oder in Besprechungen zu präsentieren.

## Fehlerbehebung

### Topologie wird nicht angezeigt

Wenn die Topologie-Visualisierung nicht angezeigt wird, prüfen Sie folgende Punkte:

1. **Browser aktualisieren**: Stellen Sie sicher, dass Ihr Browser aktuell ist und JavaScript aktiviert ist.
2. **Internet-Verbindung**: Die Visualisierung lädt einige Ressourcen von CDN-Servern.
3. **Datenmenge**: Bei sehr großen Umgebungen kann es zu Verzögerungen kommen.

### Falsche Darstellung

Wenn die Topologie falsch oder unvollständig erscheint:

1. **Datensammlung überprüfen**: Stellen Sie sicher, dass die Datensammlung erfolgreich war.
2. **Berechtigungen prüfen**: Der vCenter-Benutzer benötigt ausreichende Berechtigungen.
3. **Logs prüfen**: Im Debug-Modus werden detaillierte Informationen protokolliert.

## Zusammenfassung

Die erweiterte Topologie-Visualisierung in Version 28.0 bietet eine leistungsstarke Möglichkeit, die vSphere-Infrastruktur auf einen Blick zu erfassen. Durch die interaktiven Elemente und Filterfunktionen können Sie genau die Informationen anzeigen, die für Ihre aktuelle Aufgabe relevant sind.