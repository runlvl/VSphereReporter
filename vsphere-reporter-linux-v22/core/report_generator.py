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
        
        # Protokollieren der erhaltenen Daten für Diagnosezwecke
        logger.info("Report Generator initialized with data:")
        logger.info(f"VMware Tools: {len(data.get('vmware_tools', []))} entries")
        logger.info(f"Snapshots: {len(data.get('snapshots', []))} entries")
        logger.info(f"Orphaned VMDKs: {len(data.get('orphaned_vmdks', []))} entries")
        logger.info(f"VMs: {len(data.get('vms', []))} entries")
        logger.info(f"Hosts: {len(data.get('hosts', []))} entries")
        logger.info(f"Datastores: {len(data.get('datastores', []))} entries")
        
        # Sicherstellen, dass die erforderlichen Sektionen für Sprungmarken immer vorhanden sind
        # Dies ist wichtig, damit die Navigation in den Berichten korrekt funktioniert
        if not 'vmware_tools' in self.data:
            self.data['vmware_tools'] = []
            
        if not 'snapshots' in self.data:
            logger.warning("No snapshots data found, creating empty list")
            self.data['snapshots'] = []
            
        if not 'orphaned_vmdks' in self.data:
            logger.warning("No orphaned VMDKs data found, creating empty list")
            self.data['orphaned_vmdks'] = []
            
        # Debug-Modus überprüfen
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        if debug_mode:
            logger.warning("*** REPORT GENERATOR DEBUG MODE ACTIVE ***")
            logger.warning(f"Final dataset sizes:")
            logger.warning(f"VMware Tools: {len(self.data.get('vmware_tools', []))} entries")
            logger.warning(f"Snapshots: {len(self.data.get('snapshots', []))} entries")
            logger.warning(f"Orphaned VMDKs: {len(self.data.get('orphaned_vmdks', []))} entries")
            logger.warning(f"VMs: {len(self.data.get('vms', []))} entries")
            logger.warning(f"Hosts: {len(self.data.get('hosts', []))} entries")
            logger.warning(f"Datastores: {len(self.data.get('datastores', []))} entries")
        
        # Wenn wir in einem Diagnosemodus sind, füge Testdaten hinzu
        # Dies dient zur Überprüfung, ob die Berichtsvorlagen korrekt funktionieren
        import os
        if os.environ.get('VSPHERE_REPORTER_DEBUG') == '1':
            logger.warning("Debug mode enabled, adding test data to reports")
            
            # Hinzufügen von Testdaten für Snapshots, wenn keine vorhanden sind
            if len(self.data.get('snapshots', [])) == 0:
                logger.info("Adding test snapshot entry")
                test_snapshot = {
                    'vm_name': 'TEST-VM-DEBUG',
                    'name': 'TEST-SNAPSHOT-DEBUG',
                    'description': 'This is a test snapshot for debugging',
                    'create_time': datetime.datetime.now() - datetime.timedelta(days=10),
                    'age_days': 10,
                    'age_hours': 240
                }
                # Stelle sicher, dass wir nicht überschreiben
                if 'snapshots' not in self.data:
                    self.data['snapshots'] = []
                self.data['snapshots'].append(test_snapshot)
            
            # Hinzufügen von Testdaten für Orphaned VMDKs, wenn keine vorhanden sind
            if len(self.data.get('orphaned_vmdks', [])) == 0:
                logger.info("Adding test orphaned VMDK entry")
                test_vmdk = {
                    'path': '[TEST-DATASTORE] TEST-VM-DEBUG/TEST-VM-DEBUG.vmdk',
                    'datastore': 'TEST-DATASTORE',
                    'size': 1073741824,  # 1 GB
                    'modification_time': datetime.datetime.now() - datetime.timedelta(days=30),
                    'reason': 'Test orphaned VMDK for debugging'
                }
                # Stelle sicher, dass wir nicht überschreiben
                if 'orphaned_vmdks' not in self.data:
                    self.data['orphaned_vmdks'] = []
                self.data['orphaned_vmdks'].append(test_vmdk)
        
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
