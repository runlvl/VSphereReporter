#!/usr/bin/env python3
"""
Topology Generator Module for VMware vSphere Reporter Web Edition
Generates interactive topology diagrams of vSphere environments
"""

import logging
from pyecharts import options as opts
from pyecharts.charts import Tree
from pyVmomi import vim

# Configure logger
logger = logging.getLogger(__name__)

class TopologyGenerator:
    """Generator for vSphere environment topology diagrams"""
    
    def __init__(self, vsphere_client):
        """
        Initialize the topology generator
        
        Args:
            vsphere_client: Connected VSphereClient instance
        """
        self.client = vsphere_client
        self.logger = logging.getLogger(__name__)
    
    def generate_topology_chart(self, width="100%", height="800px"):
        """
        Generate an interactive topology chart of the vSphere environment
        
        Args:
            width: Chart width (default: 100%)
            height: Chart height (default: 800px)
            
        Returns:
            str: HTML code for the topology chart
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Generating vSphere topology chart")
        
        # Get the vCenter content
        content = self.client.content
        
        # Get all datacenters
        datacenters = self.client.get_all_datacenters()
        
        # Create the root node (vCenter)
        root_node = {
            "name": content.about.instanceName,
            "value": "vCenter",
            "itemStyle": {"color": "#00355e"},  # Bechtle dark blue
            "children": []
        }
        
        # Process each datacenter
        for dc in datacenters:
            dc_node = {
                "name": dc.name,
                "value": "Datacenter",
                "itemStyle": {"color": "#da6f1e"},  # Bechtle orange
                "children": []
            }
            
            # Add clusters
            if hasattr(dc, 'hostFolder'):
                clusters = self._get_clusters(dc.hostFolder)
                
                for cluster in clusters:
                    cluster_node = {
                        "name": cluster.name,
                        "value": "Cluster",
                        "itemStyle": {"color": "#23a96a"},  # Bechtle green
                        "children": []
                    }
                    
                    # Add hosts
                    if hasattr(cluster, 'host'):
                        for host in cluster.host:
                            host_node = {
                                "name": host.name,
                                "value": "ESXi Host",
                                "itemStyle": {"color": "#5a5a5a"},  # Bechtle dark gray
                                "children": []
                            }
                            
                            # Add VMs
                            if hasattr(host, 'vm'):
                                for vm in host.vm:
                                    vm_node = {
                                        "name": vm.name,
                                        "value": "VM",
                                        "itemStyle": {"color": "#f3f3f3", "borderColor": "#5a5a5a"},  # Bechtle light gray
                                    }
                                    
                                    host_node["children"].append(vm_node)
                            
                            cluster_node["children"].append(host_node)
                    
                    dc_node["children"].append(cluster_node)
            
            root_node["children"].append(dc_node)
        
        # Create the chart
        chart = (
            Tree()
            .add(
                series_name="",
                data=[root_node],
                pos_top="2%",
                pos_bottom="2%",
                pos_left="2%",
                pos_right="20%",
                layout="orthogonal",
                orient="LR",
                initial_tree_depth=2,
                is_roam=True,
                symbol_size=16,
                edge_fork_position="50%",
                label_opts=opts.LabelOpts(
                    position="right",
                    vertical_align="middle",
                    font_size=12,
                    color="#000"
                ),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="VMware vSphere Umgebung Topologie",
                    subtitle="Interaktive Visualisierung der vSphere-Infrastruktur",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(
                        color="#00355e",
                        font_size=18
                    ),
                    subtitle_textstyle_opts=opts.TextStyleOpts(
                        color="#5a5a5a",
                        font_size=14
                    )
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="item",
                    formatter="{b}: {c}"
                ),
            )
        )
        
        # Configure chart size
        chart.width = width
        chart.height = height
        
        # Return HTML
        html = chart.render_embed()
        self.logger.info("Topology chart generated successfully")
        
        return html
    
    def _get_clusters(self, folder):
        """
        Recursively get all clusters from a folder
        
        Args:
            folder: Folder to search for clusters
            
        Returns:
            list: List of cluster objects
        """
        clusters = []
        
        if hasattr(folder, 'childEntity'):
            for entity in folder.childEntity:
                if isinstance(entity, vim.ClusterComputeResource):
                    clusters.append(entity)
                elif isinstance(entity, vim.Folder):
                    clusters.extend(self._get_clusters(entity))
        
        return clusters