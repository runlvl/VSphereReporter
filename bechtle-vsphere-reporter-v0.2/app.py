"""
Bechtle vSphere Reporter v0.2 - Erweiterte Visualisierung
Webbasierte Reporting-Lösung für VMware vSphere-Umgebungen mit verbesserter Infrastrukturvisualisierung

Eine professionelle Web-Anwendung für VMware vSphere-Umgebungen mit Fokus auf wichtige
Infrastrukturberichte: VMware Tools Status, Snapshot Management und VMDK-Datei-Analyse.
Diese Version erweitert die v0.1 um interaktive Topologie-Visualisierungen mit ECharts.js
und bietet ein verbessertes Dashboard mit Echtzeit-Infrastrukturdaten.

© 2025 Bechtle GmbH - Alle Rechte vorbehalten
"""

import os
import logging
import time
import json
import base64
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename

from vsphere_client import VSphereClient
from report_generator import ReportGenerator

# Konfiguration
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', 'False').lower() in ['true', '1', 't']
PORT = int(os.environ.get('VSPHERE_REPORTER_PORT', 5000))
VERSION = '0.2'
APP_NAME = 'Bechtle vSphere Reporter'

# Logging konfigurieren
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'vsphere_reporter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logger = logging.getLogger('vsphere_reporter')
logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Initialisiere Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Erstelle vSphere Client
vsphere_client = VSphereClient()

# Routen
@app.route('/')
def index():
    """Startseite / Login-Formular anzeigen"""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Verarbeitet Login-Anfragen"""
    if request.method == 'POST':
        server = request.form.get('server')
        username = request.form.get('username')
        password = request.form.get('password')
        ignore_ssl = 'ignore_ssl' in request.form
        
        if not server or not username or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'danger')
            return render_template('login.html', error='Bitte füllen Sie alle Felder aus.')
        
        logger.info(f"Verbindungsversuch zu {server} als {username}")
        
        # Demo-Modus ausschalten, da wir eine echte Verbindung herstellen
        vsphere_client.set_demo_mode(False)
        session['demo_mode'] = False
        
        # Verbindung zum vCenter herstellen
        success = vsphere_client.connect_to_server(
            host=server,
            username=username,
            password=password,
            disable_ssl_verification=ignore_ssl
        )
        
        if success:
            session['logged_in'] = True
            session['server'] = server
            session['username'] = username
            session['connection_info'] = vsphere_client.connection_info
            flash('Erfolgreich verbunden!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Verbindung fehlgeschlagen. Bitte überprüfen Sie Ihre Anmeldedaten.', 'danger')
            return render_template('login.html', error='Verbindung fehlgeschlagen. Bitte überprüfen Sie Ihre Anmeldedaten.')
    
    return render_template('login.html')

@app.route('/demo')
def demo_mode():
    """Aktiviert den Demo-Modus mit Beispieldaten"""
    session['logged_in'] = True
    session['server'] = 'demo.vcenter.local'
    session['username'] = 'demo@vsphere.local'
    session['demo_mode'] = True
    session['connection_info'] = {
        'host': 'demo.vcenter.local',
        'username': 'demo@vsphere.local',
        'disable_ssl_verification': True
    }
    
    # Demo-Modus im Client aktivieren
    vsphere_client.set_demo_mode(True)
    
    flash('Demo-Modus aktiviert. Alle Daten sind Beispieldaten.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Beendet die Session und trennt die vCenter-Verbindung"""
    if not session.get('demo_mode', False):
        vsphere_client.disconnect()
    
    session.clear()
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Hauptübersicht mit den verfügbaren Berichten"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    connection_info = session.get('connection_info')
    demo_mode = session.get('demo_mode', False)
    
    return render_template(
        'dashboard.html',
        connection_info=connection_info,
        demo_mode=demo_mode,
        vsphere_client=vsphere_client
    )

@app.route('/vmware-tools')
def vmware_tools():
    """Zeigt den VMware Tools Status-Bericht an"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    # Sammle Daten, wenn noch nicht vorhanden
    result = vsphere_client.collect_vmware_tools_status()
    
    # Verarbeite die Daten je nach Demo-Modus oder Echtdaten
    if isinstance(result, dict) and 'demo' in result:
        vmware_tools_data = result.get('data', [])
    else:
        vmware_tools_data = result
    
    return render_template(
        'vmware_tools.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        vmware_tools_data=vmware_tools_data
    )

@app.route('/snapshots')
def snapshots():
    """Zeigt den Snapshot-Bericht an"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    # Sammle Daten
    result = vsphere_client.collect_snapshot_info()
    
    # Verarbeite die Daten je nach Demo-Modus oder Echtdaten
    if isinstance(result, dict) and 'demo' in result:
        snapshots_data = result.get('data', [])
    else:
        snapshots_data = result
    
    return render_template(
        'snapshots.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        snapshots=snapshots_data
    )

@app.route('/orphaned-vmdks')
def orphaned_vmdks():
    """Zeigt den Bericht über verwaiste VMDKs an"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    # Sammle Daten, unabhängig vom Demo-Modus
    app.logger.info("Sammle VMDK-Daten...")
    raw_data = vsphere_client.collect_all_vmdk_files()
    
    # Einheitliche Verarbeitung für echte und Demo-Daten
    if isinstance(raw_data, dict):
        if 'demo' in raw_data:
            # Wir haben Demo-Daten
            app.logger.info("Demo-Modus erkannt, verwende Demo-Daten")
            orphaned_vmdks = raw_data.get('orphaned_vmdks', [])
        else:
            # Wir haben Echtdaten
            orphaned_vmdks = raw_data.get('orphaned_vmdks', [])
    else:
        # Fallback, wenn keine validen Daten verfügbar sind
        app.logger.warning("Keine validen VMDK-Daten verfügbar")
        orphaned_vmdks = []
    
    # Stellen Sie sicher, dass orphaned_vmdks eine Liste ist
    if not isinstance(orphaned_vmdks, list):
        app.logger.warning(f"Unerwarteter Typ für VMDK-Daten: {type(orphaned_vmdks)}")
        orphaned_vmdks = []
    
    app.logger.info(f"Anzahl gefundener verwaister VMDKs: {len(orphaned_vmdks)}")
    
    # Debug-Logging der ersten VMDKs falls vorhanden
    if orphaned_vmdks:
        app.logger.info(f"Anzeige von {len(orphaned_vmdks)} verwaisten VMDKs")
        for i, vmdk in enumerate(orphaned_vmdks[:2]):  # Zeige nur erste 2 Einträge zur Vermeidung zu großer Logs
            app.logger.info(f"VMDK {i+1}: {vmdk.get('path', 'Unbekannt')} - {vmdk.get('size_kb', 0)/1024/1024:.2f} GB - {vmdk.get('modification_time', 'Unbekannt')}")
    else:
        app.logger.info("Keine verwaisten VMDKs gefunden oder im Dataset")
    
    return render_template(
        'orphaned_vmdks.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        orphaned_vmdks=orphaned_vmdks
    )

@app.route('/raw-data')
def raw_data():
    """Zeigt die Rohdaten für Debugging und Analyse an"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    # Sammle VMDK-Daten, wenn noch nicht vorhanden
    if not vsphere_client.collection_status['orphaned_vmdks']:
        raw_data = vsphere_client.collect_all_vmdk_files()
    else:
        raw_data = vsphere_client.raw_data
    
    return render_template(
        'raw_data.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        raw_data=raw_data
    )

@app.route('/about')
def about():
    """Zeigt Informationen über die Anwendung an"""
    return render_template(
        'about.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        version=VERSION
    )

@app.route('/downloads')
def downloads():
    """Zeigt die Download-Seite an"""
    return render_template(
        'downloads.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        version=VERSION
    )

# Neue Routen für Topologie- und Visualisierungsdaten
@app.route('/infrastructure-topology')
def infrastructure_topology():
    """Zeigt die Infrastruktur-Topologie-Visualisierung an"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    return render_template(
        'infrastructure_topology.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        version=VERSION
    )

@app.route('/api/topology-data')
def topology_data():
    """Stellt Topologiedaten im JSON-Format für die Visualisierung bereit"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'error': 'Nicht angemeldet'}), 401
    
    # In einer echten Implementierung würden hier Daten vom vSphere-Client abgerufen
    # Für die Demo verwenden wir Beispieldaten
    if session.get('demo_mode', False):
        # Beispieldaten für die Topologie
        topology_data = {
            "name": "vcenter.example.com",
            "value": "vCenter Server 7.0.3",
            "symbol": "rect",
            "symbolSize": 30,
            "itemStyle": {"color": "#00355e"},
            "children": [
                {
                    "name": "Bechtle Datacenter",
                    "symbol": "roundRect",
                    "symbolSize": 25,
                    "itemStyle": {"color": "#00355e"},
                    "children": [
                        {
                            "name": "Produktion-Cluster",
                            "value": "3 Hosts, 25 VMs",
                            "symbol": "diamond",
                            "symbolSize": 20,
                            "itemStyle": {"color": "#da6f1e"},
                            "children": [
                                {
                                    "name": "esx01.example.com",
                                    "value": "32 Cores, 256 GB RAM",
                                    "symbol": "circle",
                                    "symbolSize": 15,
                                    "itemStyle": {"color": "#23a96a"},
                                    "children": [
                                        {
                                            "name": "web01.example.com",
                                            "value": "4 vCPUs, 8 GB RAM, PoweredOn",
                                            "symbol": "emptyCircle",
                                            "symbolSize": 10,
                                            "itemStyle": {"color": "#5a5a5a"}
                                        },
                                        {
                                            "name": "web02.example.com",
                                            "value": "4 vCPUs, 8 GB RAM, PoweredOn",
                                            "symbol": "emptyCircle",
                                            "symbolSize": 10,
                                            "itemStyle": {"color": "#5a5a5a"}
                                        }
                                    ]
                                },
                                {
                                    "name": "esx02.example.com",
                                    "value": "32 Cores, 256 GB RAM",
                                    "symbol": "circle",
                                    "symbolSize": 15,
                                    "itemStyle": {"color": "#23a96a"},
                                    "children": [
                                        {
                                            "name": "db01.example.com",
                                            "value": "8 vCPUs, 32 GB RAM, PoweredOn",
                                            "symbol": "emptyCircle",
                                            "symbolSize": 10,
                                            "itemStyle": {"color": "#5a5a5a"}
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Test-Cluster",
                            "value": "2 Hosts, 10 VMs",
                            "symbol": "diamond",
                            "symbolSize": 20,
                            "itemStyle": {"color": "#da6f1e"},
                            "children": [
                                {
                                    "name": "esx03.example.com",
                                    "value": "16 Cores, 128 GB RAM",
                                    "symbol": "circle",
                                    "symbolSize": 15,
                                    "itemStyle": {"color": "#23a96a"}
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        return jsonify({"success": True, "data": topology_data})
    else:
        # Hier würde die Echtzeitdatensammlung implementiert
        # Für diese Version verwenden wir erstmal nur Demo-Daten
        return jsonify({"success": False, "error": "Echtzeit-Topologiedaten sind in dieser Version nur im Demo-Modus verfügbar"}), 500

# API Endpunkte für Datenaktualisierung
@app.route('/api/collect/vmware-tools', methods=['POST'])
def collect_vmware_tools_data():
    """Aktualisiert VMware Tools Daten über die API"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'error': 'Nicht angemeldet'}), 401
    
    try:
        vmware_tools_data = vsphere_client.collect_vmware_tools_status()
        return jsonify({'success': True, 'count': len(vmware_tools_data) if vmware_tools_data else 0})
    except Exception as e:
        logger.error(f"Fehler bei der Sammlung von VMware Tools Daten: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/collect/snapshots', methods=['POST'])
def collect_snapshot_data():
    """Aktualisiert Snapshot-Daten über die API"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'error': 'Nicht angemeldet'}), 401
    
    try:
        snapshots_data = vsphere_client.collect_snapshot_info()
        return jsonify({'success': True, 'count': len(snapshots_data) if snapshots_data else 0})
    except Exception as e:
        logger.error(f"Fehler bei der Sammlung von Snapshot-Daten: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/collect/vmdks', methods=['POST'])
def collect_vmdk_data():
    """Aktualisiert VMDK-Daten über die API"""
    if 'logged_in' not in session:
        return jsonify({'success': False, 'error': 'Nicht angemeldet'}), 401
    
    try:
        raw_data = vsphere_client.collect_all_vmdk_files()
        if raw_data and isinstance(raw_data, dict):
            # Überprüfe, ob es sich um Demo-Daten handelt
            if 'demo' in raw_data:
                orphaned_count = len(raw_data.get('orphaned_vmdks', []))
            else:
                orphaned_count = len(raw_data.get('orphaned_vmdks', []))
            return jsonify({'success': True, 'count': orphaned_count})
        else:
            return jsonify({'success': False, 'error': 'Ungültige Daten'}), 500
    except Exception as e:
        logger.error(f"Fehler bei der Sammlung von VMDK-Daten: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generiert einen Bericht basierend auf den ausgewählten Optionen"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    # Berichtsoptionen aus dem Formular lesen
    include_sections = {
        'vmware_tools': 'include_vmware_tools' in request.form,
        'snapshots': 'include_snapshots' in request.form,
        'orphaned_vmdks': 'include_orphaned_vmdks' in request.form
    }
    
    export_formats = {
        'html': 'export_html' in request.form,
        'pdf': 'export_pdf' in request.form,
        'docx': 'export_docx' in request.form
    }
    
    # Sicherstellen, dass mindestens ein Abschnitt ausgewählt ist
    if not any(include_sections.values()):
        flash('Bitte wählen Sie mindestens einen Berichtsabschnitt aus.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Sicherstellen, dass mindestens ein Format ausgewählt ist
    if not any(export_formats.values()):
        flash('Bitte wählen Sie mindestens ein Exportformat aus.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Daten sammeln, falls noch nicht erfolgt
    data = {}
    
    if include_sections.get('vmware_tools', False):
        if not vsphere_client.collection_status['vmware_tools']:
            vmware_tools_data = vsphere_client.collect_vmware_tools_status()
            if isinstance(vmware_tools_data, dict) and 'demo' in vmware_tools_data:
                data['vmware_tools'] = vmware_tools_data.get('data', [])
            else:
                data['vmware_tools'] = vmware_tools_data
        else:
            data['vmware_tools'] = vsphere_client.data.get('vmware_tools', [])
    
    if include_sections.get('snapshots', False):
        if not vsphere_client.collection_status['snapshots']:
            snapshots_data = vsphere_client.collect_snapshot_info()
            if isinstance(snapshots_data, dict) and 'demo' in snapshots_data:
                data['snapshots'] = snapshots_data.get('data', [])
            else:
                data['snapshots'] = snapshots_data
        else:
            data['snapshots'] = vsphere_client.data.get('snapshots', [])
    
    if include_sections.get('orphaned_vmdks', False):
        if not vsphere_client.collection_status['orphaned_vmdks']:
            raw_data = vsphere_client.collect_all_vmdk_files()
            if isinstance(raw_data, dict):
                if 'demo' in raw_data:
                    data['orphaned_vmdks'] = raw_data.get('orphaned_vmdks', [])
                else:
                    data['orphaned_vmdks'] = raw_data.get('orphaned_vmdks', [])
            else:
                data['orphaned_vmdks'] = []
        else:
            data['orphaned_vmdks'] = vsphere_client.data.get('orphaned_vmdks', [])
    
    # Report-Generator initialisieren
    report_generator = ReportGenerator(
        data=data,
        client=vsphere_client,
        demo_mode=session.get('demo_mode', False)
    )
    
    try:
        # Berichte generieren
        generated_files = report_generator.generate_report(
            include_sections=include_sections,
            export_formats=export_formats
        )
        
        # Bei nur einem Format, diesen direkt zum Download anbieten
        if len(generated_files) == 1:
            format_key = list(generated_files.keys())[0]
            file_path = generated_files[format_key]
            
            # Dateinamen für den Download sichern
            filename = os.path.basename(file_path)
            
            # MIME-Typ basierend auf Format
            mime_types = {
                'html': 'text/html',
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }
            
            return send_file(
                file_path,
                mimetype=mime_types.get(format_key, 'application/octet-stream'),
                as_attachment=True,
                download_name=filename
            )
        
        # Bei mehreren Formaten, zur Download-Übersicht weiterleiten
        # (In dieser Version noch nicht implementiert, stattdessen alle Formate nacheinander zum Download anbieten)
        else:
            # Speichern der generierten Dateien in der Session für den späteren Download
            session['generated_reports'] = generated_files
            
            format_names = {
                'html': 'HTML',
                'pdf': 'PDF',
                'docx': 'Word-Dokument'
            }
            
            success_message = "Bericht erfolgreich in folgenden Formaten generiert: "
            format_strings = [f"{format_names.get(fmt, fmt)}" for fmt in generated_files.keys()]
            success_message += ", ".join(format_strings)
            
            flash(success_message, 'success')
            
            # Weiterleitung zur Anzeige der generierten Berichte
            return redirect(url_for('download_reports'))
            
    except Exception as e:
        logger.error(f"Fehler bei der Berichterstellung: {str(e)}", exc_info=True)
        flash(f'Ein Fehler ist bei der Berichterstellung aufgetreten: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
        
@app.route('/download-reports')
def download_reports():
    """Zeigt Links zum Download der generierten Berichte an"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    if 'generated_reports' not in session or not session['generated_reports']:
        flash('Es wurden keine Berichte generiert oder die Session ist abgelaufen.', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template(
        'download_reports.html',
        connection_info=session.get('connection_info'),
        demo_mode=session.get('demo_mode', False),
        reports=session['generated_reports']
    )

@app.route('/download-report/<format>')
def download_report(format):
    """Ermöglicht den Download eines generierten Berichts"""
    if 'logged_in' not in session:
        flash('Bitte loggen Sie sich ein.', 'warning')
        return redirect(url_for('index'))
    
    if 'generated_reports' not in session or not session['generated_reports']:
        flash('Es wurden keine Berichte generiert oder die Session ist abgelaufen.', 'warning')
        return redirect(url_for('dashboard'))
    
    reports = session.get('generated_reports', {})
    
    if format not in reports:
        flash(f'Kein Bericht im Format {format} verfügbar.', 'danger')
        return redirect(url_for('download_reports'))
    
    file_path = reports[format]
    
    if not os.path.exists(file_path):
        flash(f'Berichtsdatei konnte nicht gefunden werden.', 'danger')
        return redirect(url_for('download_reports'))
    
    # Dateinamen für den Download sichern
    filename = os.path.basename(file_path)
    
    # MIME-Typ basierend auf Format
    mime_types = {
        'html': 'text/html',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    return send_file(
        file_path,
        mimetype=mime_types.get(format, 'application/octet-stream'),
        as_attachment=True,
        download_name=filename
    )

# Fehlerbehandlung
@app.errorhandler(404)
def page_not_found(e):
    """Behandelt 404 Fehler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Behandelt 500 Fehler"""
    logger.error(f"Serverfehler: {str(e)}")
    return render_template('500.html'), 500

# Hilfsfunktionen
def get_available_port(start_port=5000, max_attempts=10):
    """Findet einen verfügbaren Port für den Webserver"""
    import socket
    
    for attempt in range(max_attempts):
        port = start_port + attempt
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            continue
    
    return start_port

def main():
    """Haupteinstiegspunkt"""
    try:
        logger.info(f"Starte {APP_NAME} v{VERSION}...")
        port = get_available_port(PORT)
        if port != PORT:
            logger.info(f"Port {PORT} ist belegt, verwende Port {port}")
        
        logger.info(f"Starte {APP_NAME} v{VERSION} auf Port {port}...")
        app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}")

if __name__ == '__main__':
    main()