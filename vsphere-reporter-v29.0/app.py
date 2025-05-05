#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
------------------------------------------
Ein umfassendes Reporting-Tool für VMware vSphere-Umgebungen

Diese Datei ist der Haupteinstiegspunkt für die Webanwendung
und stellt die Flask-Routen und API-Endpunkte bereit.

Copyright (c) 2025 Bechtle GmbH
"""

import os
import logging
import time
import json
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash

from webapp.utils.logger import setup_logger
from webapp.vsphere_client import VSphereClient
from webapp.data_collector import DataCollector
from webapp.direct_vmdk_collector import DirectVMDKCollector
from webapp.topology_generator import TopologyGenerator
from webapp.report_generator import ReportGenerator

# Konfiguration
DEBUG = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
PORT = int(os.environ.get('PORT', 5000))
SESSION_TIMEOUT = 30 * 60  # 30 Minuten in Sekunden

# Flask-App initialisieren
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Sitzungsschlüssel für sichere Cookies
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = SESSION_TIMEOUT
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORT_FOLDER'] = 'reports'
app.config['LOG_FOLDER'] = 'logs'

# Stellen Sie sicher, dass Verzeichnisse existieren
for folder in [app.config['UPLOAD_FOLDER'], app.config['REPORT_FOLDER'], app.config['LOG_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Logger einrichten
logger = setup_logger('vsphere_reporter', app.config['LOG_FOLDER'], debug=DEBUG)
logger.info("VMware vSphere Reporter Web Edition v29.0 - Anwendung gestartet")

# Globale Variablen für den vSphere-Client
vsphere_client = None

@app.before_request
def check_session_timeout():
    """Überprüfen Sie, ob die Sitzung abgelaufen ist"""
    if 'last_activity' in session:
        now = time.time()
        last_activity = session.get('last_activity')
        if now - last_activity > SESSION_TIMEOUT:
            # Sitzung ist abgelaufen
            session.clear()
            return redirect(url_for('index'))
    session['last_activity'] = time.time()

@app.errorhandler(404)
def page_not_found(e):
    """404-Fehlerseite"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500-Fehlerseite"""
    return render_template('500.html'), 500

@app.route('/')
def index():
    """Hauptseite / Landingpage"""
    return render_template('index.html', connected=is_connected())

@app.route('/connect', methods=['GET', 'POST'])
def connect():
    """Verbindungsseite zum vCenter"""
    global vsphere_client
    
    # Wenn bereits verbunden, zur Optionsseite weiterleiten
    if is_connected():
        return redirect(url_for('options'))
    
    if request.method == 'POST':
        server = request.form.get('server')
        username = request.form.get('username')
        password = request.form.get('password')
        ignore_ssl = 'ignore_ssl' in request.form
        
        # Überprüfen Sie, ob alle erforderlichen Felder ausgefüllt sind
        if not all([server, username, password]):
            return render_template('connect.html', error="Bitte füllen Sie alle Felder aus")
        
        # Versuchen Sie, eine Verbindung zum vCenter herzustellen
        try:
            logger.info(f"Verbinde mit vCenter {server}...")
            vsphere_client = VSphereClient(server, username, password, ignore_ssl=ignore_ssl)
            vsphere_client.connect()
            # Speichern Sie die Verbindungsinformationen in der Sitzung
            session['server'] = server
            session['username'] = username
            session['connected'] = True
            logger.info(f"Verbindung zu {server} als {username} hergestellt")
            return redirect(url_for('options'))
        except Exception as e:
            logger.error(f"Verbindungsfehler: {str(e)}")
            return render_template('connect.html', error=f"Verbindungsfehler: {str(e)}")
    
    return render_template('connect.html')

@app.route('/disconnect')
def disconnect():
    """Vom vCenter trennen"""
    global vsphere_client
    if vsphere_client:
        try:
            vsphere_client.disconnect()
        except:
            pass
        vsphere_client = None
    
    # Sitzung löschen
    session.pop('server', None)
    session.pop('username', None)
    session.pop('connected', None)
    
    logger.info("Vom vCenter getrennt")
    return redirect(url_for('index'))

@app.route('/options', methods=['GET', 'POST'])
def options():
    """Berichtsoptionen Seite"""
    if not is_connected():
        return redirect(url_for('connect'))
    
    if request.method == 'POST':
        # Berichtoptionen aus dem Formular sammeln
        report_options = {
            'include_vm_list': 'include_vm_list' in request.form,
            'include_vm_details': 'include_vm_details' in request.form,
            'include_datastore_info': 'include_datastore_info' in request.form,
            'include_esxi_info': 'include_esxi_info' in request.form,
            'include_network_info': 'include_network_info' in request.form,
            'include_resource_pools': 'include_resource_pools' in request.form,
            'include_clusters': 'include_clusters' in request.form,
            'include_distributed_switches': 'include_distributed_switches' in request.form,
            'include_topology': 'include_topology' in request.form,
            'include_vmware_tools': 'include_vmware_tools' in request.form,
            'include_snapshots': 'include_snapshots' in request.form,
            'include_orphaned_vmdks': 'include_orphaned_vmdks' in request.form,
            'export_format': request.form.get('export_format', 'html')
        }
        
        # Berichtsoptionen in der Sitzung speichern
        session['report_options'] = report_options
        
        # Zur Berichtsgenerierungsseite weiterleiten
        return redirect(url_for('generate_report'))
    
    return render_template('options.html', connected=is_connected())

@app.route('/generate_report')
def generate_report():
    """Berichtsgenerierung starten"""
    if not is_connected():
        return redirect(url_for('connect'))
    
    if 'report_options' not in session:
        return redirect(url_for('options'))
    
    # Auf die Berichtsstatusseite weiterleiten, wo die Generierung über AJAX erfolgt
    return render_template('report_status.html', options=session['report_options'])

@app.route('/api/report/start', methods=['POST'])
def api_start_report():
    """API-Endpunkt zum Starten der Berichtsgenerierung"""
    if not is_connected():
        return jsonify({'success': False, 'error': 'Nicht mit vCenter verbunden'}), 403
    
    if 'report_options' not in session:
        return jsonify({'success': False, 'error': 'Keine Berichtsoptionen gefunden'}), 400
    
    # Eindeutige Berichts-ID generieren
    report_id = f"report_{int(time.time())}"
    session['current_report_id'] = report_id
    
    # Berichtspfad erstellen
    report_path = os.path.join(app.config['REPORT_FOLDER'], report_id)
    os.makedirs(report_path, exist_ok=True)
    
    try:
        # Datensammler initialisieren
        collector = DataCollector(vsphere_client)
        
        # VMDK-Sammler initialisieren, wenn erforderlich
        if session['report_options'].get('include_orphaned_vmdks', False):
            vmdk_collector = DirectVMDKCollector(vsphere_client)
        
        # Topologie-Generator initialisieren, wenn erforderlich
        if session['report_options'].get('include_topology', False):
            topology_generator = TopologyGenerator(vsphere_client)
        
        # Berichtsgenerator initialisieren
        report_generator = ReportGenerator(
            vsphere_client,
            collector,
            options=session['report_options'],
            output_dir=report_path
        )
        
        # Fortschrittsdatei initialisieren
        progress_file = os.path.join(report_path, 'progress.json')
        with open(progress_file, 'w') as f:
            json.dump({
                'status': 'initializing',
                'progress': 0,
                'message': 'Initialisiere Berichtsgenerierung...',
                'completed': False,
                'error': None
            }, f)
        
        # Berichtsgenerierung in einem separaten Thread starten
        import threading
        def generate_report_thread():
            try:
                # Datensammlung starten
                update_progress(report_id, 5, 'Sammle VM-Informationen...')
                vms = collector.collect_vms()
                
                update_progress(report_id, 15, 'Sammle Host-Informationen...')
                hosts = collector.collect_hosts()
                
                update_progress(report_id, 25, 'Sammle Datastore-Informationen...')
                datastores = collector.collect_datastores()
                
                update_progress(report_id, 35, 'Sammle Netzwerkinformationen...')
                networks = collector.collect_networks()
                
                # VMware Tools Information sammeln
                if session['report_options'].get('include_vmware_tools', False):
                    update_progress(report_id, 45, 'Sammle VMware Tools Informationen...')
                    vmware_tools = collector.collect_vmware_tools_status()
                else:
                    vmware_tools = []
                
                # Snapshot-Informationen sammeln
                if session['report_options'].get('include_snapshots', False):
                    update_progress(report_id, 55, 'Sammle Snapshot-Informationen...')
                    snapshots = collector.collect_snapshots()
                else:
                    snapshots = []
                
                # Verwaiste VMDK-Informationen sammeln
                if session['report_options'].get('include_orphaned_vmdks', False):
                    update_progress(report_id, 65, 'Sammle verwaiste VMDK-Informationen...')
                    orphaned_vmdks = vmdk_collector.collect_orphaned_vmdks()
                else:
                    orphaned_vmdks = []
                
                # Topologie generieren, wenn erforderlich
                if session['report_options'].get('include_topology', False):
                    update_progress(report_id, 75, 'Generiere Topologie-Diagramm...')
                    topology_html = topology_generator.generate_infrastructure_topology()
                else:
                    topology_html = ""
                
                # Bericht erstellen
                update_progress(report_id, 85, 'Erstelle Bericht...')
                export_format = session['report_options'].get('export_format', 'html')
                output_file = report_generator.generate_report(
                    vms, hosts, datastores, networks, 
                    vmware_tools, snapshots, orphaned_vmdks,
                    topology_html, export_format
                )
                
                # Berichtsgenerierung abgeschlossen
                update_progress(report_id, 100, 'Berichtsgenerierung abgeschlossen', completed=True, output_file=output_file)
            except Exception as e:
                logger.error(f"Fehler bei der Berichtsgenerierung: {str(e)}")
                error_message = str(e)
                update_progress(report_id, 0, f'Fehler: {error_message}', error=error_message)
        
        # Thread starten
        threading.Thread(target=generate_report_thread).start()
        
        return jsonify({
            'success': True, 
            'report_id': report_id,
            'message': 'Berichtsgenerierung gestartet'
        })
    
    except Exception as e:
        logger.error(f"Fehler beim Starten der Berichtsgenerierung: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/report/progress/<report_id>')
def api_report_progress(report_id):
    """API-Endpunkt zum Abfragen des Berichtsfortschritts"""
    if not is_connected():
        return jsonify({'success': False, 'error': 'Nicht mit vCenter verbunden'}), 403
    
    progress_file = os.path.join(app.config['REPORT_FOLDER'], report_id, 'progress.json')
    
    if not os.path.exists(progress_file):
        return jsonify({'success': False, 'error': 'Berichtsfortschritt nicht gefunden'}), 404
    
    try:
        with open(progress_file, 'r') as f:
            progress_data = json.load(f)
            return jsonify({'success': True, **progress_data})
    except Exception as e:
        logger.error(f"Fehler beim Lesen des Berichtsfortschritts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<report_id>/<filename>')
def download_report(report_id, filename):
    """Endpunkt zum Herunterladen des generierten Berichts"""
    if not is_connected():
        return redirect(url_for('connect'))
    
    report_file = os.path.join(app.config['REPORT_FOLDER'], report_id, filename)
    
    if not os.path.exists(report_file):
        return render_template('404.html', error="Die angeforderte Berichtsdatei wurde nicht gefunden."), 404
    
    # Bestimmen Sie den MIME-Typ basierend auf der Dateiendung
    mime_types = {
        'html': 'text/html',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'zip': 'application/zip'
    }
    
    extension = filename.split('.')[-1].lower()
    mime_type = mime_types.get(extension, 'application/octet-stream')
    
    return send_file(
        report_file,
        mimetype=mime_type,
        as_attachment=True,
        download_name=filename
    )

def update_progress(report_id, progress, message, completed=False, error=None, output_file=None):
    """Hilfsfunktion zum Aktualisieren der Fortschrittsdatei"""
    progress_file = os.path.join(app.config['REPORT_FOLDER'], report_id, 'progress.json')
    try:
        progress_data = {
            'status': 'completed' if completed else 'error' if error else 'in_progress',
            'progress': progress,
            'message': message,
            'completed': completed,
            'error': error,
            'output_file': output_file.split('/')[-1] if output_file else None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f)
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Berichtsfortschritts: {str(e)}")

def is_connected():
    """Überprüfen, ob der Client mit vCenter verbunden ist"""
    return vsphere_client is not None and session.get('connected', False)

if __name__ == '__main__':
    try:
        if DEBUG:
            logger.info(f"Starte Anwendung im Debug-Modus auf Port {PORT}")
            app.run(host='0.0.0.0', port=PORT, debug=True)
        else:
            logger.info(f"Starte Anwendung auf Port {PORT}")
            # Verwenden Sie Waitress für die Produktion
            from waitress import serve
            serve(app, host='0.0.0.0', port=PORT, threads=8)
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}")