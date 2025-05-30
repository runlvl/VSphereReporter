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
# Hilfsfunktion für das Importieren
def import_module_from_file(module_name, file_path):
    if not os.path.exists(file_path):
        raise ImportError(f"Datei nicht gefunden: {file_path}")
        
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Konnte keine Modul-Spec für {file_path} erstellen")
        
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    if spec.loader is None:
        raise ImportError(f"Keine Loader für Modul {module_name}")
        
    spec.loader.exec_module(module)
    return module

try:
    # HTMLExporter - versuche zuerst den normalen Exporter, dann den vereinfachten
    html_path = os.path.join(exporters_dir, 'html_exporter.py')
    simple_html_path = os.path.join(exporters_dir, 'simple_html_exporter.py')
    
    # Versuche den normalen HTML-Exporter zu laden
    try:
        html_exporter = import_module_from_file('html_exporter', html_path)
        HTMLExporter = html_exporter.HTMLExporter
        print("Standard HTML-Exporter erfolgreich geladen")
    except Exception as e:
        print(f"Fehler beim Laden des HTML-Exporters: {str(e)}")
        try:
            # Versuche den vereinfachten HTML-Exporter als Fallback zu laden
            simple_html_exporter = import_module_from_file('simple_html_exporter', simple_html_path)
            HTMLExporter = simple_html_exporter.SimpleHTMLExporter
            print("Vereinfachter HTML-Exporter als Fallback geladen")
        except Exception as e2:
            print(f"Konnte auch den vereinfachten HTML-Exporter nicht laden: {str(e2)}")
            # Wenn beide fehlschlagen, werden wir später den DummyExporter verwenden

    # DOCXExporter
    docx_path = os.path.join(exporters_dir, 'docx_exporter.py')
    docx_exporter = import_module_from_file('docx_exporter', docx_path)
    DOCXExporter = docx_exporter.DOCXExporter

    # PDFExporter
    pdf_path = os.path.join(exporters_dir, 'pdf_exporter.py')
    pdf_exporter = import_module_from_file('pdf_exporter', pdf_path)
    PDFExporter = pdf_exporter.PDFExporter
    
except ImportError as e:
    print(f"FEHLER beim Importieren der Exporter-Module: {e}")
    print(f"Bitte stellen Sie sicher, dass die Exporters-Verzeichnisstruktur korrekt ist.")
    print(f"Suche nach Exportern in: {exporters_dir}")
    print(f"Verfügbare Dateien:")
    if os.path.exists(exporters_dir):
        for filename in os.listdir(exporters_dir):
            print(f" - {filename}")
    else:
        print(f" - Verzeichnis existiert nicht!")
    
    # Dummy-Klassen für Debug-Zwecke
    class DummyExporter:
        def __init__(self, data, timestamp):
            self.data = data
            self.timestamp = timestamp
        
        def export(self, output_path):
            print(f"DUMMY-EXPORT nach {output_path}")
            with open(output_path, 'w') as f:
                f.write(f"Fehler beim Laden der Exporter-Module. Bitte prüfen Sie die Anwendungsstruktur.\nBerichtszeitstempel: {self.timestamp}")
            return True
    
    HTMLExporter = DummyExporter
    DOCXExporter = DummyExporter
    PDFExporter = DummyExporter

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
            # Sammle zuerst alle Daten, um Wiederholungen zu vermeiden und Fehler früh zu erkennen
            try:
                self.logger.info("Collecting data for reports...")
                collected_data = self.data.collect_all_data(optional_sections)
                self.logger.info("Data collection completed successfully")
            except Exception as data_err:
                self.logger.error(f"Error collecting data: {str(data_err)}")
                # Fallback: Erstelle ein leeres Dictionary für die Berichte
                self.logger.warning("Using empty datasets for reports")
                collected_data = {
                    'vmware_tools': [],
                    'snapshots': [],
                    'orphaned_vmdks': [],
                    'vms': [],
                    'hosts': [],
                    'datastores': [],
                    'clusters': [],
                    'resource_pools': [],
                    'networks': []
                }
            
            timestamp_dt = datetime.datetime.now()  # Einmal für alle Exporter
            
            # Generate reports in each requested format
            if 'html' in formats:
                try:
                    self.logger.info("Generating HTML report")
                    exporter = HTMLExporter(collected_data, timestamp_dt)
                    output_path = os.path.join(output_dir, f"vsphere_report_{timestamp}.html")
                    success = exporter.export(output_path)
                    if success:
                        generated_files.append(output_path)
                        self.logger.info(f"HTML report generated successfully: {output_path}")
                    else:
                        self.logger.error(f"HTML report generation returned False")
                except Exception as html_err:
                    self.logger.error(f"Error generating HTML report: {str(html_err)}")
                    import traceback
                    self.logger.debug(f"HTML traceback: {traceback.format_exc()}")
                
            if 'docx' in formats:
                try:
                    self.logger.info("Generating DOCX report")
                    exporter = DOCXExporter(collected_data, timestamp_dt)
                    output_path = os.path.join(output_dir, f"vsphere_report_{timestamp}.docx")
                    success = exporter.export(output_path)
                    if success:
                        generated_files.append(output_path)
                        self.logger.info(f"DOCX report generated successfully: {output_path}")
                    else:
                        self.logger.error(f"DOCX report generation returned False")
                except Exception as docx_err:
                    self.logger.error(f"Error generating DOCX report: {str(docx_err)}")
                    import traceback
                    self.logger.debug(f"DOCX traceback: {traceback.format_exc()}")
                
            if 'pdf' in formats:
                try:
                    self.logger.info("Generating PDF report")
                    exporter = PDFExporter(collected_data, timestamp_dt)
                    output_path = os.path.join(output_dir, f"vsphere_report_{timestamp}.pdf")
                    success = exporter.export(output_path)
                    if success:
                        generated_files.append(output_path)
                        self.logger.info(f"PDF report generated successfully: {output_path}")
                    else:
                        self.logger.error(f"PDF report generation returned False")
                except Exception as pdf_err:
                    self.logger.error(f"Error generating PDF report: {str(pdf_err)}")
                    import traceback
                    self.logger.debug(f"PDF traceback: {traceback.format_exc()}")
                
            self.logger.info(f"Generated {len(generated_files)} reports: {generated_files}")
            return generated_files
            
        except Exception as e:
            self.logger.error(f"Error in report generation process: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Wir geben eine leere Liste zurück, anstatt eine Exception zu werfen
            # Dies verhindert das Abstürzen der Anwendung
            return []