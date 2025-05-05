#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vereinfachter HTML-Exporter mit minimalen Abhängigkeiten
Dient als Fallback für den regulären HTML-Exporter bei Problemen
"""

import os
import datetime
import logging
import base64

# Logger konfigurieren
logger = logging.getLogger(__name__)

class SimpleHTMLExporter:
    """Vereinfachter Exporter für HTML-Berichte mit minimalen Abhängigkeiten"""
    
    def __init__(self, data, timestamp):
        """
        Initialisiere den vereinfachten HTML-Exporter
        
        Args:
            data (dict): Dictionary mit gesammelten vSphere-Daten
            timestamp (datetime): Zeitstempel für die Berichtserstellung
        """
        self.data = data
        self.timestamp = timestamp
        
        # Stelle sicher, dass alle erforderlichen Schlüssel vorhanden sind
        if not self.data:
            self.data = {}
        
        # Pflichtdaten
        if 'vmware_tools' not in self.data:
            self.data['vmware_tools'] = []
        if 'snapshots' not in self.data:
            self.data['snapshots'] = []
        if 'orphaned_vmdks' not in self.data:
            self.data['orphaned_vmdks'] = []
            
        # Logo-Pfad setzen (bevorzugt weißes Logo für Berichte)
        white_logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'images', 'logo_bechtle_white.png')
        regular_logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'images', 'logo_bechtle.png')
        
        # Bevorzugt das weiße Logo für Berichte, fallback auf das normale Logo
        if os.path.exists(white_logo_path):
            self.logo_path = white_logo_path
        else:
            self.logo_path = regular_logo_path
            
    def _format_size(self, size_bytes):
        """
        Formatiere Byteanzahl in menschenlesbare Größe
        
        Args:
            size_bytes: Größe in Bytes
            
        Returns:
            str: Formatierte Größe (z.B. "1.23 GB")
        """
        if size_bytes is None:
            return "Unbekannt"
            
        try:
            size_bytes = float(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} PB"
        except:
            return str(size_bytes)
            
    def _format_date(self, date_value):
        """
        Formatiere Datum
        
        Args:
            date_value: Datumswert
            
        Returns:
            str: Formatiertes Datum
        """
        if isinstance(date_value, datetime.datetime):
            return date_value.strftime('%Y-%m-%d')
        return str(date_value)
        
    def _format_datetime(self, dt_value):
        """
        Formatiere Datum und Uhrzeit
        
        Args:
            dt_value: Datums- und Uhrzeitwert
            
        Returns:
            str: Formatiertes Datum und Uhrzeit
        """
        if isinstance(dt_value, datetime.datetime):
            return dt_value.strftime('%Y-%m-%d %H:%M:%S')
        return str(dt_value)
        
    def _format_percent(self, value):
        """
        Formatiere Prozentwert
        
        Args:
            value: Prozentwert
            
        Returns:
            str: Formatierter Prozentwert
        """
        try:
            return f"{value:.2f}%"
        except:
            return str(value)
            
    def _get_sections(self):
        """
        Ermittle Berichtsabschnitte basierend auf verfügbaren Daten
        
        Returns:
            list: Liste von Abschnitts-Dictionaries
        """
        sections = []
        
        # VMware Tools-Abschnitt (Pflicht)
        sections.append({
            'id': 'vmware_tools',
            'title': 'VMware Tools Versionen',
            'description': 'VMware Tools-Versionen für alle virtuellen Maschinen, sortiert nach ältester Version zuerst.'
        })
        
        # Snapshots-Abschnitt (Pflicht)
        sections.append({
            'id': 'snapshots',
            'title': 'VM-Snapshots',
            'description': 'Snapshots virtueller Maschinen, sortiert nach ältestem zuerst.'
        })
        
        # Verwaiste VMDKs-Abschnitt (Pflicht)
        sections.append({
            'id': 'orphaned_vmdks',
            'title': 'Verwaiste VMDK-Dateien',
            'description': 'VMDK-Dateien, die verwaist zu sein scheinen oder keiner registrierten virtuellen Maschine zugeordnet sind.'
        })
            
        # Zusätzliche Abschnitte je nach Datenverfügbarkeit
        if 'vms' in self.data:
            sections.append({
                'id': 'vms',
                'title': 'Virtuelle Maschinen',
                'description': 'Übersicht aller virtuellen Maschinen in der Umgebung.'
            })
            
        if 'hosts' in self.data:
            sections.append({
                'id': 'hosts',
                'title': 'ESXi-Hosts',
                'description': 'Übersicht aller ESXi-Hosts in der Umgebung.'
            })
            
        if 'datastores' in self.data:
            sections.append({
                'id': 'datastores',
                'title': 'Datenspeicher',
                'description': 'Übersicht aller Datenspeicher in der Umgebung.'
            })
            
        if 'clusters' in self.data:
            sections.append({
                'id': 'clusters',
                'title': 'Cluster',
                'description': 'Übersicht aller Cluster in der Umgebung.'
            })
            
        if 'resource_pools' in self.data:
            sections.append({
                'id': 'resource_pools',
                'title': 'Ressourcenpools',
                'description': 'Übersicht aller Ressourcenpools in der Umgebung.'
            })
            
        if 'networks' in self.data:
            sections.append({
                'id': 'networks',
                'title': 'Netzwerke',
                'description': 'Übersicht aller Netzwerke in der Umgebung.'
            })
            
        return sections
        
    def _generate_basic_css(self):
        """
        Generiere grundlegendes CSS für den Bericht
        
        Returns:
            str: CSS-Styles
        """
        return """
        :root {
            --bechtle-dark-blue: #00355e;
            --bechtle-orange: #da6f1e;
            --bechtle-green: #23a96a;
            --bechtle-light-gray: #f3f3f3;
            --bechtle-dark-gray: #5a5a5a;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #fff;
            margin: 0;
            padding: 0;
        }
        
        a {
            color: var(--bechtle-dark-blue);
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        header {
            background-color: var(--bechtle-dark-blue);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
        }
        
        .logo {
            max-height: 50px;
            margin-right: 20px;
        }
        
        .header-title h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .header-title p {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .date-info {
            text-align: right;
            font-size: 14px;
        }
        
        .nav-fixed {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: var(--bechtle-dark-blue);
            color: white;
            padding: 10px 20px;
            z-index: 1000;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .nav-fixed .nav-title {
            font-weight: bold;
            flex: 1;
        }
        
        .nav-fixed .nav-links {
            display: flex;
            list-style-type: none;
        }
        
        .nav-fixed .nav-links li {
            margin: 0 10px;
        }
        
        .nav-fixed .nav-links a {
            color: rgba(255, 255, 255, 0.85);
            text-decoration: none;
            padding: 10px 5px;
        }
        
        .nav-fixed .nav-links a:hover, 
        .nav-fixed .nav-links a.active {
            color: white;
            border-bottom: 2px solid var(--bechtle-orange);
        }
        
        main {
            padding: 40px 0;
        }
        
        .section {
            margin-bottom: 40px;
            padding-top: 20px;
        }
        
        h2 {
            color: var(--bechtle-dark-blue);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--bechtle-light-gray);
        }
        
        h3 {
            color: var(--bechtle-dark-blue);
            margin: 15px 0;
        }
        
        p {
            margin-bottom: 15px;
        }
        
        .description {
            color: var(--bechtle-dark-gray);
            font-style: italic;
            margin-bottom: 25px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background-color: white;
        }
        
        th {
            background-color: var(--bechtle-dark-blue);
            color: white;
            text-align: left;
            padding: 12px 15px;
        }
        
        td {
            padding: 10px 15px;
            border-bottom: 1px solid var(--bechtle-light-gray);
        }
        
        tr:nth-child(even) {
            background-color: var(--bechtle-light-gray);
        }
        
        tr:hover {
            background-color: rgba(0, 53, 94, 0.05);
        }
        
        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        .alert-info {
            background-color: rgba(0, 53, 94, 0.1);
            border-left: 5px solid var(--bechtle-dark-blue);
        }
        
        .alert-warning {
            background-color: rgba(218, 111, 30, 0.1);
            border-left: 5px solid var(--bechtle-orange);
        }
        
        .alert-success {
            background-color: rgba(35, 169, 106, 0.1);
            border-left: 5px solid var(--bechtle-green);
        }
        
        footer {
            background-color: var(--bechtle-dark-blue);
            color: white;
            padding: 20px 0;
            margin-top: 40px;
        }
        
        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .footer-logo {
            max-height: 30px;
        }
        
        .footer-info {
            font-size: 12px;
            opacity: 0.8;
        }
        """
        
    def _generate_nav_links_html(self, sections):
        """
        Generiere HTML für die Navigationslinks
        
        Args:
            sections: Liste der Berichtsabschnitte
            
        Returns:
            str: HTML für die Navigationslinks
        """
        links_html = ""
        for section in sections:
            links_html += f'<li><a href="#{section["id"]}">{section["title"]}</a></li>\n'
        return links_html
        
    def _generate_vmware_tools_html(self):
        """
        Generiere HTML für den VMware Tools-Abschnitt
        
        Returns:
            str: HTML für den VMware Tools-Abschnitt
        """
        tools_html = """
        <h2>VMware Tools Versionen</h2>
        <p class="description">VMware Tools-Versionen für alle virtuellen Maschinen, sortiert nach ältester Version zuerst.</p>
        """
        
        if not self.data['vmware_tools']:
            tools_html += """
            <div class="alert alert-info">
                <p>Keine VMware Tools-Informationen verfügbar.</p>
            </div>
            """
            return tools_html
            
        tools_html += """
        <table>
            <thead>
                <tr>
                    <th>VM Name</th>
                    <th>VMware Tools Version</th>
                    <th>Status</th>
                    <th>Letzte Aktualisierung</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for vm in self.data['vmware_tools']:
            tools_html += f"""
            <tr>
                <td>{vm.get('name', 'Unbekannt')}</td>
                <td>{vm.get('tools_version', 'Unbekannt')}</td>
                <td>{vm.get('tools_status', 'Unbekannt')}</td>
                <td>{self._format_date(vm.get('tools_update_time', 'Unbekannt'))}</td>
            </tr>
            """
            
        tools_html += """
            </tbody>
        </table>
        """
        
        return tools_html
        
    def _generate_snapshots_html(self):
        """
        Generiere HTML für den Snapshots-Abschnitt
        
        Returns:
            str: HTML für den Snapshots-Abschnitt
        """
        snapshots_html = """
        <h2>VM-Snapshots</h2>
        <p class="description">Snapshots virtueller Maschinen, sortiert nach ältestem zuerst.</p>
        """
        
        if not self.data['snapshots']:
            snapshots_html += """
            <div class="alert alert-success">
                <p>Keine Snapshots gefunden. Ihre Umgebung entspricht den Best Practices ohne langfristige Snapshots.</p>
            </div>
            """
        else:
            snapshots_html += """
            <table>
                <thead>
                    <tr>
                        <th>VM Name</th>
                        <th>Snapshot Name</th>
                        <th>Erstellt am</th>
                        <th>Alter</th>
                        <th>Größe</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for snapshot in self.data['snapshots']:
                snapshots_html += f"""
                <tr>
                    <td>{snapshot.get('vm_name', 'Unbekannt')}</td>
                    <td>{snapshot.get('name', 'Unbekannt')}</td>
                    <td>{self._format_datetime(snapshot.get('created', 'Unbekannt'))}</td>
                    <td>{snapshot.get('age_days', 'Unbekannt')} Tage</td>
                    <td>{self._format_size(snapshot.get('size_bytes', 'Unbekannt'))}</td>
                </tr>
                """
                
            snapshots_html += """
                </tbody>
            </table>
            """
            
        snapshots_html += """
        <div class="alert alert-warning">
            <p><strong>Hinweis:</strong> VMware empfiehlt, Snapshots nur kurzfristig zu verwenden und keine Snapshots älter als 72 Stunden zu behalten. Langfristige Snapshots können zu Performance-Problemen und erhöhtem Speicherverbrauch führen.</p>
        </div>
        """
        
        return snapshots_html
        
    def _generate_orphaned_vmdks_html(self):
        """
        Generiere HTML für den Verwaiste VMDKs-Abschnitt
        
        Returns:
            str: HTML für den Verwaiste VMDKs-Abschnitt
        """
        orphaned_html = """
        <h2>Verwaiste VMDK-Dateien</h2>
        <p class="description">VMDK-Dateien, die verwaist zu sein scheinen oder keiner registrierten virtuellen Maschine zugeordnet sind.</p>
        """
        
        if not self.data['orphaned_vmdks']:
            orphaned_html += """
            <div class="alert alert-success">
                <p>Keine verwaisten VMDK-Dateien gefunden. Alle Festplattendateien sind ordnungsgemäß zugeordnet.</p>
            </div>
            """
        else:
            orphaned_html += """
            <table>
                <thead>
                    <tr>
                        <th>Datastore</th>
                        <th>Pfad</th>
                        <th>Größe</th>
                        <th>Geändert am</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for vmdk in self.data['orphaned_vmdks']:
                orphaned_html += f"""
                <tr>
                    <td>{vmdk.get('datastore', 'Unbekannt')}</td>
                    <td>{vmdk.get('path', 'Unbekannt')}</td>
                    <td>{self._format_size(vmdk.get('size', 'Unbekannt'))}</td>
                    <td>{self._format_datetime(vmdk.get('modified', 'Unbekannt'))}</td>
                </tr>
                """
                
            orphaned_html += """
                </tbody>
            </table>
            """
            
        orphaned_html += """
        <div class="alert alert-info">
            <p><strong>Definition:</strong> Eine VMDK-Datei gilt als "verwaist", wenn sie keiner registrierten VM zugeordnet ist und kein Teil einer Template-VM ist.</p>
            <p><strong>Empfehlung:</strong> Prüfen Sie verwaiste VMDKs und entfernen Sie diese, wenn sie nicht mehr benötigt werden, um Speicherplatz freizugeben.</p>
        </div>
        """
        
        return orphaned_html
        
    def _generate_vms_html(self):
        """
        Generiere HTML für den VMs-Abschnitt
        
        Returns:
            str: HTML für den VMs-Abschnitt
        """
        if 'vms' not in self.data:
            return ""
            
        vms_html = """
        <h2>Virtuelle Maschinen</h2>
        <p class="description">Übersicht aller virtuellen Maschinen in der Umgebung.</p>
        """
        
        if not self.data['vms']:
            vms_html += """
            <div class="alert alert-info">
                <p>Keine VM-Informationen verfügbar.</p>
            </div>
            """
            return vms_html
            
        vms_html += """
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>CPU</th>
                    <th>RAM</th>
                    <th>Betriebssystem</th>
                    <th>Host</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for vm in self.data['vms']:
            vms_html += f"""
            <tr>
                <td>{vm.get('name', 'Unbekannt')}</td>
                <td>{vm.get('status', 'Unbekannt')}</td>
                <td>{vm.get('cpu', 'Unbekannt')} vCPU</td>
                <td>{self._format_size(vm.get('memory_mb', 'Unbekannt') * 1024 * 1024 if vm.get('memory_mb') else 'Unbekannt')}</td>
                <td>{vm.get('guest_os', 'Unbekannt')}</td>
                <td>{vm.get('host', 'Unbekannt')}</td>
            </tr>
            """
            
        vms_html += """
            </tbody>
        </table>
        """
        
        return vms_html
        
    def _generate_html(self):
        """
        Generiere den vollständigen HTML-Inhalt
        
        Returns:
            str: HTML-Inhalt
        """
        # Bereite Daten vor
        sections = self._get_sections()
        nav_links = self._generate_nav_links_html(sections)
        css = self._generate_basic_css()
        
        # Logo einbetten, falls vorhanden
        logo_data = None
        if os.path.exists(self.logo_path):
            try:
                with open(self.logo_path, 'rb') as logo_file:
                    logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
                logger.info(f"Logo erfolgreich geladen: {self.logo_path}")
            except Exception as e:
                logger.warning(f"Fehler beim Laden des Logos: {str(e)}")
        
        # JavaScript für die Navigation
        nav_script = """
        document.addEventListener('DOMContentLoaded', function() {
            const sections = document.querySelectorAll('section');
            const navLinks = document.querySelectorAll('.nav-links a');
            
            function setActiveLink() {
                let current = '';
                
                sections.forEach(section => {
                    const sectionTop = section.offsetTop - 100;
                    const sectionHeight = section.offsetHeight;
                    
                    if (window.pageYOffset >= sectionTop && window.pageYOffset < sectionTop + sectionHeight) {
                        current = '#' + section.getAttribute('id');
                    }
                });
                
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === current) {
                        link.classList.add('active');
                    }
                });
            }
            
            window.addEventListener('scroll', setActiveLink);
            setActiveLink();
            
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                });
            });
        });
        """
        
        # HTML-Header
        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VMware vSphere Environment Report</title>
    <style>
{css}
    </style>
</head>
<body>
    <!-- Feste Navigation -->
    <nav class="nav-fixed">
        <div class="nav-title">VMware vSphere Reporter</div>
        <ul class="nav-links">
{nav_links}
        </ul>
    </nav>
    
    <!-- Abstand für die feste Navigation -->
    <div style="height: 60px;"></div>

    <header>
        <div class="container header-content">
            <div class="logo-container">
                {f'<img src="data:image/png;base64,{logo_data}" alt="Bechtle Logo" class="logo">' if logo_data else ''}
                <div class="header-title">
                    <h1>VMware vSphere Environment Report</h1>
                    <p>Bechtle Cloud Solutions | Datacenter & Endpoint</p>
                </div>
            </div>
            <div class="date-info">
                <p>Erstellt am: {self._format_datetime(self.timestamp)}</p>
            </div>
        </div>
    </header>

    <main class="container">
        <div class="alert alert-info">
            <p>Dieser Bericht enthält eine Zusammenfassung Ihrer VMware vSphere-Umgebung mit Schwerpunkt auf wichtigen Metriken und potenziellen Problemstellen.</p>
        </div>
        """
        
        # Berichtsabschnitte
        for section in sections:
            html += f'\n        <section id="{section["id"]}" class="section">\n'
            
            if section['id'] == 'vmware_tools':
                html += self._generate_vmware_tools_html()
            elif section['id'] == 'snapshots':
                html += self._generate_snapshots_html()
            elif section['id'] == 'orphaned_vmdks':
                html += self._generate_orphaned_vmdks_html()
            elif section['id'] == 'vms':
                html += self._generate_vms_html()
                
            html += '\n        </section>\n'
            
        # Footer
        html += f"""
    </main>

    <footer>
        <div class="container footer-content">
            <div>
                {f'<img src="data:image/png;base64,{logo_data}" alt="Bechtle Logo" class="footer-logo">' if logo_data else ''}
            </div>
            <div class="footer-info">
                <p>© {self.timestamp.year} Bechtle GmbH. Alle Rechte vorbehalten.</p>
                <p>Erstellt mit VMware vSphere Reporter v23.0</p>
            </div>
        </div>
    </footer>

    <script>
{nav_script}
    </script>
</body>
</html>"""
        
        return html
        
    def export(self, output_path):
        """
        Exportiere Daten in eine HTML-Datei
        
        Args:
            output_path (str): Pfad zum Speichern der HTML-Datei
            
        Returns:
            bool: True, wenn der Export erfolgreich war
        """
        try:
            logger.info(f"Generiere vereinfachten HTML-Bericht: {output_path}")
            
            # Erstelle den HTML-Inhalt
            html_content = self._generate_html()
            
            # Schreibe die gerenderte HTML in eine Datei
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"HTML-Bericht erfolgreich generiert: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Exportieren als HTML: {str(e)}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return False