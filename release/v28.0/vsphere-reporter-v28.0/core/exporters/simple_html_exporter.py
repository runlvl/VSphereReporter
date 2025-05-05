#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Einfacher HTML-Exporter für vSphere-Reports
Fallback-Lösung bei Problemen mit dem komplexen HTML-Exporter
"""

import os
import datetime
import logging

logger = logging.getLogger(__name__)

class SimpleHTMLExporter:
    """Einfacher HTML-Exporter ohne externe Abhängigkeiten"""
    
    def __init__(self, data, timestamp):
        """
        Initialisiert den einfachen HTML-Exporter
        
        Args:
            data (dict): Gesammelte vSphere-Daten
            timestamp (datetime): Zeitstempel für den Bericht
        """
        self.data = data or {}
        self.timestamp = timestamp or datetime.datetime.now()
    
    def export(self, output_path):
        """
        Exportiert die Daten in eine einfache HTML-Datei
        
        Args:
            output_path (str): Pfad für die HTML-Ausgabe
            
        Returns:
            bool: True bei Erfolg
        """
        try:
            # Erstelle das Verzeichnis, falls es noch nicht existiert
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Generiere den HTML-Inhalt
            html_content = self._generate_html()
            
            # Schreibe die HTML-Datei
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"Einfacher HTML-Bericht erfolgreich exportiert nach: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Exportieren des einfachen HTML-Berichts: {str(e)}")
            raise
    
    def _generate_html(self):
        """
        Generiert den HTML-Code für den Bericht
        
        Returns:
            str: HTML-Code
        """
        # Einfacher HTML-Header
        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VMware vSphere Bericht - {self.timestamp.strftime('%d.%m.%Y')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
        }}
        
        h1, h2, h3 {{
            color: #00355e;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background-color: #00355e;
            color: white;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .section {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        th {{
            background-color: #00355e;
            color: white;
            text-align: left;
            padding: 10px;
        }}
        
        td {{
            padding: 8px 10px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        
        .footer {{
            margin-top: 50px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
            text-align: center;
            color: #777;
        }}
        
        .warning {{
            color: #da6f1e;
            font-weight: bold;
        }}
        
        .critical {{
            color: red;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VMware vSphere Umgebungsbericht</h1>
            <p>Generiert am {self.timestamp.strftime('%d.%m.%Y um %H:%M')} Uhr</p>
        </div>
"""
        
        # VMware Tools Section
        html += self._generate_vmware_tools_section()
        
        # Snapshots Section
        html += self._generate_snapshots_section()
        
        # Orphaned VMDKs Section
        html += self._generate_orphaned_vmdks_section()
        
        # Optional Sections
        if 'vms' in self.data:
            html += self._generate_vms_section()
            
        if 'hosts' in self.data:
            html += self._generate_hosts_section()
            
        if 'datastores' in self.data:
            html += self._generate_datastores_section()
        
        # Footer
        html += """
        <div class="footer">
            <p>VMware vSphere Reporter v28.0</p>
            <p>&copy; 2025 Bechtle GmbH. Alle Rechte vorbehalten.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _format_size(self, size_bytes):
        """Formatiert Bytes in menschenlesbare Größe"""
        if not size_bytes:
            return "0 B"
            
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{round(size, 2)} {units[unit_index]}"
    
    def _generate_vmware_tools_section(self):
        """Erzeugt den HTML-Code für den VMware Tools-Abschnitt"""
        html = """
        <div class="section">
            <h2>VMware Tools Versionen</h2>
            <p>VMware Tools Versionen aller virtuellen Maschinen, sortiert nach ältester Version zuerst.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>VM Name</th>
                        <th>VMware Tools Version</th>
                        <th>Status</th>
                        <th>VM Version</th>
                        <th>Betriebssystem</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Füge die VMware Tools-Daten ein
        for vm in self.data.get('vmware_tools', []):
            html += f"""
                    <tr>
                        <td>{vm.get('name', '-')}</td>
                        <td>{vm.get('tools_version', '-')}</td>
                        <td>{vm.get('tools_status', '-')}</td>
                        <td>{vm.get('vm_version', '-')}</td>
                        <td>{vm.get('guest_full_name', '-')}</td>
                    </tr>
"""
        
        # Wenn keine Daten vorhanden sind
        if not self.data.get('vmware_tools', []):
            html += """
                    <tr>
                        <td colspan="5">Keine VMware Tools Daten verfügbar</td>
                    </tr>
"""
            
        html += """
                </tbody>
            </table>
        </div>
"""
        
        return html
    
    def _generate_snapshots_section(self):
        """Erzeugt den HTML-Code für den Snapshots-Abschnitt"""
        html = """
        <div class="section">
            <h2>VM Snapshots</h2>
            <p>Snapshots aller virtuellen Maschinen, sortiert nach ältesten zuerst.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>VM Name</th>
                        <th>Snapshot Name</th>
                        <th>Erstellungsdatum</th>
                        <th>Alter (Tage)</th>
                        <th>Beschreibung</th>
                        <th>Größe</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Füge die Snapshot-Daten ein
        for snapshot in self.data.get('snapshots', []):
            # Bestimme die CSS-Klasse basierend auf dem Alter
            age_class = ""
            age_days = snapshot.get('age_days', 0)
            if age_days > 30:
                age_class = "critical"
            elif age_days > 14:
                age_class = "warning"
                
            # Formatiere das Erstellungsdatum
            create_time = snapshot.get('create_time', '-')
            if isinstance(create_time, datetime.datetime):
                create_time = create_time.strftime('%Y-%m-%d %H:%M:%S')
                
            # Formatiere die Größe
            size_mb = snapshot.get('size_mb', 0)
            if size_mb:
                size_display = self._format_size(size_mb * 1024 * 1024)
            else:
                size_display = '-'
                
            html += f"""
                    <tr>
                        <td>{snapshot.get('vm_name', '-')}</td>
                        <td>{snapshot.get('name', '-')}</td>
                        <td>{create_time}</td>
                        <td class="{age_class}">{age_days}</td>
                        <td>{snapshot.get('description', '-')}</td>
                        <td>{size_display}</td>
                    </tr>
"""
        
        # Wenn keine Daten vorhanden sind
        if not self.data.get('snapshots', []):
            html += """
                    <tr>
                        <td colspan="6">Keine Snapshot-Daten verfügbar</td>
                    </tr>
"""
            
        html += """
                </tbody>
            </table>
        </div>
"""
        
        return html
    
    def _generate_orphaned_vmdks_section(self):
        """Erzeugt den HTML-Code für den VMDK-Abschnitt"""
        html = """
        <div class="section">
            <h2>VMDK-Dateien</h2>
            <p>Übersicht aller VMDK-Dateien in der Umgebung mit Status und Zuordnungsinformationen.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>VM</th>
                        <th>Datastore</th>
                        <th>Pfad</th>
                        <th>Größe</th>
                        <th>Letzte Änderung</th>
                        <th>Erklärung</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Füge die VMDK-Daten ein
        for vmdk in self.data.get('orphaned_vmdks', []):
            # Bestimme die CSS-Klasse basierend auf dem Status
            status_class = ""
            status = vmdk.get('status', '')
            if 'AKTIV' in status:
                status_class = "active"
            elif 'TEMPLATE' in status:
                status_class = "template"
            elif 'VERWAIST' in status:
                status_class = "warning"
                
            # Formatiere das Änderungsdatum
            mod_time = vmdk.get('modification_time', '-')
            if isinstance(mod_time, datetime.datetime):
                mod_time = mod_time.strftime('%Y-%m-%d %H:%M:%S')
                
            # Formatiere die Größe
            size_mb = vmdk.get('size_mb', 0)
            if size_mb:
                size_display = self._format_size(size_mb * 1024 * 1024)
            else:
                size_display = '-'
                
            html += f"""
                    <tr>
                        <td class="{status_class}">{status}</td>
                        <td>{vmdk.get('vm', '-')}</td>
                        <td>{vmdk.get('datastore', '-')}</td>
                        <td>{vmdk.get('path', '-')}</td>
                        <td>{size_display}</td>
                        <td>{mod_time}</td>
                        <td>{vmdk.get('explanation', '-')}</td>
                    </tr>
"""
        
        # Wenn keine Daten vorhanden sind
        if not self.data.get('orphaned_vmdks', []):
            html += """
                    <tr>
                        <td colspan="7">Keine VMDK-Daten verfügbar</td>
                    </tr>
"""
            
        html += """
                </tbody>
            </table>
        </div>
"""
        
        return html
    
    def _generate_vms_section(self):
        """Erzeugt den HTML-Code für den VMs-Abschnitt"""
        html = """
        <div class="section">
            <h2>Virtuelle Maschinen</h2>
            <p>Übersicht aller virtuellen Maschinen in der Umgebung.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>vCPUs</th>
                        <th>RAM (MB)</th>
                        <th>Host</th>
                        <th>Betriebssystem</th>
                        <th>IP-Adresse</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Füge die VM-Daten ein
        for vm in self.data.get('vms', []):
            html += f"""
                    <tr>
                        <td>{vm.get('name', '-')}</td>
                        <td>{vm.get('status', '-')}</td>
                        <td>{vm.get('cpu', '-')}</td>
                        <td>{vm.get('memory_mb', '-')}</td>
                        <td>{vm.get('host', '-')}</td>
                        <td>{vm.get('guest_full_name', '-')}</td>
                        <td>{vm.get('ip_address', '-')}</td>
                    </tr>
"""
        
        # Wenn keine Daten vorhanden sind
        if not self.data.get('vms', []):
            html += """
                    <tr>
                        <td colspan="7">Keine VM-Daten verfügbar</td>
                    </tr>
"""
            
        html += """
                </tbody>
            </table>
        </div>
"""
        
        return html
    
    def _generate_hosts_section(self):
        """Erzeugt den HTML-Code für den Hosts-Abschnitt"""
        html = """
        <div class="section">
            <h2>ESXi Hosts</h2>
            <p>Übersicht aller ESXi Hosts in der Umgebung.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Version</th>
                        <th>CPU Modell</th>
                        <th>CPU Kerne</th>
                        <th>RAM</th>
                        <th>Cluster</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Füge die Host-Daten ein
        for host in self.data.get('hosts', []):
            # Formatiere die RAM-Größe
            memory_size = host.get('memory_size', 0)
            memory_display = self._format_size(memory_size) if memory_size else '-'
                
            html += f"""
                    <tr>
                        <td>{host.get('name', '-')}</td>
                        <td>{host.get('status', '-')}</td>
                        <td>{host.get('version', '-')}</td>
                        <td>{host.get('cpu_model', '-')}</td>
                        <td>{host.get('cpu_cores', '-')}</td>
                        <td>{memory_display}</td>
                        <td>{host.get('cluster', '-')}</td>
                    </tr>
"""
        
        # Wenn keine Daten vorhanden sind
        if not self.data.get('hosts', []):
            html += """
                    <tr>
                        <td colspan="7">Keine Host-Daten verfügbar</td>
                    </tr>
"""
            
        html += """
                </tbody>
            </table>
        </div>
"""
        
        return html
    
    def _generate_datastores_section(self):
        """Erzeugt den HTML-Code für den Datastores-Abschnitt"""
        html = """
        <div class="section">
            <h2>Datastores</h2>
            <p>Übersicht aller Datastores in der Umgebung.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Typ</th>
                        <th>Kapazität</th>
                        <th>Freier Speicher</th>
                        <th>Auslastung</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Füge die Datastore-Daten ein
        for ds in self.data.get('datastores', []):
            # Berechne die Auslastung
            capacity = ds.get('capacity', 0)
            free_space = ds.get('free_space', 0)
            usage_percent = ((capacity - free_space) / capacity * 100) if capacity > 0 else 0
            
            # Bestimme die CSS-Klasse basierend auf der Auslastung
            usage_class = ""
            if usage_percent > 90:
                usage_class = "critical"
            elif usage_percent > 75:
                usage_class = "warning"
                
            # Formatiere die Größen
            capacity_display = self._format_size(capacity) if capacity else '-'
            free_space_display = self._format_size(free_space) if free_space else '-'
                
            html += f"""
                    <tr>
                        <td>{ds.get('name', '-')}</td>
                        <td>{ds.get('type', '-')}</td>
                        <td>{capacity_display}</td>
                        <td>{free_space_display}</td>
                        <td class="{usage_class}">{usage_percent:.2f}%</td>
                    </tr>
"""
        
        # Wenn keine Daten vorhanden sind
        if not self.data.get('datastores', []):
            html += """
                    <tr>
                        <td colspan="5">Keine Datastore-Daten verfügbar</td>
                    </tr>
"""
            
        html += """
                </tbody>
            </table>
        </div>
"""
        
        return html