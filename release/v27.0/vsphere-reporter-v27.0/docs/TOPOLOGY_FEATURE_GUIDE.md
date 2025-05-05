# VMware vSphere Reporter - Topologie-Visualisierung

Mit der Version 27.0 des VMware vSphere Reporters wurde eine interaktive Topologie-Visualisierung eingeführt, die Ihnen einen schnellen Überblick über die Struktur Ihrer virtuellen Umgebung bietet.

## Überblick

Die Topologie-Visualisierung stellt die hierarchische Struktur Ihrer vSphere-Umgebung grafisch dar. Sie zeigt:

- vCenter Server als Wurzel
- Datacenter
- Cluster
- ESXi-Hosts
- Virtuelle Maschinen
- Datastores
- Netzwerke
- Resource Pools

Die Darstellung ermöglicht es Ihnen, schnell Beziehungen zwischen den verschiedenen Komponenten zu erkennen und die Gesamtstruktur der Umgebung zu verstehen.

## Interaktive Funktionen

Die Topologie-Visualisierung ist vollständig interaktiv:

1. **Ein-/Ausklappen**: Klicken Sie auf einen Knoten, um dessen Unterelemente ein- oder auszuklappen.
2. **Details anzeigen**: Bewegen Sie den Mauszeiger über einen Knoten, um detaillierte Informationen anzuzeigen.
3. **Zoom**: Verwenden Sie das Mausrad oder die Zoomsteuerung, um in die Visualisierung hinein- oder hinauszuzoomen.
4. **Verschieben**: Klicken und ziehen Sie, um den sichtbaren Ausschnitt zu verschieben.

## Farbcodierung und Symbolik

Die verschiedenen Komponententypen werden durch unterschiedliche Formen und Farben dargestellt:

- **vCenter Server**: Rechteck (dunkelblau)
- **Datacenter**: Abgerundetes Rechteck (dunkelblau)
- **Cluster**: Raute (orange)
- **ESXi-Host**: Kreis (grün)
- **VM**: Leerer Kreis (dunkelgrau)
- **Template**: Pin-Symbol (dunkelgrau)
- **Datastore**: Rechteck (lila)
- **Netzwerk**: Abgerundetes Rechteck (türkis)
- **Resource Pool**: Dreieck (koralle)

## Vorteile der Topologie-Visualisierung

- **Schneller Überblick**: Verstehen Sie auf einen Blick die Struktur Ihrer vSphere-Umgebung.
- **Einfache Navigation**: Navigieren Sie intuitiv durch die verschiedenen Ebenen Ihrer Infrastruktur.
- **Problemidentifikation**: Erkennen Sie schnell ungewöhnliche Strukturen oder Ungleichgewichte in der Verteilung.
- **Dokumentation**: Nutzen Sie die Visualisierung für Präsentationen oder Dokumentationszwecke.

## Tipps zur Verwendung

- Die Topologie-Visualisierung zeigt standardmäßig die ersten zwei Ebenen an. Tiefere Ebenen können durch Klicken auf die entsprechenden Knoten angezeigt werden.
- Bei großen Umgebungen werden nur eine begrenzte Anzahl von VMs pro Host angezeigt (standardmäßig 10), um die Übersichtlichkeit zu wahren.
- Die Visualisierung ist so optimiert, dass sie auch in exportierten Berichten (HTML) funktioniert und interaktiv bleibt.

## Technische Hinweise

Die Topologie-Visualisierung verwendet die JavaScript-Bibliothek ECharts (über PyECharts) und funktioniert in allen modernen Webbrowsern. Für die beste Erfahrung empfehlen wir Google Chrome oder Microsoft Edge in der neuesten Version.

---

Copyright © 2025 Bechtle GmbH