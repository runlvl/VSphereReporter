#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report generator for vSphere environment reports
"""

import os
import datetime
import logging
import importlib.util
import sys

# Wir müssen den relativen Import anpassen, damit die Anwendung startet
current_dir = os.path.dirname(os.path.abspath(__file__))
exporters_dir = os.path.join(current_dir, 'exporters')

# Dynamisches Importieren der Exporter, um Importfehler zu vermeiden
# HTMLExporter
html_path = os.path.join(exporters_dir, 'html_exporter.py')
spec = importlib.util.spec_from_file_location('html_exporter', html_path)
html_exporter = importlib.util.module_from_spec(spec)
sys.modules['html_exporter'] = html_exporter
spec.loader.exec_module(html_exporter)
HTMLExporter = html_exporter.HTMLExporter

# DOCXExporter
docx_path = os.path.join(exporters_dir, 'docx_exporter.py')
spec = importlib.util.spec_from_file_location('docx_exporter', docx_path)
docx_exporter = importlib.util.module_from_spec(spec)
sys.modules['docx_exporter'] = docx_exporter
spec.loader.exec_module(docx_exporter)
DOCXExporter = docx_exporter.DOCXExporter

# PDFExporter
pdf_path = os.path.join(exporters_dir, 'pdf_exporter.py')
spec = importlib.util.spec_from_file_location('pdf_exporter', pdf_path)
pdf_exporter = importlib.util.module_from_spec(spec)
sys.modules['pdf_exporter'] = pdf_exporter
spec.loader.exec_module(pdf_exporter)
PDFExporter = pdf_exporter.PDFExporter

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generator for vSphere environment reports"""
    
    def __init__(self, data):
        """
        Initialize the report generator
        
        Args:
            data: DataCollector instance with vSphere data
        """
        self.data = data
        self.logger = logging.getLogger(__name__)
        
    def generate_reports(self, output_dir=None, formats=None, optional_sections=None):
        """
        Generate reports in the specified formats
        
        Args:
            output_dir: Directory where reports will be saved. Default is user's home directory
            formats: List of formats to generate. Options: 'html', 'docx', 'pdf', 'all'
            optional_sections: Dictionary specifying which optional sections to include
            
        Returns:
            List of paths to generated report files
        """
        # Setup default values
        if output_dir is None:
            output_dir = os.path.join(os.path.expanduser("~"), "vsphere_reports")
            
        if formats is None:
            formats = ['html']
            
        if 'all' in formats:
            formats = ['html', 'docx', 'pdf']
            
        if optional_sections is None:
            optional_sections = {
                'vms': True,
                'hosts': True,
                'datastores': True,
                'clusters': True,
                'resource_pools': True,
                'networks': True
            }
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize list of generated files
        generated_files = []
        
        try:
            # Generate reports in each requested format
            if 'html' in formats:
                self.logger.info("Generating HTML report")
                exporter = HTMLExporter(self.data, optional_sections)
                output_path = os.path.join(output_dir, f"vsphere_report_{timestamp}.html")
                exporter.export(output_path)
                generated_files.append(output_path)
                
            if 'docx' in formats:
                self.logger.info("Generating DOCX report")
                exporter = DOCXExporter(self.data, optional_sections)
                output_path = os.path.join(output_dir, f"vsphere_report_{timestamp}.docx")
                exporter.export(output_path)
                generated_files.append(output_path)
                
            if 'pdf' in formats:
                self.logger.info("Generating PDF report")
                exporter = PDFExporter(self.data, optional_sections)
                output_path = os.path.join(output_dir, f"vsphere_report_{timestamp}.pdf")
                exporter.export(output_path)
                generated_files.append(output_path)
                
            self.logger.info(f"Generated {len(generated_files)} reports: {generated_files}")
            return generated_files
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {str(e)}")
            raise