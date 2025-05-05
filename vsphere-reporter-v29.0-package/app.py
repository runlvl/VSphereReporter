#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Copyright (c) 2025 Bechtle GmbH

Eine webbasierte Anwendung für umfassende VMware vSphere-Berichterstattung.
"""

import os
import sys
import logging
import datetime
import json
import humanize
from pathlib import Path

# Import Flask-Framework
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash

# Import eigene Module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from webapp.utils.logger import setup_logger
from webapp.utils.error_handler import handle_vsphere_error, ConnectionError, AuthenticationError
from webapp.vsphere_client import VSphereClient
from webapp.data_collector import DataCollector
from webapp.direct_vmdk_collector import DirectVMDKCollector
from webapp.topology_generator import TopologyGenerator
from webapp.report_generator import ReportGenerator

# Konfiguration
APP_PORT = 5009  # Port auf 5009 geändert, um Konflikte zu vermeiden
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', 'False').lower() == 'true'
DEMO_MODE = os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() == 'true'

# Initialisiere Verzeichnisstruktur
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
STATIC_DIR = BASE_DIR / "static"
TOPOLOGY_DIR = STATIC_DIR / "topology"

# Erstelle Verzeichnisse, falls sie nicht existieren
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
TOPOLOGY_DIR.mkdir(exist_ok=True)

# Initialisiere Logger
logger = setup_logger(LOGS_DIR)
logger.info("VMware vSphere Reporter v29.0 - Web Edition gestartet")
logger.info(f"Debug-Modus: {DEBUG_MODE}")
logger.info(f"Demo-Modus: {DEMO_MODE}")

# Flask-App initialisieren
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'bechtle_vsphere_reporter_secure_key')
app.config['REPORTS_DIR'] = REPORTS_DIR
app.config['TOPOLOGY_DIR'] = TOPOLOGY_DIR
app.config['DEMO_MODE'] = DEMO_MODE
app.config['SESSION_PERMANENT'] = False

# Demo-Daten
if DEMO_MODE:
    from webapp.demo_data import generate_demo_data

# Route: Startseite
@app.route('/')
def index():
    # Prüfe, ob eine Verbindung bereits besteht
    if 'connected' in session and session['connected']:
        return redirect(url_for('report_options'))
    return render_template('index.html', demo_mode=app.config['DEMO_MODE'])

# Route: Verbindungsseite
@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        # Verbindungsdaten aus dem Formular holen
        server = request.form['server']
        username = request.form['username']
        password = request.form['password']
        ignore_ssl = 'ignore_ssl' in request.form
        
        try:
            # Wenn Demo-Modus aktiv ist, überspringen wir die tatsächliche Verbindung
            if app.config['DEMO_MODE']:
                session['connected'] = True
                session['server'] = server
                session['username'] = username
                session['demo_data'] = generate_demo_data()
                flash('Demo-Modus: Verbindung simuliert', 'info')
                return redirect(url_for('report_options'))
            
            # Verbindung zum vCenter herstellen
            client = VSphereClient(server, username, password, ignore_ssl)
            
            # Versuche zu verbinden und speichere das Ergebnis in der Session
            content = client.connect()
            session['connected'] = True
            session['server'] = server
            session['username'] = username
            session['password'] = password  # In der Praxis sollte dies verschlüsselt werden
            session['ignore_ssl'] = ignore_ssl
            
            # Erfolgreiche Verbindung
            flash(f'Erfolgreich mit {server} verbunden', 'success')
            return redirect(url_for('report_options'))
            
        except AuthenticationError as e:
            # Authentifizierungsfehler
            flash(f'Authentifizierungsfehler: {str(e)}', 'danger')
            logger.error(f"Authentifizierungsfehler: {str(e)}")
            
        except ConnectionError as e:
            # Verbindungsfehler
            flash(f'Verbindungsfehler: {str(e)}', 'danger')
            logger.error(f"Verbindungsfehler: {str(e)}")
            
        except Exception as e:
            # Allgemeiner Fehler
            flash(f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}', 'danger')
            logger.error(f"Unerwarteter Fehler bei der Verbindung: {str(e)}", exc_info=True)
    
    return render_template('connect.html', demo_mode=app.config['DEMO_MODE'])

# Route: Berichtsoptionen
@app.route('/report-options', methods=['GET', 'POST'])
def report_options():
    # Prüfe, ob eine Verbindung besteht
    if 'connected' not in session or not session['connected']:
        flash('Bitte stellen Sie zuerst eine Verbindung zum vCenter her', 'warning')
        return redirect(url_for('connect'))
    
    if request.method == 'POST':
        # Speichere die ausgewählten Optionen in der Session
        options = {
            'include_vmware_tools': 'include_vmware_tools' in request.form,
            'include_snapshots': 'include_snapshots' in request.form,
            'include_orphaned_vmdks': 'include_orphaned_vmdks' in request.form,
            'include_vms': 'include_vms' in request.form,
            'include_hosts': 'include_hosts' in request.form,
            'include_datastores': 'include_datastores' in request.form,
            'include_networks': 'include_networks' in request.form,
            'include_clusters': 'include_clusters' in request.form,
            'include_topology': 'include_topology' in request.form,
            'export_format': request.form.get('export_format', 'html')
        }
        
        session['report_options'] = options
        
        # Leite zur Berichtsgenerierung weiter
        return redirect(url_for('generate_report'))
    
    # Default-Optionen oder gespeicherte Optionen anzeigen
    options = session.get('report_options', {
        'include_vmware_tools': True,
        'include_snapshots': True,
        'include_orphaned_vmdks': True,
        'include_vms': False,
        'include_hosts': False,
        'include_datastores': False,
        'include_networks': False,
        'include_clusters': False,
        'include_topology': False,
        'export_format': 'html'
    })
    
    return render_template('report_options.html', options=options, demo_mode=app.config['DEMO_MODE'])

# Route: Berichtsgenerierung
@app.route('/generate-report')
def generate_report():
    # Prüfe, ob eine Verbindung besteht
    if 'connected' not in session or not session['connected']:
        flash('Bitte stellen Sie zuerst eine Verbindung zum vCenter her', 'warning')
        return redirect(url_for('connect'))
    
    # Prüfe, ob Berichtsoptionen ausgewählt wurden
    if 'report_options' not in session:
        flash('Bitte wählen Sie zuerst Berichtsoptionen aus', 'warning')
        return redirect(url_for('report_options'))
    
    options = session['report_options']
    
    # Generiere einen eindeutigen Berichtsnamen
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    server_name = session['server'].replace('.', '_').replace(':', '_')
    report_name = f"vsphere_report_{server_name}_{timestamp}"
    session['report_name'] = report_name
    
    # Initialisiere Statusinformationen
    status = {
        'stage': 'connecting',
        'progress': 0,
        'message': 'Verbinde mit vCenter...',
        'complete': False
    }
    session['report_status'] = status
    
    return redirect(url_for('report_status'))

# Route: Berichtsstatus (asynchrone Verarbeitung simulieren)
@app.route('/report-status')
def report_status():
    # Prüfe, ob eine Verbindung besteht
    if 'connected' not in session or not session['connected']:
        flash('Bitte stellen Sie zuerst eine Verbindung zum vCenter her', 'warning')
        return redirect(url_for('connect'))
    
    # Prüfe, ob Berichtsoptionen ausgewählt wurden
    if 'report_options' not in session:
        flash('Bitte wählen Sie zuerst Berichtsoptionen aus', 'warning')
        return redirect(url_for('report_options'))
    
    # Prüfe, ob ein Berichtsname definiert wurde
    if 'report_name' not in session:
        flash('Ein Fehler ist aufgetreten. Bitte starten Sie den Prozess erneut.', 'danger')
        return redirect(url_for('report_options'))
    
    options = session['report_options']
    report_name = session['report_name']
    
    # Im Demo-Modus verwenden wir Beispieldaten
    if app.config['DEMO_MODE']:
        # Simuliere Berichtsfortschritt (im echten Betrieb würde dies asynchron laufen)
        if 'report_status' in session:
            status = session['report_status']
            
            # Simuliere Fortschritt
            if status['stage'] == 'connecting':
                status = {'stage': 'collecting', 'progress': 20, 'message': 'Sammle Daten...', 'complete': False}
            elif status['stage'] == 'collecting':
                status = {'stage': 'processing', 'progress': 50, 'message': 'Verarbeite Daten...', 'complete': False}
            elif status['stage'] == 'processing':
                status = {'stage': 'generating', 'progress': 80, 'message': 'Generiere Bericht...', 'complete': False}
            elif status['stage'] == 'generating':
                export_format = options.get('export_format', 'html')
                status = {
                    'stage': 'complete', 
                    'progress': 100, 
                    'message': f'Bericht im {export_format.upper()}-Format erfolgreich erstellt!',
                    'complete': True,
                    'report_file': f"{report_name}.{export_format}",
                    'report_url': url_for('static', filename=f'reports/{report_name}.{export_format}')
                }
                
                # In einem echten System würden wir hier den Bericht mit den Demo-Daten erstellen
                # Für die Demo verwenden wir ein vorgefertigtes Beispiel
                if export_format == 'html':
                    # Beispiel-HTML-Report kopieren oder erstellen
                    pass
            
            session['report_status'] = status
            
            # Wenn der Bericht fertig ist, zur Ergebnisseite weiterleiten
            if status['complete']:
                return redirect(url_for('report_view'))
    else:
        # Echter Modus mit vCenter-Verbindung
        try:
            # Verbindung zum vCenter herstellen
            client = VSphereClient(
                session['server'], 
                session['username'], 
                session['password'], 
                session.get('ignore_ssl', False)
            )
            client.connect()
            
            # Datensammler initialisieren
            data_collector = DataCollector(client)
            
            # Status aktualisieren
            status = {'stage': 'collecting', 'progress': 20, 'message': 'Sammle Daten...', 'complete': False}
            session['report_status'] = status
            
            # Daten sammeln basierend auf den ausgewählten Optionen
            data = {}
            
            # Sammle VM-Daten, wenn erforderlich oder für andere Berichte benötigt
            if options.get('include_vms') or options.get('include_vmware_tools') or options.get('include_snapshots'):
                data['vms'] = data_collector.collect_vms()
            
            # Sammle Host-Daten, wenn erforderlich
            if options.get('include_hosts'):
                data['hosts'] = data_collector.collect_hosts()
            
            # Sammle Datastore-Daten, wenn erforderlich oder für verwaiste VMDKs benötigt
            if options.get('include_datastores') or options.get('include_orphaned_vmdks'):
                data['datastores'] = data_collector.collect_datastores()
            
            # Sammle Netzwerkdaten, wenn erforderlich
            if options.get('include_networks'):
                data['networks'] = data_collector.collect_networks()
            
            # Sammle VMware Tools-Daten, wenn erforderlich
            if options.get('include_vmware_tools'):
                data['vmware_tools'] = data_collector.collect_vmware_tools()
            
            # Sammle Snapshot-Daten, wenn erforderlich
            if options.get('include_snapshots'):
                data['snapshots'] = data_collector.collect_snapshots()
            
            # Sammle verwaiste VMDK-Daten, wenn erforderlich
            if options.get('include_orphaned_vmdks'):
                vmdk_collector = DirectVMDKCollector(client)
                data['orphaned_vmdks'] = vmdk_collector.collect_all_vmdks()
            
            # Status aktualisieren
            status = {'stage': 'processing', 'progress': 50, 'message': 'Verarbeite Daten...', 'complete': False}
            session['report_status'] = status
            
            # Topologie erstellen, wenn erforderlich
            if options.get('include_topology'):
                topology_generator = TopologyGenerator()
                topology_file = topology_generator.generate_infrastructure_topology(
                    data.get('vms', []),
                    data.get('hosts', []),
                    data.get('datastores', []),
                    data.get('networks', [])
                )
                data['topology_file'] = topology_file
            
            # Status aktualisieren
            status = {'stage': 'generating', 'progress': 80, 'message': 'Generiere Bericht...', 'complete': False}
            session['report_status'] = status
            
            # Bericht generieren
            export_format = options.get('export_format', 'html')
            report_generator = ReportGenerator(data_collector)
            report_file = report_generator.generate_report(
                report_name,
                REPORTS_DIR,
                export_format,
                data
            )
            
            if export_format == 'html':
                # Kopiere HTML-Bericht in den static/reports-Ordner für direkten Zugriff
                html_static_path = STATIC_DIR / 'reports'
                html_static_path.mkdir(exist_ok=True)
                
                # In einer echten Implementierung würden wir hier die Datei kopieren
                # shutil.copy(report_file, html_static_path / f"{report_name}.html")
                
                # Für das Demo-Setup setzen wir einfach den Pfad
                report_url = url_for('static', filename=f'reports/{report_name}.html')
            else:
                # Für andere Formate bieten wir einen Download-Link
                report_url = url_for('download_report', filename=f"{report_name}.{export_format}")
            
            # Status aktualisieren
            status = {
                'stage': 'complete', 
                'progress': 100, 
                'message': f'Bericht im {export_format.upper()}-Format erfolgreich erstellt!',
                'complete': True,
                'report_file': os.path.basename(report_file),
                'report_url': report_url
            }
            session['report_status'] = status
            
            # Verbindung trennen
            client.disconnect()
            
            # Zur Ergebnisseite weiterleiten
            return redirect(url_for('report_view'))
            
        except Exception as e:
            # Fehlerbehandlung
            logger.error(f"Fehler bei der Berichtsgenerierung: {str(e)}", exc_info=True)
            flash(f'Ein Fehler ist aufgetreten: {str(e)}', 'danger')
            
            # Status aktualisieren
            status = {
                'stage': 'error', 
                'progress': 0, 
                'message': f'Fehler: {str(e)}',
                'complete': False,
                'error': True
            }
            session['report_status'] = status
    
    # Berichtsstatus anzeigen
    return render_template('report_status.html', 
                          status=session.get('report_status', {}),
                          demo_mode=app.config['DEMO_MODE'])

# Route: Berichtsansicht
@app.route('/report-view')
def report_view():
    # Prüfe, ob eine Verbindung besteht
    if 'connected' not in session or not session['connected']:
        flash('Bitte stellen Sie zuerst eine Verbindung zum vCenter her', 'warning')
        return redirect(url_for('connect'))
    
    # Prüfe, ob ein Berichtsstatus vorhanden ist
    if 'report_status' not in session or not session['report_status'].get('complete', False):
        flash('Es wurde noch kein Bericht generiert', 'warning')
        return redirect(url_for('report_options'))
    
    status = session['report_status']
    options = session.get('report_options', {})
    
    return render_template('report_view.html', 
                          status=status,
                          options=options,
                          demo_mode=app.config['DEMO_MODE'])

# Route: Berichtsdownload
@app.route('/download-report/<filename>')
def download_report(filename):
    # Prüfe, ob eine Verbindung besteht
    if 'connected' not in session or not session['connected']:
        flash('Bitte stellen Sie zuerst eine Verbindung zum vCenter her', 'warning')
        return redirect(url_for('connect'))
    
    # Prüfe, ob ein Berichtsstatus vorhanden ist
    if 'report_status' not in session or not session['report_status'].get('complete', False):
        flash('Es wurde noch kein Bericht generiert', 'warning')
        return redirect(url_for('report_options'))
    
    # Im Demo-Modus geben wir eine Beispieldatei zurück
    if app.config['DEMO_MODE']:
        # Hier würden wir eine Demo-Datei zurückgeben
        pass
    
    # Sende die Berichtsdatei
    try:
        return send_file(
            str(REPORTS_DIR / filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Fehler beim Download des Berichts: {str(e)}", exc_info=True)
        flash(f'Ein Fehler ist aufgetreten: {str(e)}', 'danger')
        return redirect(url_for('report_view'))

# Route: Trennen
@app.route('/disconnect')
def disconnect():
    # Session zurücksetzen
    session.clear()
    flash('Erfolgreich vom vCenter getrennt', 'success')
    return redirect(url_for('index'))

# Fehlerseiten
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Seite nicht gefunden"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Interner Serverfehler"), 500

# Haupteinstiegspunkt
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=APP_PORT)
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}", exc_info=True)
        print(f"Fehler: {str(e)}")
        sys.exit(1)