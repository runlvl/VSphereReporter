#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML exporter for vSphere environment reports
Erweiterte Version für v28.0 mit Topologie- und Suchfunktionen
"""

import os
import logging
import jinja2
import datetime
import humanize
import sys
import json

# Stellen Sie sicher, dass core im Pythonpfad ist
current_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.dirname(current_dir)
if core_dir not in sys.path:
    sys.path.append(core_dir)

from topology_generator import TopologyGenerator

logger = logging.getLogger(__name__)

class HTMLExporter:
    """Erweiterter Exporter für HTML-Berichte mit Topologie und Filteroptionen"""
    
    def __init__(self, data, timestamp):
        """
        Initialize the HTML exporter
        
        Args:
            data (dict): Dictionary containing collected vSphere data
            timestamp (datetime): Report generation timestamp
        """
        self.data = data
        self.timestamp = timestamp
        
        # Stellen Sie sicher, dass alle erforderlichen Schlüssel vorhanden sind
        if not self.data:
            self.data = {}
        
        # Pflichtdaten
        if 'vmware_tools' not in self.data:
            self.data['vmware_tools'] = []
        if 'snapshots' not in self.data:
            self.data['snapshots'] = []
        if 'orphaned_vmdks' not in self.data:
            self.data['orphaned_vmdks'] = []
        
        # Set up assets for HTML embedding
        white_logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'images', 'logo_bechtle_white.png')
        regular_logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'images', 'logo_bechtle.png')
        
        # Bevorzugt das weiße Logo für Berichte, fallback auf das normale Logo
        if os.path.exists(white_logo_path):
            self.logo_path = white_logo_path
        else:
            self.logo_path = regular_logo_path
        
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.jinja_env.filters['format_date'] = self.format_date
        self.jinja_env.filters['format_datetime'] = self.format_datetime
        self.jinja_env.filters['format_size'] = self.format_size
        self.jinja_env.filters['format_percent'] = self.format_percent
        self.jinja_env.filters['to_json'] = self.to_json
        
    def export(self, output_path, filter_options=None):
        """
        Export data to HTML file with filter options
        
        Args:
            output_path (str): Path to save the HTML file
            filter_options (dict): Optional filter options for the report
            
        Returns:
            bool: True if export was successful
        """
        try:
            # Default filter options
            if filter_options is None:
                filter_options = {
                    'show_vms': True,
                    'show_datastores': True,
                    'show_networks': True,
                    'max_vms_per_host': 10,
                    'max_datastores': 15,
                    'include_topology': True
                }
                
            # Get the template
            template = self.jinja_env.get_template('report_template_v28.html')
            
            # Prepare the logo for embedding if it exists
            logo_data = None
            if os.path.exists(self.logo_path):
                try:
                    import base64
                    with open(self.logo_path, 'rb') as logo_file:
                        logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
                    logger.info(f"Bechtle logo loaded successfully from {self.logo_path}")
                except Exception as e:
                    logger.warning(f"Could not load Bechtle logo: {str(e)}")
            
            # Generiere die Topologieansicht, wenn gewünscht
            topology_chart = None
            if filter_options.get('include_topology', True):
                try:
                    topology_generator = TopologyGenerator()
                    topology_chart = topology_generator.create_topology_tree(self.data, filter_options)
                    logger.info("Topology chart generated successfully")
                except Exception as e:
                    logger.error(f"Error generating topology chart: {str(e)}")
                    topology_chart = "<div class='alert alert-warning'><p>Die Topologieübersicht konnte nicht generiert werden: " + str(e) + "</p></div>"
            
            # Prepare VMDK data for filtering in JavaScript
            vmdk_data_json = self.to_json(self.data.get('orphaned_vmdks', []))
            
            # Render the template with data
            html_content = template.render(
                report_title="VMware vSphere Environment Report",
                report_date=self.timestamp,
                data=self.data,
                sections=self._get_sections(),
                bechtle_logo=logo_data,
                topology_chart=topology_chart,
                vmdk_data_json=vmdk_data_json,
                filter_options=filter_options
            )
            
            # Write the rendered HTML to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to HTML: {str(e)}")
            raise
            
    def _get_sections(self):
        """
        Get report sections based on available data
        
        Returns:
            list: List of section dictionaries
        """
        sections = []
        
        # Topologie-Übersicht (neu)
        sections.append({
            'id': 'topology',
            'title': 'Infrastruktur-Topologie',
            'description': 'Interaktive graphische Übersicht der vSphere-Infrastruktur.',
            'priority': 1
        })
        
        # VMware Tools section (required)
        sections.append({
            'id': 'vmware_tools',
            'title': 'VMware Tools Versions',
            'description': 'VMware Tools versions for all virtual machines, ordered by oldest version first.',
            'priority': 2
        })
        
        # Snapshots section (required)
        sections.append({
            'id': 'snapshots',
            'title': 'VM Snapshots',
            'description': 'Virtual machine snapshots, ordered by oldest first.',
            'priority': 3
        })
        
        # Orphaned VMDKs section (required)
        sections.append({
            'id': 'orphaned_vmdks',
            'title': 'VMDK-Dateien',
            'description': 'Übersicht aller VMDK-Dateien in der Umgebung mit Status und Zuordnungsinformationen.',
            'priority': 4
        })
            
        # Additional sections
        if 'vms' in self.data:
            sections.append({
                'id': 'vms',
                'title': 'Virtual Machines',
                'description': 'Overview of all virtual machines in the environment.',
                'priority': 5
            })
            
        if 'hosts' in self.data:
            sections.append({
                'id': 'hosts',
                'title': 'ESXi Hosts',
                'description': 'Overview of all ESXi hosts in the environment.',
                'priority': 6
            })
            
        if 'datastores' in self.data:
            sections.append({
                'id': 'datastores',
                'title': 'Datastores',
                'description': 'Overview of all datastores in the environment.',
                'priority': 7
            })
            
        if 'clusters' in self.data:
            sections.append({
                'id': 'clusters',
                'title': 'Clusters',
                'description': 'Overview of all clusters in the environment.',
                'priority': 8
            })
            
        if 'resource_pools' in self.data:
            sections.append({
                'id': 'resource_pools',
                'title': 'Resource Pools',
                'description': 'Overview of all resource pools in the environment.',
                'priority': 9
            })
            
        if 'networks' in self.data:
            sections.append({
                'id': 'networks',
                'title': 'Networks',
                'description': 'Overview of all networks in the environment.',
                'priority': 10
            })
            
        # Sort sections by priority
        sections.sort(key=lambda x: x['priority'])
        
        return sections
        
    @staticmethod
    def format_date(value):
        """Format date value for display"""
        if isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d')
        return str(value)
        
    @staticmethod
    def format_datetime(value):
        """Format datetime value for display"""
        if isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value)
        
    @staticmethod
    def format_size(value):
        """Format byte size value for display"""
        try:
            return humanize.naturalsize(value, binary=True)
        except:
            return str(value)
            
    @staticmethod
    def format_percent(value):
        """Format percentage value for display"""
        try:
            return f"{value:.2f}%"
        except:
            return str(value)
    
    @staticmethod        
    def to_json(data):
        """Convert data to JSON for JavaScript use"""
        try:
            return json.dumps(data)
        except:
            return "[]"
    
    def export_vmdks_as_csv(self, output_path):
        """
        Export VMDK data to CSV file
        
        Args:
            output_path (str): Path to save the CSV file
            
        Returns:
            bool: True if export was successful
        """
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Define fields for CSV
                fieldnames = ['status', 'vm', 'datastore', 'path', 'size_mb', 'modification_time', 'explanation']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for vmdk in self.data.get('orphaned_vmdks', []):
                    # Create a clean dict with only the fields we want
                    row = {field: vmdk.get(field, '') for field in fieldnames}
                    writer.writerow(row)
                    
            return True
        except Exception as e:
            logger.error(f"Error exporting VMDKs to CSV: {str(e)}")
            return False