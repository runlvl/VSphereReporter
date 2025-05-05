#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Erweiterter Topologie-Generator (v28.0)

Dieses Modul generiert eine visuelle Darstellung der vSphere-Umgebungsstruktur
als interaktives Diagramm für den HTML-Report mit erweiterten Funktionen.
"""

import logging
import os
import base64
from datetime import datetime
from pyecharts import options as opts
from pyecharts.charts import Tree, Page
from pyecharts.globals import CurrentConfig, ThemeType
from pyecharts.render.engine import RenderEngine

# Bechtle-Farben
BECHTLE_COLORS = {
    'dark_blue': '#00355e',
    'orange': '#da6f1e',
    'green': '#23a96a',
    'light_gray': '#f3f3f3',
    'dark_gray': '#5a5a5a'
}

# Node-Typen mit Icons und Farben
NODE_TYPES = {
    'vcenter': {'symbol': 'rect', 'color': BECHTLE_COLORS['dark_blue'], 'name': 'vCenter'},
    'datacenter': {'symbol': 'roundRect', 'color': BECHTLE_COLORS['dark_blue'], 'name': 'Datacenter'},
    'cluster': {'symbol': 'diamond', 'color': BECHTLE_COLORS['orange'], 'name': 'Cluster'},
    'host': {'symbol': 'circle', 'color': BECHTLE_COLORS['green'], 'name': 'Host'},
    'vm': {'symbol': 'emptyCircle', 'color': BECHTLE_COLORS['dark_gray'], 'name': 'VM'},
    'template': {'symbol': 'pin', 'color': BECHTLE_COLORS['dark_gray'], 'name': 'Template'},
    'datastore': {'symbol': 'rect', 'color': '#6a5acd', 'name': 'Datastore'},
    'network': {'symbol': 'roundRect', 'color': '#008b8b', 'name': 'Netzwerk'},
    'resource_pool': {'symbol': 'triangle', 'color': '#ff7f50', 'name': 'Resource Pool'}
}

class TopologyGenerator:
    """Generiert interaktive Topologie-Diagramme der vSphere-Umgebung mit erweiterten Funktionen"""
    
    def __init__(self):
        """Initialisiert den Topologie-Generator"""
        self.logger = logging.getLogger(__name__)
        self.nodes_data = []
        CurrentConfig.ONLINE_HOST = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/"
    
    def create_topology_tree(self, vsphere_data, filter_options=None):
        """
        Erstellt ein hierarchisches Baum-Diagramm der vSphere-Umgebung mit Filtermöglichkeiten
        
        Args:
            vsphere_data: Gesammeltes vSphere-Daten-Dictionary
            filter_options: Dictionary mit Filtermöglichkeiten (z.B. {'show_vms': True, 'show_datastores': True})

        Returns:
            str: HTML-Code mit dem eingebetteten Diagramm
        """
        try:
            # Standardwerte für Filter-Optionen
            if filter_options is None:
                filter_options = {
                    'show_vms': True, 
                    'show_datastores': True, 
                    'show_networks': True,
                    'max_vms_per_host': 10,
                    'max_datastores': 15
                }
            
            # Hierarchische Datenstruktur erstellen
            vcenter_node = self._build_topology_tree(vsphere_data, filter_options)
            
            # Tree-Diagramm initialisieren
            tree = (
                Tree(init_opts=opts.InitOpts(
                    width="100%", 
                    height="600px",
                    bg_color="#ffffff",
                    animation_opts=opts.AnimationOpts(animation=True),
                    theme=ThemeType.LIGHT
                ))
                .add(
                    series_name="VMware vSphere Topologie",
                    data=[vcenter_node],
                    pos_top="5%",
                    pos_bottom="5%",
                    layout="orthogonal",  # orthogonal für horizontale Darstellung
                    orient="LR",  # Links nach Rechts
                    initial_tree_depth=2,  # Zeige zwei Ebenen initial an
                    label_opts=opts.LabelOpts(
                        position="right",
                        color="#000000",
                        font_size=12,
                        font_family="Arial"
                    ),
                    leaves_label_opts=opts.LabelOpts(
                        position="right",
                        color="#000000",
                        font_size=12,
                        font_family="Arial"
                    ),
                    symbol_size=20,
                    is_roam=True,  # Erlaube Zoom und Pan
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title="VMware vSphere Infrastruktur",
                        subtitle=f"Interaktive Übersicht der virtuellen Umgebung (Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')})",
                        title_textstyle_opts=opts.TextStyleOpts(
                            color=BECHTLE_COLORS['dark_blue'],
                            font_size=20
                        ),
                        subtitle_textstyle_opts=opts.TextStyleOpts(
                            color=BECHTLE_COLORS['dark_gray'],
                            font_size=14
                        )
                    ),
                    tooltip_opts=opts.TooltipOpts(
                        trigger="item", 
                        formatter="{b}: {c}"
                    ),
                    legend_opts=opts.LegendOpts(
                        is_show=True,
                        pos_top="bottom",
                        orient="horizontal",
                        item_width=25,
                        item_height=14
                    ),
                    # Erweitertes Tool-Menu für Export-Funktionen
                    toolbox_opts=opts.ToolboxOpts(
                        is_show=True,
                        orient="vertical",
                        pos_left="right",
                        pos_top="center",
                        feature={
                            "saveAsImage": {"title": "Als Bild speichern", "name": "vsphere_topology"},
                            "restore": {"title": "Zurücksetzen"},
                            "dataView": {"title": "Daten anzeigen", "lang": ["Datenansicht", "Schließen", "Aktualisieren"]},
                            "dataZoom": {"title": {"zoom": "Vergrößern", "back": "Zurücksetzen"}},
                        }
                    )
                )
            )
            
            # Legende für die Knotentypen erstellen
            legend_items = []
            for node_type, props in NODE_TYPES.items():
                legend_items.append({
                    'name': props['name'],
                    'icon': props['symbol'],
                    'itemStyle': {'color': props['color']}
                })
                
            tree.options['legend'][0]['data'] = legend_items
            
            # Rendere das HTML
            self.logger.info("Topologie-Diagramm erfolgreich generiert")
            return tree.render_embed()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Generieren des Topologie-Diagramms: {str(e)}", exc_info=True)
            return "<div class='alert alert-warning'><p>Die Topologieübersicht konnte nicht generiert werden: " + str(e) + "</p></div>"
    
    def export_topology_as_image(self, vsphere_data, output_path, image_format="png"):
        """
        Exportiert das Topologie-Diagramm als statisches Bild (für PDF/DOCX-Berichte)
        
        Args:
            vsphere_data: Gesammeltes vSphere-Daten-Dictionary
            output_path: Pfad für die Ausgabedatei
            image_format: Format des Bildes ("png" oder "svg")
            
        Returns:
            bool: True bei Erfolg, False sonst
        """
        try:
            # Hierarchische Datenstruktur erstellen
            vcenter_node = self._build_topology_tree(vsphere_data, {
                'show_vms': True,
                'show_datastores': True,
                'show_networks': True,
                'max_vms_per_host': 5,  # Reduzierte Anzahl VMs für statische Bilder
                'max_datastores': 10
            })
            
            # Tree-Diagramm initialisieren
            tree = (
                Tree(init_opts=opts.InitOpts(
                    width="1200px", 
                    height="800px",
                    bg_color="#ffffff"
                ))
                .add(
                    series_name="VMware vSphere Topologie",
                    data=[vcenter_node],
                    layout="orthogonal",
                    orient="LR",
                    initial_tree_depth=3,
                    symbol_size=20,
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title="VMware vSphere Infrastruktur",
                        subtitle=f"Generiert am {datetime.now().strftime('%d.%m.%Y')}"
                    )
                )
            )
            
            # Temporäre HTML-Datei für das Rendering
            temp_html_path = output_path + ".temp.html"
            tree.render(temp_html_path)
            
            # Konvertierung zu Bild (benötigt phantomjs oder wkhtmltoimage)
            # Diese Funktion ist ein Platzhalter und muss je nach System angepasst werden
            success = False
            if image_format.lower() == "png":
                # Beispiel für PNG-Export mit wkhtmltoimage
                import subprocess
                cmd = ["wkhtmltoimage", "--quality", "90", temp_html_path, output_path]
                subprocess.run(cmd, check=True)
                success = os.path.exists(output_path)
            elif image_format.lower() == "svg":
                # SVG erfordert eine spezielle Behandlung
                # Hier könnte eine Konvertierung mit svglib, librsvg oder ähnlichem erfolgen
                pass
            
            # Temporäre Datei entfernen
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)
                
            return success
            
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren des Topologie-Diagramms: {str(e)}", exc_info=True)
            return False
    
    def _build_topology_tree(self, vsphere_data, filter_options):
        """
        Baut die hierarchische Baumstruktur für die Topologiedarstellung auf
        
        Args:
            vsphere_data: Dictionary mit vSphere-Daten
            filter_options: Dictionary mit Filteroptionen

        Returns:
            dict: Hierarchische Datenstruktur für den Tree-Chart
        """
        # vCenter als Wurzel
        vcenter_name = vsphere_data.get('vcenter_info', {}).get('server', 'vCenter Server')
        vcenter_version = vsphere_data.get('vcenter_info', {}).get('version', 'N/A')
        
        vcenter_node = {
            'name': vcenter_name,
            'value': f"vCenter Server {vcenter_version}",
            'symbol': NODE_TYPES['vcenter']['symbol'],
            'symbolSize': 30,
            'itemStyle': {'color': NODE_TYPES['vcenter']['color']},
            'children': []
        }

        # Datacenters hinzufügen
        datacenters = vsphere_data.get('datacenters', [])
        clusters = vsphere_data.get('clusters', [])
        hosts = vsphere_data.get('hosts', [])
        vms = vsphere_data.get('vms', [])
        datastores = vsphere_data.get('datastores', [])
        networks = vsphere_data.get('networks', [])
        resource_pools = vsphere_data.get('resource_pools', [])
        
        # Maximalwerte für Anzeige
        max_vms_per_host = filter_options.get('max_vms_per_host', 10)
        max_datastores = filter_options.get('max_datastores', 15)
        
        # Wenn keine expliziten Datacenter-Daten vorhanden, erzeugen wir ein virtuelles
        if not datacenters:
            default_dc = {
                'name': 'Default Datacenter',
                'symbol': NODE_TYPES['datacenter']['symbol'],
                'symbolSize': 25,
                'itemStyle': {'color': NODE_TYPES['datacenter']['color']},
                'children': []
            }
            vcenter_node['children'].append(default_dc)
            
            # Cluster direkt unter Default-Datacenter
            for cluster in clusters:
                cluster_node = {
                    'name': cluster.get('name', 'Unbekannter Cluster'),
                    'value': f"{cluster.get('host_count', 0)} Hosts, {cluster.get('vm_count', 0)} VMs",
                    'symbol': NODE_TYPES['cluster']['symbol'],
                    'symbolSize': 20,
                    'itemStyle': {'color': NODE_TYPES['cluster']['color']},
                    'children': []
                }
                default_dc['children'].append(cluster_node)
                
                # Hosts im Cluster
                cluster_hosts = [h for h in hosts if h.get('cluster') == cluster.get('name')]
                for host in cluster_hosts:
                    host_node = {
                        'name': host.get('name', 'Unbekannter Host'),
                        'value': f"{host.get('cpu_cores', 0)} Cores, {self._format_size(host.get('memory_size', 0))} RAM",
                        'symbol': NODE_TYPES['host']['symbol'],
                        'symbolSize': 15,
                        'itemStyle': {'color': NODE_TYPES['host']['color']},
                        'children': []
                    }
                    cluster_node['children'].append(host_node)
                    
                    # VMs auf dem Host
                    if filter_options.get('show_vms', True):
                        host_vms = [v for v in vms if v.get('host') == host.get('name')]
                        for vm in host_vms[:max_vms_per_host]:
                            # Unterscheide zwischen normalen VMs und Templates
                            is_template = vm.get('is_template', False)
                            vm_node = {
                                'name': vm.get('name', 'Unbekannte VM'),
                                'value': f"{vm.get('cpu', 0)} vCPUs, {vm.get('memory_mb', 0)} MB RAM, {vm.get('status', 'Unbekannt')}",
                                'symbol': NODE_TYPES['template']['symbol'] if is_template else NODE_TYPES['vm']['symbol'],
                                'symbolSize': 10,
                                'itemStyle': {'color': NODE_TYPES['template']['color'] if is_template else NODE_TYPES['vm']['color']}
                            }
                            host_node['children'].append(vm_node)
                        
                        # ... evtl mehr anzeigen
                        if len(host_vms) > max_vms_per_host:
                            more_node = {
                                'name': f"... und {len(host_vms) - max_vms_per_host} weitere VMs",
                                'symbol': 'rect',
                                'symbolSize': 10,
                                'itemStyle': {'color': BECHTLE_COLORS['light_gray']}
                            }
                            host_node['children'].append(more_node)
            
            # Datastores als separate Gruppe, wenn aktiviert
            if filter_options.get('show_datastores', True):
                datastores_node = {
                    'name': 'Datastores',
                    'symbol': NODE_TYPES['datastore']['symbol'],
                    'symbolSize': 25,
                    'itemStyle': {'color': NODE_TYPES['datastore']['color']},
                    'children': []
                }
                
                if datastores:
                    for ds in datastores[:max_datastores]:
                        # Zusätzliche Informationen zur Speichernutzung
                        capacity = ds.get('capacity', 0)
                        free_space = ds.get('free_space', 0)
                        used_space = capacity - free_space
                        used_percent = (used_space / capacity * 100) if capacity > 0 else 0
                        
                        ds_node = {
                            'name': ds.get('name', 'Unbekannter Datastore'),
                            'value': f"Kapazität: {self._format_size(capacity)}, {used_percent:.1f}% belegt",
                            'symbol': NODE_TYPES['datastore']['symbol'],
                            'symbolSize': 15,
                            'itemStyle': {'color': NODE_TYPES['datastore']['color']}
                        }
                        
                        # Färbung basierend auf Speichernutzung
                        if used_percent > 90:
                            ds_node['itemStyle']['color'] = '#FF0000'  # Rot für kritische Auslastung
                        elif used_percent > 75:
                            ds_node['itemStyle']['color'] = '#FFA500'  # Orange für hohe Auslastung
                        
                        datastores_node['children'].append(ds_node)
                    
                    # ... evtl mehr anzeigen
                    if len(datastores) > max_datastores:
                        more_ds_node = {
                            'name': f"... und {len(datastores) - max_datastores} weitere Datastores",
                            'symbol': 'rect',
                            'symbolSize': 10,
                            'itemStyle': {'color': BECHTLE_COLORS['light_gray']}
                        }
                        datastores_node['children'].append(more_ds_node)
                    
                    vcenter_node['children'].append(datastores_node)
            
            # Netzwerke als separate Gruppe, wenn aktiviert
            if filter_options.get('show_networks', True):
                networks_node = {
                    'name': 'Netzwerke',
                    'symbol': NODE_TYPES['network']['symbol'],
                    'symbolSize': 25,
                    'itemStyle': {'color': NODE_TYPES['network']['color']},
                    'children': []
                }
                
                if networks:
                    for net in networks[:15]:  # Maximal 15 Netzwerke zeigen
                        net_node = {
                            'name': net.get('name', 'Unbekanntes Netzwerk'),
                            'value': f"Typ: {net.get('type', 'N/A')}, VMs: {net.get('vm_count', 0)}",
                            'symbol': NODE_TYPES['network']['symbol'],
                            'symbolSize': 15,
                            'itemStyle': {'color': NODE_TYPES['network']['color']}
                        }
                        networks_node['children'].append(net_node)
                    
                    # ... evtl mehr anzeigen
                    if len(networks) > 15:
                        more_net_node = {
                            'name': f"... und {len(networks) - 15} weitere Netzwerke",
                            'symbol': 'rect',
                            'symbolSize': 10,
                            'itemStyle': {'color': BECHTLE_COLORS['light_gray']}
                        }
                        networks_node['children'].append(more_net_node)
                    
                    vcenter_node['children'].append(networks_node)
        
        return vcenter_node
    
    def _format_size(self, size_bytes):
        """
        Formatiert Byte-Größen in menschenlesbare Form
        
        Args:
            size_bytes: Größe in Bytes

        Returns:
            str: Formatierte Größe
        """
        if not size_bytes:
            return "0 B"
        
        # Einfache Größenangabe für das Diagramm
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{round(size, 2)} {units[unit_index]}"

    def generate_resource_utilization_chart(self, vsphere_data):
        """
        Generiert ein zusätzliches Diagramm zur Ressourcenauslastung
        
        Args:
            vsphere_data: Gesammeltes vSphere-Daten-Dictionary
            
        Returns:
            str: HTML-Code mit dem eingebetteten Diagramm
        """
        # Diese Funktion dient als Platzhalter für zukünftige Erweiterungen
        # Hier könnten weitere Diagramme für CPU-Auslastung, Speichernutzung etc. implementiert werden
        pass