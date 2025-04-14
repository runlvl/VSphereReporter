#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report generator for vSphere environment reports
"""

import os
import datetime
import logging
from core.exporters.html_exporter import HTMLExporter
from core.exporters.docx_exporter import DOCXExporter
from core.exporters.pdf_exporter import PDFExporter

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generator for vSphere environment reports"""
    
    def __init__(self, data):
        """
        Initialize the report generator
        
        Args:
            data (dict): Dictionary containing collected vSphere data
        """
        self.data = data
        
        # Sicherstellen, dass die erforderlichen Sektionen für Sprungmarken immer vorhanden sind
        # Dies ist wichtig, damit die Navigation in den Berichten korrekt funktioniert
        if not 'vmware_tools' in self.data:
            self.data['vmware_tools'] = []
            
        if not 'snapshots' in self.data:
            self.data['snapshots'] = []
            
        if not 'orphaned_vmdks' in self.data:
            self.data['orphaned_vmdks'] = []
            
        self.timestamp = datetime.datetime.now()
        self.filename_base = f"vsphere_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
        
    def export_to_html(self, output_dir):
        """
        Export the report to HTML format
        
        Args:
            output_dir (str): Directory to save the report
            
        Returns:
            str: Path to the generated HTML file
        """
        logger.info("Generating HTML report")
        
        exporter = HTMLExporter(self.data, self.timestamp)
        output_path = os.path.join(output_dir, f"{self.filename_base}.html")
        
        try:
            exporter.export(output_path)
            logger.info(f"HTML report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            raise Exception(f"Error generating HTML report: {str(e)}")
            
    def export_to_docx(self, output_dir):
        """
        Export the report to DOCX format
        
        Args:
            output_dir (str): Directory to save the report
            
        Returns:
            str: Path to the generated DOCX file
        """
        logger.info("Generating DOCX report")
        
        exporter = DOCXExporter(self.data, self.timestamp)
        output_path = os.path.join(output_dir, f"{self.filename_base}.docx")
        
        try:
            exporter.export(output_path)
            logger.info(f"DOCX report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating DOCX report: {str(e)}")
            raise Exception(f"Error generating DOCX report: {str(e)}")
            
    def export_to_pdf(self, output_dir):
        """
        Export the report to PDF format
        
        Args:
            output_dir (str): Directory to save the report
            
        Returns:
            str: Path to the generated PDF file
        """
        logger.info("Generating PDF report")
        
        exporter = PDFExporter(self.data, self.timestamp)
        output_path = os.path.join(output_dir, f"{self.filename_base}.pdf")
        
        try:
            exporter.export(output_path)
            logger.info(f"PDF report saved to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise Exception(f"Error generating PDF report: {str(e)}")
