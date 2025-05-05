#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Copyright (c) 2025 Bechtle GmbH

Dies ist die Hauptanwendungsdatei für die webbasierte Version des VMware vSphere Reporters.
Die Anwendung verwendet Flask als Web-Framework und bietet eine moderne, responsive
Benutzeroberfläche für die Erstellung von VMware vSphere-Berichten.
"""

import os
import sys
import logging
import json
import datetime
import tempfile
from pathlib import Path
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, abort

# Stellen Sie sicher, dass Pakete aus dem aktuellen Verzeichnis importiert werden können
if '.' not in sys.path:
    sys.path.append('.')

# Importiere die Anwendungsmodule
from webapp.vsphere_client import VSphereClient
from webapp.utils.error_handler import handle_vsphere_error, ConnectionError, AuthenticationError
from webapp.data_collector import DataCollector
from webapp.direct_vmdk_collector import DirectVMDKCollector
from webapp.topology_generator import TopologyGenerator
from webapp.report_generator import ReportGenerator

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Prüfe, ob Demo-Modus aktiviert ist
DEMO_MODE = os.environ.get('VSPHERE_REPORTER_DEMO', 'false').lower() == 'true'
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', 'false').lower() == 'true'

if DEBUG_MODE:
    logging.getLogger().setLevel(logging.DEBUG)
    logger.debug("Debug-Modus aktiviert")

if DEMO_MODE:
    logger.info("Demo-Modus aktiviert - Es werden keine echten vCenter-Verbindungen hergestellt")
    from demo_data import (get_demo_vms, get_demo_hosts, get_demo_datastores, 
                          get_demo_networks, get_demo_vmware_tools, 
                          get_demo_snapshots, get_demo_orphaned_vmdks,
                          get_demo_clusters, get_demo_datacenters)

# Erstelle die Flask-Anwendung
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Einfache Sitzungsverwaltung
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=2)

# Hilfsfunktion zur Prüfung, ob Benutzer angemeldet ist
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('connected'):
            flash('Bitte melden Sie sich zuerst an einem vCenter an', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routen für die Weboberfläche
@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html', title="Startseite", demo_mode=DEMO_MODE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Anmeldeseite"""
    if request.method == 'POST':
        host = request.form.get('host')
        username = request.form.get('username')
        password = request.form.get('password')
        ignore_ssl = 'ignore_ssl' in request.form
        
        if not host or not username or not password:
            flash('Bitte geben Sie alle erforderlichen Felder ein', 'danger')
            return render_template('connect.html', title="Anmelden", demo_mode=DEMO_MODE)
        
        try:
            if DEMO_MODE:
                # Im Demo-Modus keine echte Verbindung herstellen
                session['connected'] = True
                session['host'] = host
                session['username'] = username
                session['ignore_ssl'] = ignore_ssl
                flash(f'Demo-Verbindung zu {host} als {username} hergestellt', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Versuche, eine Verbindung herzustellen
                client = VSphereClient(host, username, password, ignore_ssl)
                client.connect()
                
                # Verbindung erfolgreich
                session['connected'] = True
                session['host'] = host
                session['username'] = username
                session['ignore_ssl'] = ignore_ssl
                flash(f'Verbindung zu {host} als {username} hergestellt', 'success')
                return redirect(url_for('dashboard'))
        
        except (ConnectionError, AuthenticationError) as e:
            flash(f'Verbindungsfehler: {str(e)}', 'danger')
            logger.error(f"Verbindungsfehler: {str(e)}")
        except Exception as e:
            flash(f'Unerwarteter Fehler: {str(e)}', 'danger')
            logger.exception("Unerwarteter Fehler bei der Verbindung")
    
    return render_template('connect.html', title="Anmelden", demo_mode=DEMO_MODE)

@app.route('/logout')
def logout():
    """Abmelden und Sitzung zurücksetzen"""
    if session.get('connected') and not DEMO_MODE:
        try:
            # Nur versuchen, die Verbindung zu trennen, wenn tatsächlich verbunden
            host = session.get('host')
            username = session.get('username')
            logger.info(f"Trenne Verbindung zu {host} als {username}")
        except Exception as e:
            logger.warning(f"Fehler beim Trennen der Verbindung: {str(e)}")
    
    # Sitzung löschen
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard mit Übersicht über die vSphere-Umgebung"""
    if DEMO_MODE:
        vms = get_demo_vms()
        hosts = get_demo_hosts()
        datastores = get_demo_datastores()
        networks = get_demo_networks()
        
        # Zähle Status
        vm_on = sum(1 for vm in vms if vm.get('power_state') == 'poweredOn')
        vm_off = sum(1 for vm in vms if vm.get('power_state') == 'poweredOff')
        host_connected = sum(1 for host in hosts if host.get('connection_state') == 'connected')
        hosts_in_maintenance = sum(1 for host in hosts if host.get('maintenance_mode'))
        
        # Berechne Speichernutzung
        total_storage_capacity = sum(ds.get('capacity', 0) for ds in datastores)
        used_storage = sum(ds.get('capacity', 0) - ds.get('free_space', 0) for ds in datastores)
        
        return render_template(
            'dashboard.html',
            title="Dashboard",
            demo_mode=DEMO_MODE,
            vm_count=len(vms),
            host_count=len(hosts),
            datastore_count=len(datastores),
            network_count=len(networks),
            vm_on=vm_on,
            vm_off=vm_off,
            host_connected=host_connected,
            hosts_in_maintenance=hosts_in_maintenance,
            total_storage_capacity=total_storage_capacity,
            used_storage=used_storage
        )
    else:
        try:
            # Echtzeit-Datenerfassung vom vSphere-Server
            client = VSphereClient(
                session.get('host'),
                session.get('username'),
                session.get('password', ''),  # Passwort sollte in einer echten Anwendung sicherer verwaltet werden
                session.get('ignore_ssl', False)
            )
            client.connect()
            
            data_collector = DataCollector(client)
            
            vms = data_collector.collect_vms()
            hosts = data_collector.collect_hosts()
            datastores = data_collector.collect_datastores()
            networks = data_collector.collect_networks()
            
            # Zähle Status
            vm_on = sum(1 for vm in vms if vm.get('power_state') == 'poweredOn')
            vm_off = sum(1 for vm in vms if vm.get('power_state') == 'poweredOff')
            host_connected = sum(1 for host in hosts if host.get('connection_state') == 'connected')
            hosts_in_maintenance = sum(1 for host in hosts if host.get('maintenance_mode'))
            
            # Berechne Speichernutzung
            total_storage_capacity = sum(ds.get('capacity', 0) for ds in datastores)
            used_storage = sum(ds.get('capacity', 0) - ds.get('free_space', 0) for ds in datastores)
            
            client.disconnect()
            
            return render_template(
                'dashboard.html',
                title="Dashboard",
                demo_mode=DEMO_MODE,
                vm_count=len(vms),
                host_count=len(hosts),
                datastore_count=len(datastores),
                network_count=len(networks),
                vm_on=vm_on,
                vm_off=vm_off,
                host_connected=host_connected,
                hosts_in_maintenance=hosts_in_maintenance,
                total_storage_capacity=total_storage_capacity,
                used_storage=used_storage
            )
        except Exception as e:
            flash(f'Fehler beim Laden des Dashboards: {str(e)}', 'danger')
            logger.exception("Fehler beim Laden des Dashboards")
            return redirect(url_for('index'))

@app.route('/vmware-tools')
@login_required
def vmware_tools():
    """VMware Tools-Bericht"""
    try:
        if DEMO_MODE:
            tools_info = get_demo_vmware_tools()
        else:
            client = VSphereClient(
                session.get('host'),
                session.get('username'),
                session.get('password', ''),
                session.get('ignore_ssl', False)
            )
            client.connect()
            
            data_collector = DataCollector(client)
            tools_info = data_collector.collect_vmware_tools_status()
            
            client.disconnect()
        
        # Sortiere nach Version (älteste zuerst)
        tools_info = sorted(tools_info, key=lambda x: x.get('version', '0.0.0'))
        
        return render_template(
            'vmware_tools.html',
            title="VMware Tools Status",
            demo_mode=DEMO_MODE,
            tools_info=tools_info
        )
    except Exception as e:
        flash(f'Fehler beim Laden der VMware Tools-Daten: {str(e)}', 'danger')
        logger.exception("Fehler beim Laden der VMware Tools-Daten")
        return redirect(url_for('dashboard'))

@app.route('/snapshots')
@login_required
def snapshots():
    """Snapshot-Bericht"""
    try:
        if DEMO_MODE:
            snapshots_info = get_demo_snapshots()
        else:
            client = VSphereClient(
                session.get('host'),
                session.get('username'),
                session.get('password', ''),
                session.get('ignore_ssl', False)
            )
            client.connect()
            
            data_collector = DataCollector(client)
            snapshots_info = data_collector.collect_snapshots()
            
            client.disconnect()
        
        # Sortiere nach Alter (älteste zuerst)
        snapshots_info = sorted(snapshots_info, key=lambda x: x.get('create_time', datetime.datetime.now()))
        
        return render_template(
            'snapshots.html',
            title="Snapshot-Bericht",
            demo_mode=DEMO_MODE,
            snapshots=snapshots_info
        )
    except Exception as e:
        flash(f'Fehler beim Laden der Snapshot-Daten: {str(e)}', 'danger')
        logger.exception("Fehler beim Laden der Snapshot-Daten")
        return redirect(url_for('dashboard'))

@app.route('/orphaned-vmdks')
@login_required
def orphaned_vmdks():
    """Bericht über verwaiste VMDK-Dateien"""
    try:
        if DEMO_MODE:
            orphaned_vmdks_info = get_demo_orphaned_vmdks()
        else:
            client = VSphereClient(
                session.get('host'),
                session.get('username'),
                session.get('password', ''),
                session.get('ignore_ssl', False)
            )
            client.connect()
            
            data_collector = DataCollector(client)
            direct_vmdk_collector = DirectVMDKCollector(client)
            
            # Verwenden des VM-zentrischen Ansatzes für bessere Genauigkeit
            vms = data_collector.collect_vms()
            datastores = data_collector.collect_datastores()
            orphaned_vmdks_info = direct_vmdk_collector.find_orphaned_vmdks(vms, datastores)
            
            client.disconnect()
        
        return render_template(
            'orphaned_vmdks.html',
            title="Verwaiste VMDK-Dateien",
            demo_mode=DEMO_MODE,
            orphaned_vmdks=orphaned_vmdks_info
        )
    except Exception as e:
        flash(f'Fehler beim Laden der VMDK-Daten: {str(e)}', 'danger')
        logger.exception("Fehler beim Laden der VMDK-Daten")
        return redirect(url_for('dashboard'))

@app.route('/generate-report', methods=['GET', 'POST'])
@login_required
def generate_report():
    """Generiere einen benutzerdefinierten Bericht"""
    if request.method == 'POST':
        include_vmware_tools = 'include_vmware_tools' in request.form
        include_snapshots = 'include_snapshots' in request.form
        include_orphaned_vmdks = 'include_orphaned_vmdks' in request.form
        include_topology = 'include_topology' in request.form
        export_format = request.form.get('export_format', 'html')
        
        if not any([include_vmware_tools, include_snapshots, include_orphaned_vmdks, include_topology]):
            flash('Bitte wählen Sie mindestens einen Berichtsinhalt aus', 'warning')
            return redirect(url_for('generate_report'))
        
        try:
            if DEMO_MODE:
                # Demo-Daten für den Bericht
                vmware_tools = get_demo_vmware_tools() if include_vmware_tools else []
                snapshots = get_demo_snapshots() if include_snapshots else []
                orphaned_vmdks = get_demo_orphaned_vmdks() if include_orphaned_vmdks else []
                
                # Sortieren
                vmware_tools = sorted(vmware_tools, key=lambda x: x.get('version', '0.0.0'))
                snapshots = sorted(snapshots, key=lambda x: x.get('create_time', datetime.datetime.now()))
                
                # Erzeuge Berichtsverzeichnis, falls es nicht existiert
                report_dir = Path('reports')
                report_dir.mkdir(exist_ok=True)
                
                # Erzeuge Zeitstempel für den Dateinamen
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Erstelle den Bericht basierend auf dem gewünschten Format
                if export_format == 'html':
                    report_file = report_dir / f'vsphere_report_{timestamp}.html'
                    # HTML-Bericht generieren...
                    
                elif export_format == 'pdf':
                    report_file = report_dir / f'vsphere_report_{timestamp}.pdf'
                    # PDF-Bericht generieren...
                    
                elif export_format == 'docx':
                    report_file = report_dir / f'vsphere_report_{timestamp}.docx'
                    # DOCX-Bericht generieren...
                
                # Erfolg melden
                flash(f'Bericht erfolgreich erstellt: {report_file.name}', 'success')
                
                # Datei zum Download anbieten
                return send_file(
                    report_file,
                    as_attachment=True,
                    download_name=report_file.name
                )
            
            else:
                # Echte Daten vom vCenter sammeln
                client = VSphereClient(
                    session.get('host'),
                    session.get('username'),
                    session.get('password', ''),
                    session.get('ignore_ssl', False)
                )
                client.connect()
                
                data_collector = DataCollector(client)
                direct_vmdk_collector = DirectVMDKCollector(client)
                topology_generator = TopologyGenerator(client)
                
                # Sammle Daten basierend auf den ausgewählten Optionen
                vms = data_collector.collect_vms()
                hosts = data_collector.collect_hosts() if include_topology else []
                datastores = data_collector.collect_datastores() if include_topology or include_orphaned_vmdks else []
                networks = data_collector.collect_networks() if include_topology else []
                
                vmware_tools = data_collector.collect_vmware_tools_status() if include_vmware_tools else []
                snapshots = data_collector.collect_snapshots() if include_snapshots else []
                
                # VM-zentrischer Ansatz für verwaiste VMDKs
                orphaned_vmdks = []
                if include_orphaned_vmdks:
                    orphaned_vmdks = direct_vmdk_collector.find_orphaned_vmdks(vms, datastores)
                
                # Sortieren
                vmware_tools = sorted(vmware_tools, key=lambda x: x.get('version', '0.0.0'))
                snapshots = sorted(snapshots, key=lambda x: x.get('create_time', datetime.datetime.now()))
                
                # Topologie generieren, wenn ausgewählt
                topology_file = None
                if include_topology:
                    topology_file = topology_generator.generate_infrastructure_topology(
                        vms, hosts, datastores, networks
                    )
                
                # Bericht generieren
                report_generator = ReportGenerator()
                report_file = report_generator.generate_report(
                    vsphere_client=client,
                    vms=vms,
                    hosts=hosts,
                    datastores=datastores,
                    networks=networks,
                    vmware_tools=vmware_tools,
                    snapshots=snapshots,
                    orphaned_vmdks=orphaned_vmdks,
                    topology_file=topology_file,
                    export_format=export_format
                )
                
                client.disconnect()
                
                # Erfolg melden
                flash(f'Bericht erfolgreich erstellt: {report_file.name}', 'success')
                
                # Datei zum Download anbieten
                return send_file(
                    report_file,
                    as_attachment=True,
                    download_name=report_file.name
                )
                
        except Exception as e:
            flash(f'Fehler bei der Berichtserstellung: {str(e)}', 'danger')
            logger.exception("Fehler bei der Berichtserstellung")
            return redirect(url_for('generate_report'))
    
    return render_template(
        'generate_report.html',
        title="Bericht erstellen",
        demo_mode=DEMO_MODE
    )

@app.route('/about')
def about():
    """Über-Seite mit Informationen zur Anwendung"""
    return render_template('about.html', title="Über", demo_mode=DEMO_MODE)

# Fehlerbehandlung
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html', title="Seite nicht gefunden", demo_mode=DEMO_MODE), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html', title="Serverfehler", demo_mode=DEMO_MODE), 500

# Haupteinstieg
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"VMware vSphere Reporter v29.0 - Web Edition gestartet")
    logger.info(f"Debug-Modus: {DEBUG_MODE}")
    logger.info(f"Demo-Modus: {DEMO_MODE}")
    app.run(host='0.0.0.0', port=port)