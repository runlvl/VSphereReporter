"""
Bechtle vSphere Reporter v0.2 - Report Generator
Modul für die Generierung von Berichten in verschiedenen Formaten

Stellt eine zentrale Klasse für die Erzeugung von Berichten in den Formaten HTML, PDF und DOCX
zur Verfügung, mit konsistentem Layout und Bechtle-Branding.

© 2025 Bechtle GmbH - Alle Rechte vorbehalten
"""

import os
import logging
import tempfile
from datetime import datetime
import jinja2
import humanize
import io
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image

# Konfiguriere Logging
logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generator für VMware vSphere Berichte in verschiedenen Formaten
    """
    
    def __init__(self, data, client, demo_mode=False):
        """
        Initialisiert den Report Generator
        
        Args:
            data (dict): Die gesammelten Daten für den Bericht
            client: Der vSphere Client für zusätzliche Informationen
            demo_mode (bool): Gibt an, ob der Demo-Modus aktiv ist
        """
        self.data = data
        self.client = client
        self.demo_mode = demo_mode
        self.report_dir = os.path.join(tempfile.gettempdir(), 'bechtle_vsphere_reports')
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Stelle sicher, dass das Verzeichnis existiert
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        
        # Template-Pfad
        self.template_path = os.path.join(os.path.dirname(__file__), 'templates')
        
        # Jinja2 Umgebung für Templates
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_path),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def generate_report(self, include_sections, export_formats):
        """
        Generiert Berichte in den angegebenen Formaten
        
        Args:
            include_sections (dict): Enthält die auszuwählenden Berichtsabschnitte
            export_formats (dict): Enthält die zu exportierenden Formate
            
        Returns:
            dict: Pfade zu den generierten Berichtsdateien
        """
        logger.info(f"Generiere Bericht mit Abschnitten: {include_sections} in Formaten: {export_formats}")
        
        # Stelle sicher, dass mindestens ein Abschnitt ausgewählt ist
        if not any(include_sections.values()):
            raise ValueError("Mindestens ein Berichtsabschnitt muss ausgewählt sein.")
        
        # Stelle sicher, dass mindestens ein Format ausgewählt ist
        if not any(export_formats.values()):
            raise ValueError("Mindestens ein Exportformat muss ausgewählt sein.")
        
        # Vorbereiten der Berichtsdaten
        report_data = self._prepare_report_data(include_sections)
        
        # Generiere Berichte in den ausgewählten Formaten
        generated_files = {}
        
        if export_formats.get('html', False):
            html_path = self._generate_html_report(report_data, include_sections)
            generated_files['html'] = html_path
        
        if export_formats.get('pdf', False):
            pdf_path = self._generate_pdf_report(report_data, include_sections)
            generated_files['pdf'] = pdf_path
        
        if export_formats.get('docx', False):
            docx_path = self._generate_docx_report(report_data, include_sections)
            generated_files['docx'] = docx_path
        
        return generated_files
    
    def _prepare_report_data(self, include_sections):
        """
        Bereitet die Daten für den Bericht vor
        
        Args:
            include_sections (dict): Enthält die auszuwählenden Berichtsabschnitte
            
        Returns:
            dict: Aufbereitete Daten für den Bericht
        """
        report_data = {
            'title': 'VMware vSphere Infrastrukturbericht',
            'generated_at': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            'demo_mode': self.demo_mode,
            'sections': []
        }
        
        # Verbindungsinformationen
        if hasattr(self.client, 'host') and self.client.host:
            report_data['vcenter'] = self.client.host
        else:
            report_data['vcenter'] = 'Demo-Modus - Keine Verbindung'
        
        # Füge die ausgewählten Abschnitte hinzu
        if include_sections.get('vmware_tools', False) and 'vmware_tools' in self.data:
            report_data['sections'].append({
                'id': 'vmware_tools',
                'title': 'VMware Tools Status',
                'data': self.data['vmware_tools']
            })
        
        if include_sections.get('snapshots', False) and 'snapshots' in self.data:
            report_data['sections'].append({
                'id': 'snapshots',
                'title': 'VM Snapshots',
                'data': self.data['snapshots']
            })
        
        if include_sections.get('orphaned_vmdks', False) and 'orphaned_vmdks' in self.data:
            report_data['sections'].append({
                'id': 'orphaned_vmdks',
                'title': 'Verwaiste VMDK-Dateien',
                'data': self.data['orphaned_vmdks']
            })
        
        return report_data
    
    def _generate_html_report(self, report_data, include_sections):
        """
        Generiert einen HTML-Bericht
        
        Args:
            report_data (dict): Aufbereitete Daten für den Bericht
            include_sections (dict): Enthält die auszuwählenden Berichtsabschnitte
            
        Returns:
            str: Pfad zur generierten HTML-Datei
        """
        logger.info("Generiere HTML-Bericht...")
        
        # Lade das Template
        template = self.env.get_template('report_template.html')
        
        # Rendere das Template mit den Daten
        html_content = template.render(
            report=report_data,
            version="0.2"  # Stellen Sie sicher, dass hier die aktuelle Version steht
        )
        
        # Speichere den Bericht
        file_path = os.path.join(self.report_dir, f'vsphere_report_{self.timestamp}.html')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML-Bericht gespeichert unter: {file_path}")
        return file_path
    
    def _generate_pdf_report(self, report_data, include_sections):
        """
        Generiert einen PDF-Bericht mit ReportLab
        
        Args:
            report_data (dict): Aufbereitete Daten für den Bericht
            include_sections (dict): Enthält die auszuwählenden Berichtsabschnitte
            
        Returns:
            str: Pfad zur generierten PDF-Datei
        """
        logger.info("Generiere PDF-Bericht...")
        
        # Dateipfad für das PDF
        file_path = os.path.join(self.report_dir, f'vsphere_report_{self.timestamp}.pdf')
        
        # Erstelle PDF-Dokument
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            title=report_data['title'],
            author="Bechtle GmbH"
        )
        
        # Definiere Stile
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading1']
        normal_style = styles['Normal']
        
        # Definiere Bechtle-Farben
        bechtle_blue = colors.HexColor('#00355e')
        bechtle_orange = colors.HexColor('#da6f1e')
        
        # Erstelle benutzerdefinierte Stile
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=heading_style,
            textColor=bechtle_blue,
            spaceAfter=12
        )
        
        # Erstelle Story (Inhalt)
        story = []
        
        # Titel und Metadaten
        story.append(Paragraph(report_data['title'], title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Erstellt am: {report_data['generated_at']}", normal_style))
        story.append(Paragraph(f"vCenter: {report_data['vcenter']}", normal_style))
        if report_data['demo_mode']:
            story.append(Paragraph("DEMO-MODUS - Beispieldaten", 
                         ParagraphStyle('Demo', parent=normal_style, textColor=colors.red)))
        story.append(Spacer(1, 24))
        
        # Füge Abschnitte hinzu
        for section in report_data['sections']:
            story.append(Paragraph(section['title'], section_title_style))
            story.append(Spacer(1, 12))
            
            # Je nach Abschnittstyp unterschiedliche Tabellen erstellen
            if section['id'] == 'vmware_tools':
                # Tabelle für VMware Tools Status
                if section['data']:
                    data = [['VM-Name', 'Tools-Version', 'Status', 'Betriebssystem']]
                    
                    # Füge Daten hinzu
                    for item in section['data']:
                        status_text = item.get('status_text', '')
                        running_text = item.get('running_text', '')
                        
                        if status_text and running_text:
                            status = f"{status_text} / {running_text}"
                        else:
                            status = status_text or running_text or '-'
                            
                        data.append([
                            item.get('name', '-'),
                            item.get('tools_version', '-'),
                            status,
                            item.get('os', '-')
                        ])
                    
                    # Erstelle Tabelle
                    table = Table(data, colWidths=[120, 80, 100, 180])
                    
                    # Styling der Tabelle
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), bechtle_blue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ])
                    
                    # Farbkodierung basierend auf Status
                    for i, item in enumerate(section['data'], 1):
                        status_class = item.get('status_class', '')
                        
                        if status_class == 'success':
                            table_style.add('TEXTCOLOR', (2, i), (2, i), colors.green)
                        elif status_class == 'warning':
                            table_style.add('TEXTCOLOR', (2, i), (2, i), colors.orange)
                        elif status_class == 'danger':
                            table_style.add('TEXTCOLOR', (2, i), (2, i), colors.red)
                    
                    table.setStyle(table_style)
                    story.append(table)
                else:
                    story.append(Paragraph("Keine VMware Tools Daten verfügbar", normal_style))
            
            elif section['id'] == 'snapshots':
                # Tabelle für Snapshots
                if section['data']:
                    data = [['VM-Name', 'Snapshot-Name', 'Erstellungsdatum', 'Alter', 'Größe']]
                    
                    # Füge Daten hinzu
                    for item in section['data']:
                        data.append([
                            item.get('vm_name', '-'),
                            item.get('name', '-'),
                            item.get('create_time_str', '-'),
                            item.get('age_str', '-'),
                            item.get('size_str', '-')
                        ])
                    
                    # Erstelle Tabelle
                    table = Table(data, colWidths=[100, 100, 100, 100, 80])
                    
                    # Styling der Tabelle
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), bechtle_blue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ])
                    
                    # Farbkodierung basierend auf Alter
                    for i, item in enumerate(section['data'], 1):
                        age_class = item.get('age_class', '')
                        
                        if age_class == 'success':
                            table_style.add('TEXTCOLOR', (3, i), (3, i), colors.green)
                        elif age_class == 'warning':
                            table_style.add('TEXTCOLOR', (3, i), (3, i), colors.orange)
                        elif age_class == 'danger':
                            table_style.add('TEXTCOLOR', (3, i), (3, i), colors.red)
                    
                    table.setStyle(table_style)
                    story.append(table)
                else:
                    story.append(Paragraph("Keine Snapshot-Daten verfügbar", normal_style))
            
            elif section['id'] == 'orphaned_vmdks':
                # Tabelle für verwaiste VMDKs
                if section['data']:
                    data = [['Pfad', 'Datastore', 'Größe', 'Änderungsdatum']]
                    
                    # Füge Daten hinzu
                    for item in section['data']:
                        # Konvertiere KB in GB für die Anzeige
                        size_kb = item.get('size_kb', 0)
                        size_gb = size_kb / (1024 * 1024)
                        size_str = f"{size_gb:.2f} GB"
                        
                        data.append([
                            item.get('path', '-'),
                            item.get('datastore', '-'),
                            size_str,
                            item.get('modification_time', '-')
                        ])
                    
                    # Erstelle Tabelle
                    table = Table(data, colWidths=[180, 80, 80, 120])
                    
                    # Styling der Tabelle
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), bechtle_blue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ])
                    
                    table.setStyle(table_style)
                    story.append(table)
                else:
                    story.append(Paragraph("Keine verwaisten VMDK-Dateien gefunden", normal_style))
            
            story.append(Spacer(1, 24))
        
        # Fußzeile mit Version
        story.append(Paragraph(f"Generiert mit Bechtle vSphere Reporter v0.2", 
                    ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
        
        # Erstelle das PDF
        doc.build(story)
        
        logger.info(f"PDF-Bericht gespeichert unter: {file_path}")
        return file_path
    
    def _generate_docx_report(self, report_data, include_sections):
        """
        Generiert einen DOCX-Bericht mit python-docx
        
        Args:
            report_data (dict): Aufbereitete Daten für den Bericht
            include_sections (dict): Enthält die auszuwählenden Berichtsabschnitte
            
        Returns:
            str: Pfad zur generierten DOCX-Datei
        """
        logger.info("Generiere DOCX-Bericht...")
        
        # Erstelle ein neues Dokument
        document = Document()
        
        # Seitenränder anpassen
        sections = document.sections
        for section in sections:
            section.top_margin = Cm(2)
            section.bottom_margin = Cm(2)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)
        
        # Titel hinzufügen
        title = document.add_heading(report_data['title'], level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Metadaten hinzufügen
        document.add_paragraph(f"Erstellt am: {report_data['generated_at']}")
        document.add_paragraph(f"vCenter: {report_data['vcenter']}")
        
        if report_data['demo_mode']:
            demo_para = document.add_paragraph("DEMO-MODUS - Beispieldaten")
            for run in demo_para.runs:
                run.font.color.rgb = RGBColor(255, 0, 0)
        
        document.add_paragraph()  # Leerzeile
        
        # Bechtle Farben
        bechtle_blue = RGBColor(0, 53, 94)  # #00355e
        bechtle_orange = RGBColor(218, 111, 30)  # #da6f1e
        
        # Füge Abschnitte hinzu
        for section in report_data['sections']:
            # Abschnittstitel
            section_title = document.add_heading(section['title'], level=1)
            for run in section_title.runs:
                run.font.color.rgb = bechtle_blue
            
            # Je nach Abschnittstyp unterschiedliche Tabellen erstellen
            if section['id'] == 'vmware_tools':
                if section['data']:
                    # Erstelle Tabelle
                    table = document.add_table(rows=1, cols=4)
                    table.style = 'Table Grid'
                    
                    # Überschriftenzeile
                    header_cells = table.rows[0].cells
                    header_cells[0].text = 'VM-Name'
                    header_cells[1].text = 'Tools-Version'
                    header_cells[2].text = 'Status'
                    header_cells[3].text = 'Betriebssystem'
                    
                    # Formatiere Überschriftenzeile
                    for cell in header_cells:
                        cell.paragraphs[0].runs[0].font.bold = True
                        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                        cell._tc.get_or_add_tcPr().append(
                            document._element.makeelement(
                                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd',
                                {
                                    '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill': '00355e'
                                }
                            )
                        )
                    
                    # Füge Daten hinzu
                    for item in section['data']:
                        status_text = item.get('status_text', '')
                        running_text = item.get('running_text', '')
                        
                        if status_text and running_text:
                            status = f"{status_text} / {running_text}"
                        else:
                            status = status_text or running_text or '-'
                            
                        row_cells = table.add_row().cells
                        row_cells[0].text = item.get('name', '-')
                        row_cells[1].text = item.get('tools_version', '-')
                        row_cells[2].text = status
                        row_cells[3].text = item.get('os', '-')
                        
                        # Farbkodierung basierend auf Status
                        status_class = item.get('status_class', '')
                        status_run = row_cells[2].paragraphs[0].runs[0]
                        
                        if status_class == 'success':
                            status_run.font.color.rgb = RGBColor(0, 128, 0)  # Grün
                        elif status_class == 'warning':
                            status_run.font.color.rgb = RGBColor(255, 165, 0)  # Orange
                        elif status_class == 'danger':
                            status_run.font.color.rgb = RGBColor(255, 0, 0)  # Rot
                else:
                    document.add_paragraph("Keine VMware Tools Daten verfügbar")
            
            elif section['id'] == 'snapshots':
                if section['data']:
                    # Erstelle Tabelle
                    table = document.add_table(rows=1, cols=5)
                    table.style = 'Table Grid'
                    
                    # Überschriftenzeile
                    header_cells = table.rows[0].cells
                    header_cells[0].text = 'VM-Name'
                    header_cells[1].text = 'Snapshot-Name'
                    header_cells[2].text = 'Erstellungsdatum'
                    header_cells[3].text = 'Alter'
                    header_cells[4].text = 'Größe'
                    
                    # Formatiere Überschriftenzeile
                    for cell in header_cells:
                        cell.paragraphs[0].runs[0].font.bold = True
                        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                        cell._tc.get_or_add_tcPr().append(
                            document._element.makeelement(
                                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd',
                                {
                                    '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill': '00355e'
                                }
                            )
                        )
                    
                    # Füge Daten hinzu
                    for item in section['data']:
                        row_cells = table.add_row().cells
                        row_cells[0].text = item.get('vm_name', '-')
                        row_cells[1].text = item.get('name', '-')
                        row_cells[2].text = item.get('create_time_str', '-')
                        row_cells[3].text = item.get('age_str', '-')
                        row_cells[4].text = item.get('size_str', '-')
                        
                        # Farbkodierung basierend auf Alter
                        age_class = item.get('age_class', '')
                        age_run = row_cells[3].paragraphs[0].runs[0]
                        
                        if age_class == 'success':
                            age_run.font.color.rgb = RGBColor(0, 128, 0)  # Grün
                        elif age_class == 'warning':
                            age_run.font.color.rgb = RGBColor(255, 165, 0)  # Orange
                        elif age_class == 'danger':
                            age_run.font.color.rgb = RGBColor(255, 0, 0)  # Rot
                else:
                    document.add_paragraph("Keine Snapshot-Daten verfügbar")
            
            elif section['id'] == 'orphaned_vmdks':
                if section['data']:
                    # Erstelle Tabelle
                    table = document.add_table(rows=1, cols=4)
                    table.style = 'Table Grid'
                    
                    # Überschriftenzeile
                    header_cells = table.rows[0].cells
                    header_cells[0].text = 'Pfad'
                    header_cells[1].text = 'Datastore'
                    header_cells[2].text = 'Größe'
                    header_cells[3].text = 'Änderungsdatum'
                    
                    # Formatiere Überschriftenzeile
                    for cell in header_cells:
                        cell.paragraphs[0].runs[0].font.bold = True
                        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                        cell._tc.get_or_add_tcPr().append(
                            document._element.makeelement(
                                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd',
                                {
                                    '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill': '00355e'
                                }
                            )
                        )
                    
                    # Füge Daten hinzu
                    for item in section['data']:
                        # Konvertiere KB in GB für die Anzeige
                        size_kb = item.get('size_kb', 0)
                        size_gb = size_kb / (1024 * 1024)
                        size_str = f"{size_gb:.2f} GB"
                        
                        row_cells = table.add_row().cells
                        row_cells[0].text = item.get('path', '-')
                        row_cells[1].text = item.get('datastore', '-')
                        row_cells[2].text = size_str
                        row_cells[3].text = item.get('modification_time', '-')
                else:
                    document.add_paragraph("Keine verwaisten VMDK-Dateien gefunden")
            
            document.add_paragraph()  # Leerzeile
        
        # Fußzeile mit Version
        footer = document.sections[0].footer
        footer_paragraph = footer.paragraphs[0]
        footer_paragraph.text = f"Generiert mit Bechtle vSphere Reporter v0.2"
        for run in footer_paragraph.runs:
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(90, 90, 90)  # Dark gray
        
        # Speichere das Dokument
        file_path = os.path.join(self.report_dir, f'vsphere_report_{self.timestamp}.docx')
        document.save(file_path)
        
        logger.info(f"DOCX-Bericht gespeichert unter: {file_path}")
        return file_path