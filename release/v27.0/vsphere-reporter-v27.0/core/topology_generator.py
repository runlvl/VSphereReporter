#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Topologie-Generator

Dieses Modul generiert eine visuelle Darstellung der vSphere-Umgebungsstruktur
als interaktives Diagramm für den HTML-Report.
"""

import logging
from pyecharts import options as opts
from pyecharts.charts import Tree
from pyecharts.globals import CurrentConfig

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
    """Generiert interaktive Topologie-Diagramme der vSphere-Umgebung"""
    
    def __init__(self):
        """Initialisiert den Topologie-Generator"""
        self.logger = logging.getLogger(__name__)
        self.nodes_data = []
        CurrentConfig.ONLINE_HOST = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/"
    
    def create_topology_tree(self, vsphere_data):
        """
        Erstellt ein hierarchisches Baum-Diagramm der vSphere-Umgebung
        
        Args:
            vsphere_data: Gesammeltes vSphere-Daten-Dictionary

        Returns:
            str: HTML-Code mit dem eingebetteten Diagramm
        """
        try:
            # Hierarchische Datenstruktur erstellen
            vcenter_node = self._build_topology_tree(vsphere_data)
            
            # Tree-Diagramm initialisieren
            tree = (
                Tree(init_opts=opts.InitOpts(
                    width="100%", 
                    height="600px",
                    bg_color="#ffffff",
                    animation_opts=opts.AnimationOpts(animation=True)
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
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title="VMware vSphere Infrastruktur",
                        subtitle="Interaktive Übersicht der virtuellen Umgebung",
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
            return "<div class='alert alert-warning'><p>Die Topologieübersicht konnte nicht generiert werden.</p></div>"
    
    def _build_topology_tree(self, vsphere_data):
        """
        Baut die hierarchische Baumstruktur für die Topologiedarstellung auf
        
        Args:
            vsphere_data: Dictionary mit vSphere-Daten

        Returns:
            dict: Hierarchische Datenstruktur für den Tree-Chart
        """
        # vCenter als Wurzel
        vcenter_name = vsphere_data.get('vcenter_info', {}).get('server', 'vCenter Server')
        
        vcenter_node = {
            'name': vcenter_name,
            'value': 'vCenter Server',
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
                        'value': f"{host.get('cpu_cores', 0)} Cores, {host.get('memory_size', 0)} RAM",
                        'symbol': NODE_TYPES['host']['symbol'],
                        'symbolSize': 15,
                        'itemStyle': {'color': NODE_TYPES['host']['color']},
                        'children': []
                    }
                    cluster_node['children'].append(host_node)
                    
                    # VMs auf dem Host
                    host_vms = [v for v in vms if v.get('host') == host.get('name')]
                    for vm in host_vms[:10]:  # Maximal 10 VMs pro Host zeigen
                        vm_node = {
                            'name': vm.get('name', 'Unbekannte VM'),
                            'value': f"{vm.get('cpu', 0)} vCPUs, {vm.get('memory_mb', 0)} MB",
                            'symbol': NODE_TYPES['vm']['symbol'],
                            'symbolSize': 10,
                            'itemStyle': {'color': NODE_TYPES['vm']['color']}
                        }
                        host_node['children'].append(vm_node)
                    
                    # ... evtl mehr anzeigen
                    if len(host_vms) > 10:
                        more_node = {
                            'name': f"... und {len(host_vms) - 10} weitere VMs",
                            'symbol': 'rect',
                            'symbolSize': 10,
                            'itemStyle': {'color': BECHTLE_COLORS['light_gray']}
                        }
                        host_node['children'].append(more_node)
            
            # Datastores als separate Gruppe
            datastores_node = {
                'name': 'Datastores',
                'symbol': NODE_TYPES['datastore']['symbol'],
                'symbolSize': 25,
                'itemStyle': {'color': NODE_TYPES['datastore']['color']},
                'children': []
            }
            
            if datastores:
                for ds in datastores[:15]:  # Maximal 15 Datastores zeigen
                    ds_node = {
                        'name': ds.get('name', 'Unbekannter Datastore'),
                        'value': f"Kapazität: {self._format_size(ds.get('capacity', 0))}",
                        'symbol': NODE_TYPES['datastore']['symbol'],
                        'symbolSize': 15,
                        'itemStyle': {'color': NODE_TYPES['datastore']['color']}
                    }
                    datastores_node['children'].append(ds_node)
                
                # ... evtl mehr anzeigen
                if len(datastores) > 15:
                    more_ds_node = {
                        'name': f"... und {len(datastores) - 15} weitere Datastores",
                        'symbol': 'rect',
                        'symbolSize': 10,
                        'itemStyle': {'color': BECHTLE_COLORS['light_gray']}
                    }
                    datastores_node['children'].append(more_ds_node)
                
                vcenter_node['children'].append(datastores_node)
            
            # Netzwerke als separate Gruppe
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
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{round(size, 2)} {units[unit_index]}"