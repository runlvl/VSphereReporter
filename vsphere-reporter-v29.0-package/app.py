#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Hauptanwendung (Flask)

Copyright (c) 2025 Bechtle GmbH
"""

import os
import uuid
import json
import logging
import threading
import time
from datetime import datetime

# Flask und Flask-Erweiterungen
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

# Import der eigenen Module
from webapp.vsphere_client import VSphereClient
from webapp.data_collector import DataCollector
from webapp.direct_vmdk_collector import DirectVMDKCollector
from webapp.topology_generator import TopologyGenerator
from webapp.report_generator import ReportGenerator
from webapp.utils.error_handler import friendly_error_message
from webapp.utils.logger import setup_logger

# Konfiguration
DEBUG = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
SECRET_KEY = os.environ.get('VSPHERE_REPORTER_SECRET_KEY', os.urandom(24))
REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

# Stellen Sie sicher, dass Verzeichnisse existieren
for directory in [REPORT_DIR, os.path.join(STATIC_DIR, 'topology'), LOG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Logger einrichten
logger = setup_logger('vsphere_reporter', LOG_DIR, DEBUG)

# Flask-Anwendung initialisieren
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['REPORT_DIR'] = REPORT_DIR

# Globale Variablen
vsphere_client = None
active_reports = {}  # Speichert aktive Berichtsgenerierungs-Prozesse

# Hilfsfunktionen
def is_connected():
    """Prüft, ob eine Verbindung zum vCenter besteht"""
    return vsphere_client is not None and vsphere_client.is_connected

def requires_connection(f):
    """Dekorator, der prüft, ob eine Verbindung besteht"""
    def decorated_function(*args, **kwargs):
        if not is_connected():
            return redirect(url_for('connect'))
        return f(*args, **kwargs)
    return decorated_function

# Routen: Allgemein
@app.route('/')
def index():
    """Startseite der Anwendung"""
    return render_template('index.html', connected=is_connected())

# Routen: Verbindung
@app.route('/connect', methods=['GET', 'POST'])
def connect():
    """Verbindungsseite mit Formular zur Eingabe der vCenter-Verbindungsdaten"""
    global vsphere_client
    
    if request.method == 'POST':
        server = request.form.get('server')
        username = request.form.get('username')
        password = request.form.get('password')
        ignore_ssl = 'ignore_ssl' in request.form
        
        # Verbindung zum vCenter herstellen
        try:
            vsphere_client = VSphereClient(server, username, password, ignore_ssl)
            vsphere_client.connect()
            
            # Verbindungsdaten in der Session speichern (nicht das Passwort!)
            session['connected'] = True
            session['server'] = server
            session['username'] = username
            
            logger.info(f"Erfolgreich verbunden mit vCenter {server} als {username}")
            return redirect(url_for('options'))
        except Exception as e:
            error_message = friendly_error_message(e)
            logger.error(f"Verbindungsfehler: {error_message}")
            return render_template('connect.html', error=error_message)
    
    return render_template('connect.html')

@app.route('/disconnect')
def disconnect():
    """Trennt die Verbindung zum vCenter"""
    global vsphere_client
    
    if vsphere_client and vsphere_client.is_connected:
        try:
            vsphere_client.disconnect()
        except Exception as e:
            logger.error(f"Fehler beim Trennen der Verbindung: {str(e)}")
    
    # Session zurücksetzen
    session.clear()
    vsphere_client = None
    
    return redirect(url_for('index'))

# Routen: Berichtsoptionen
@app.route('/options', methods=['GET', 'POST'])
@requires_connection
def options():
    """Seite zur Auswahl der Berichtsoptionen"""
    if request.method == 'POST':
        # Optionen aus dem Formular sammeln
        options = {
            'include_vmware_tools': 'include_vmware_tools' in request.form,
            'include_snapshots': 'include_snapshots' in request.form,
            'include_orphaned_vmdks': 'include_orphaned_vmdks' in request.form,
            'include_vm_list': 'include_vm_list' in request.form,
            'include_vm_details': 'include_vm_details' in request.form,
            'include_esxi_info': 'include_esxi_info' in request.form,
            'include_datastore_info': 'include_datastore_info' in request.form,
            'include_network_info': 'include_network_info' in request.form,
            'include_distributed_switches': 'include_distributed_switches' in request.form,
            'include_clusters': 'include_clusters' in request.form,
            'include_resource_pools': 'include_resource_pools' in request.form,
            'include_topology': 'include_topology' in request.form,
            'export_format': request.form.get('export_format', 'html')
        }
        
        # Optionen in der Session speichern
        session['report_options'] = options
        
        # Zur Berichtsgenerierungsseite weiterleiten
        return redirect(url_for('report_status'))
    
    return render_template('options.html')

# Routen: Berichtsgenerierung
@app.route('/report/status')
@requires_connection
def report_status():
    """Zeigt den Status der Berichtsgenerierung an"""
    options = session.get('report_options', {})
    return render_template('report_status.html', options=options)

@app.route('/report/view/<report_id>')
@requires_connection
def report_view(report_id):
    """Zeigt einen generierten Bericht an"""
    report_data = {}
    # In der echten Implementierung würden hier die Berichtsdaten geladen
    
    return render_template('report_view.html', report_id=report_id, report_data=report_data)

@app.route('/download/<report_id>/<filename>')
@requires_connection
def download_report(report_id, filename):
    """Lädt einen generierten Bericht herunter"""
    report_folder = os.path.join(REPORT_DIR, report_id)
    return send_from_directory(report_folder, filename, as_attachment=True)

# API-Routen
@app.route('/api/report/start', methods=['POST'])
@requires_connection
def api_start_report():
    """Startet die Berichtsgenerierung"""
    options = session.get('report_options', {})
    report_id = str(uuid.uuid4())
    report_folder = os.path.join(REPORT_DIR, report_id)
    
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    
    # Berichtsgenerierung in separatem Thread starten
    def generate_report_thread():
        try:
            # Statusdatei initialisieren
            status = {
                'report_id': report_id,
                'progress': 0,
                'message': 'Initialisiere Berichtsgenerierung...',
                'started_at': datetime.now().isoformat(),
                'completed': False,
                'success': True,
                'error': None,
                'output_file': None
            }
            save_report_status(report_id, status)
            
            # Datensammler initialisieren
            data_collector = DataCollector(vsphere_client)
            
            # 1. VMs sammeln
            update_report_status(report_id, {
                'progress': 10,
                'message': 'Sammle Informationen über virtuelle Maschinen...'
            })
            vms = data_collector.collect_vms()
            
            # 2. ESXi-Hosts sammeln
            update_report_status(report_id, {
                'progress': 20,
                'message': 'Sammle Informationen über ESXi-Hosts...'
            })
            hosts = data_collector.collect_hosts()
            
            # 3. Datastores sammeln
            update_report_status(report_id, {
                'progress': 30,
                'message': 'Sammle Informationen über Datastores...'
            })
            datastores = data_collector.collect_datastores()
            
            # 4. Netzwerke sammeln
            update_report_status(report_id, {
                'progress': 40,
                'message': 'Sammle Netzwerkinformationen...'
            })
            networks = data_collector.collect_networks()
            
            # 5. VMware Tools Status
            update_report_status(report_id, {
                'progress': 50,
                'message': 'Analysiere VMware Tools Status...'
            })
            if options.get('include_vmware_tools'):
                vmware_tools = data_collector.collect_vmware_tools_status()
            else:
                vmware_tools = []
            
            # 6. Snapshots
            update_report_status(report_id, {
                'progress': 60,
                'message': 'Sammle Snapshot-Informationen...'
            })
            if options.get('include_snapshots'):
                snapshots = data_collector.collect_snapshots()
            else:
                snapshots = []
            
            # 7. Verwaiste VMDKs
            update_report_status(report_id, {
                'progress': 70,
                'message': 'Suche nach verwaisten VMDK-Dateien...'
            })
            if options.get('include_orphaned_vmdks'):
                vmdk_collector = DirectVMDKCollector(vsphere_client)
                orphaned_vmdks = vmdk_collector.collect_orphaned_vmdks()
            else:
                orphaned_vmdks = []
            
            # 8. Infrastruktur-Topologie generieren
            update_report_status(report_id, {
                'progress': 80,
                'message': 'Generiere Infrastruktur-Topologie...'
            })
            if options.get('include_topology'):
                topology_generator = TopologyGenerator(vsphere_client)
                topology_file = topology_generator.generate_infrastructure_topology(report_folder)
            else:
                topology_file = None
            
            # 9. Bericht generieren
            update_report_status(report_id, {
                'progress': 90,
                'message': 'Erstelle Bericht...'
            })
            report_generator = ReportGenerator(
                vsphere_client=vsphere_client,
                vms=vms,
                hosts=hosts,
                datastores=datastores,
                networks=networks,
                vmware_tools=vmware_tools,
                snapshots=snapshots,
                orphaned_vmdks=orphaned_vmdks,
                topology_file=topology_file,
                export_format=options.get('export_format', 'html')
            )
            
            output_file = report_generator.generate_report(report_folder, options)
            
            # Abschluss
            update_report_status(report_id, {
                'progress': 100,
                'message': 'Bericht erfolgreich erstellt!',
                'completed': True,
                'success': True,
                'output_file': output_file
            })
            
            logger.info(f"Bericht {report_id} erfolgreich erstellt: {output_file}")
            
        except Exception as e:
            error_message = friendly_error_message(e)
            logger.error(f"Fehler bei der Berichtsgenerierung: {error_message}")
            logger.exception(e)
            
            update_report_status(report_id, {
                'progress': 0,
                'message': 'Fehler bei der Berichtsgenerierung',
                'completed': True,
                'success': False,
                'error': error_message
            })
    
    # Thread starten
    thread = threading.Thread(target=generate_report_thread)
    thread.daemon = True
    thread.start()
    
    active_reports[report_id] = {
        'thread': thread,
        'started_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'report_id': report_id,
        'message': 'Berichtsgenerierung gestartet'
    })

@app.route('/api/report/progress/<report_id>', methods=['GET'])
@requires_connection
def api_report_progress(report_id):
    """Gibt den aktuellen Fortschritt der Berichtsgenerierung zurück"""
    status_file = os.path.join(REPORT_DIR, report_id, 'status.json')
    
    if not os.path.exists(status_file):
        return jsonify({
            'success': False,
            'error': 'Bericht nicht gefunden'
        })
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        return jsonify({
            'success': True,
            **status
        })
    except Exception as e:
        logger.error(f"Fehler beim Lesen des Berichtsstatus: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Fehler beim Lesen des Berichtsstatus'
        })

def save_report_status(report_id, status):
    """Speichert den Status eines Berichts"""
    status_file = os.path.join(REPORT_DIR, report_id, 'status.json')
    
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Berichtsstatus: {str(e)}")

def update_report_status(report_id, update_data):
    """Aktualisiert den Status eines Berichts"""
    status_file = os.path.join(REPORT_DIR, report_id, 'status.json')
    
    try:
        # Aktuelle Statusdaten lesen
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        # Statusdaten aktualisieren
        status.update(update_data)
        
        # Aktualisierte Daten speichern
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Berichtsstatus: {str(e)}")

def cleanup_old_reports():
    """Bereinigt alte Berichte (älter als 7 Tage)"""
    # In der echten Implementierung würde hier eine Routine zum Löschen alter Berichte stehen
    pass

# Hilfsfunktion zum Bereinigen der Ressourcen beim Herunterfahren
def cleanup_resources():
    """Bereinigt Ressourcen beim Herunterfahren der Anwendung"""
    global vsphere_client
    
    if vsphere_client and vsphere_client.is_connected:
        try:
            vsphere_client.disconnect()
            logger.info("Verbindung zum vCenter getrennt")
        except Exception as e:
            logger.error(f"Fehler beim Trennen der Verbindung: {str(e)}")

# Anwendung starten, wenn direkt ausgeführt
if __name__ == '__main__':
    import atexit
    atexit.register(cleanup_resources)
    
    host = os.environ.get('VSPHERE_REPORTER_HOST', '0.0.0.0')
    port = int(os.environ.get('VSPHERE_REPORTER_PORT', 5000))
    
    logger.info(f"VMware vSphere Reporter v29.0 wird gestartet auf {host}:{port}")
    app.run(host=host, port=port, debug=DEBUG)