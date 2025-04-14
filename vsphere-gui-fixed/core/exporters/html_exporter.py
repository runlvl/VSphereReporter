#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML report exporter
"""

import os
import logging
import jinja2
import datetime
import humanize

logger = logging.getLogger(__name__)

class HTMLExporter:
    """Exporter for HTML reports"""
    
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
        
        # Set up assets for HTML embedding - use the white logo for better visibility in reports
        # The white logo is only used in reports, not in the tool itself
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
        
    def export(self, output_path):
        """
        Export data to HTML file
        
        Args:
            output_path (str): Path to save the HTML file
            
        Returns:
            bool: True if export was successful
        """
        try:
            # Get the template
            template = self.jinja_env.get_template('report_template.html')
            
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
            
            # Render the template with data
            html_content = template.render(
                report_title="VMware vSphere Environment Report",
                report_date=self.timestamp,
                data=self.data,
                sections=self._get_sections(),
                bechtle_logo=logo_data
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
        
        # VMware Tools section (required)
        sections.append({
            'id': 'vmware_tools',
            'title': 'VMware Tools Versions',
            'description': 'VMware Tools versions for all virtual machines, ordered by oldest version first.',
            'priority': 1
        })
        
        # Snapshots section (required)
        sections.append({
            'id': 'snapshots',
            'title': 'VM Snapshots',
            'description': 'Virtual machine snapshots, ordered by oldest first.',
            'priority': 2
        })
        
        # Orphaned VMDKs section (required)
        sections.append({
            'id': 'orphaned_vmdks',
            'title': 'Orphaned VMDK Files',
            'description': 'VMDK files that appear to be orphaned or not associated with any registered virtual machine.',
            'priority': 3
        })
            
        # Additional sections
        if 'vms' in self.data:
            sections.append({
                'id': 'vms',
                'title': 'Virtual Machines',
                'description': 'Overview of all virtual machines in the environment.',
                'priority': 4
            })
            
        if 'hosts' in self.data:
            sections.append({
                'id': 'hosts',
                'title': 'ESXi Hosts',
                'description': 'Overview of all ESXi hosts in the environment.',
                'priority': 5
            })
            
        if 'datastores' in self.data:
            sections.append({
                'id': 'datastores',
                'title': 'Datastores',
                'description': 'Overview of all datastores in the environment.',
                'priority': 6
            })
            
        if 'clusters' in self.data:
            sections.append({
                'id': 'clusters',
                'title': 'Clusters',
                'description': 'Overview of all clusters in the environment.',
                'priority': 7
            })
            
        if 'resource_pools' in self.data:
            sections.append({
                'id': 'resource_pools',
                'title': 'Resource Pools',
                'description': 'Overview of all resource pools in the environment.',
                'priority': 8
            })
            
        if 'networks' in self.data:
            sections.append({
                'id': 'networks',
                'title': 'Networks',
                'description': 'Overview of all networks in the environment.',
                'priority': 9
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
