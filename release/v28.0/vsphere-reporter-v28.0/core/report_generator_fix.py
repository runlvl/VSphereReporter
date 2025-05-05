#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verbesserte Version des Report-Generators für Version 28.0
mit Fehlerbehandlung und Absturzsicherheit
"""

import os
import logging
import datetime
import tempfile
import threading
import traceback
import time

from core.utils.error_handler import ErrorHandler, log_exception

from core.exporters.html_exporter import HTMLExporter
from core.exporters.docx_exporter import DOCXExporter
from core.exporters.pdf_exporter import PDFExporter

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Spezieller Report-Generator für v28.0 mit verbesserter Fehlerbehandlung"""
    
    def __init__(self, data, output_dir=None):
        """
        Initialisiert den Report-Generator
        
        Args:
            data: Gesammelte Daten aus der vSphere-Umgebung
            output_dir: Ausgabeverzeichnis für die Berichte
        """
        self.data = data or {}
        
        # Sicherheitsüberprüfung für die wichtigsten Datenfelder
        if not isinstance(self.data, dict):
            logger.error("Daten sind kein Dictionary - Initialisiere leeres Dictionary")
            self.data = {}
            
        # Stelle sicher, dass alle benötigten Schlüssel existieren
        required_keys = ['vmware_tools', 'snapshots', 'orphaned_vmdks']
        for key in required_keys:
            if key not in self.data:
                logger.warning(f"Schlüssel '{key}' fehlt in den Daten - Initialisiere leere Liste")
                self.data[key] = []
        
        # Ausgabeverzeichnis setzen
        self.output_dir = output_dir or os.path.join(os.getcwd(), "reports")
        
        # Zeitstempel für Berichte
        self.timestamp = datetime.datetime.now()
        
        # Status und Fortschritt
        self.status = "Bereit"
        self.progress = 0
        self.error_message = None
        self.cancelled = False
        
        # Thread-Lock für Thread-Sicherheit
        self.lock = threading.Lock()
    
    def _ensure_output_dir(self):
        """Stellt sicher, dass das Ausgabeverzeichnis existiert"""
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                logger.info(f"Ausgabeverzeichnis erstellt: {self.output_dir}")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Ausgabeverzeichnisses: {str(e)}")
            raise
    
    def _update_status(self, status, progress=None):
        """Aktualisiert den Status und Fortschritt des Report-Generators"""
        with self.lock:
            self.status = status
            if progress is not None:
                self.progress = progress
            logger.info(f"Status: {status}, Fortschritt: {self.progress}%")
    
    def _check_cancelled(self):
        """Prüft, ob der Vorgang abgebrochen wurde"""
        with self.lock:
            return self.cancelled
    
    def cancel(self):
        """Bricht den Report-Generierungsprozess ab"""
        with self.lock:
            self.cancelled = True
            self.status = "Abgebrochen"
            logger.info("Report-Generierung abgebrochen")
    
    def generate_reports(self, formats=None, callback=None):
        """
        Generiert Berichte in den angegebenen Formaten
        
        Args:
            formats: Liste der zu generierenden Formate (html, docx, pdf)
            callback: Optionale Callback-Funktion für Statusaktualisierungen
            
        Returns:
            dict: Pfade zu den generierten Berichten
        """
        if formats is None:
            formats = ["html"]
            
        if not isinstance(formats, list):
            formats = [formats]
            
        # Validiere die Formate
        valid_formats = ["html", "docx", "pdf"]
        formats = [fmt.lower() for fmt in formats if fmt.lower() in valid_formats]
        
        self._update_status("Berichte werden generiert...", 0)
        
        try:
            self._ensure_output_dir()
            
            generated_reports = {}
            total_formats = len(formats)
            
            for i, fmt in enumerate(formats):
                if self._check_cancelled():
                    logger.info("Report-Generierung abgebrochen")
                    break
                    
                progress = int((i / total_formats) * 100)
                self._update_status(f"{fmt.upper()}-Bericht wird generiert...", progress)
                
                try:
                    if callback:
                        callback(self.status, self.progress)
                        
                    if fmt == "html":
                        path = self._generate_html_report()
                    elif fmt == "docx":
                        path = self._generate_docx_report()
                    elif fmt == "pdf":
                        path = self._generate_pdf_report()
                    
                    generated_reports[fmt] = path
                    
                except Exception as e:
                    logger.error(f"Fehler beim Generieren des {fmt.upper()}-Berichts: {str(e)}")
                    logger.error(traceback.format_exc())
                    with self.lock:
                        self.error_message = f"Fehler beim Generieren des {fmt.upper()}-Berichts: {str(e)}"
                    
                    # Versuchen Sie es mit einer sicheren Alternative, wenn HTML fehlschlägt
                    if fmt == "html":
                        try:
                            logger.info("Versuche, einen einfachen HTML-Bericht zu generieren...")
                            path = self._generate_simple_html_report()
                            generated_reports[fmt] = path
                        except Exception as e2:
                            logger.error(f"Auch der einfache HTML-Bericht ist fehlgeschlagen: {str(e2)}")
            
            progress = 100
            self._update_status("Berichte generiert", progress)
            
            if callback:
                callback(self.status, self.progress)
                
            return generated_reports
            
        except Exception as e:
            # Nutze den ErrorHandler für bessere Fehlerbehandlung
            error_info = ErrorHandler.handle_error(e, context="Report-Generierung", show_traceback=True)
            
            with self.lock:
                self.error_message = error_info["message"]
            
            if callback:
                callback(f"Fehler: {error_info['message']}", 0)
            
            logger.error(f"Unerwarteter Fehler bei der Report-Generierung: {error_info['message']}")
                
            # Gebe zumindest die bereits generierten Berichte zurück
            return {}
    
    def _generate_html_report(self):
        """
        Generiert einen HTML-Bericht
        
        Returns:
            str: Pfad zum generierten Bericht
        """
        try:
            # Sichere Fehlerbehandlung beim Laden des Exporters
            try:
                exporter = HTMLExporter(self.data, self.timestamp)
            except Exception as e:
                logger.error(f"Fehler beim Initialisieren des HTML-Exporters: {str(e)}")
                raise
            
            # Erstellung des Dateinamens mit sicherer Zeitstempelformatierung
            try:
                timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
            except:
                timestamp_str = str(int(time.time()))
                
            filename = f"vsphere_report_{timestamp_str}.html"
            output_path = os.path.join(self.output_dir, filename)
            
            # Sichere Fehlerbehandlung beim Export
            try:
                exporter.export(output_path)
            except Exception as e:
                logger.error(f"Fehler beim HTML-Export: {str(e)}")
                # Temporären Fallback-Export versuchen
                try:
                    fallback_path = os.path.join(tempfile.gettempdir(), filename)
                    exporter.export(fallback_path)
                    output_path = fallback_path
                except Exception as e2:
                    logger.error(f"Auch Fallback-Export fehlgeschlagen: {str(e2)}")
                    # Als letzter Ausweg den einfachen HTML-Exporter verwenden
                    output_path = self._generate_simple_html_report()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Fehler im HTML-Report-Generator: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _generate_simple_html_report(self):
        """
        Generiert einen einfachen HTML-Bericht für Notfälle
        
        Returns:
            str: Pfad zum generierten Bericht
        """
        from core.exporters.simple_html_exporter import SimpleHTMLExporter
        
        try:
            exporter = SimpleHTMLExporter(self.data, self.timestamp)
            
            timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"vsphere_simple_report_{timestamp_str}.html"
            output_path = os.path.join(self.output_dir, filename)
            
            exporter.export(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Fehler im einfachen HTML-Report-Generator: {str(e)}")
            raise
    
    def _generate_docx_report(self):
        """
        Generiert einen DOCX-Bericht
        
        Returns:
            str: Pfad zum generierten Bericht
        """
        try:
            exporter = DOCXExporter(self.data, self.timestamp)
            
            timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"vsphere_report_{timestamp_str}.docx"
            output_path = os.path.join(self.output_dir, filename)
            
            exporter.export(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Fehler im DOCX-Report-Generator: {str(e)}")
            raise
    
    def _generate_pdf_report(self):
        """
        Generiert einen PDF-Bericht
        
        Returns:
            str: Pfad zum generierten Bericht
        """
        try:
            exporter = PDFExporter(self.data, self.timestamp)
            
            timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"vsphere_report_{timestamp_str}.pdf"
            output_path = os.path.join(self.output_dir, filename)
            
            exporter.export(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Fehler im PDF-Report-Generator: {str(e)}")
            raise