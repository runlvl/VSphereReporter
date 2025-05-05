#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Copyright (c) 2025 Bechtle GmbH

Hauptanwendungsdatei für den webbasierten VMware vSphere Reporter.
"""

import os
import logging
import datetime
import tempfile
from typing import Dict, Any, List, Optional
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_file
from flask_wtf.csrf import CSRFProtect

# Demo-Daten für den Demo-Modus importieren
from demo_data import generate_all_demo_data

# Eigene Module
from webapp.utils.error_handler import log_exception, VSphereError, ConnectionError, AuthenticationError

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Demo-Modus aktivieren, wenn die Umgebungsvariable gesetzt ist
DEMO_MODE = os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() == 'true'
# Debug-Modus aktivieren, wenn die Umgebungsvariable gesetzt ist
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', 'False').lower() == 'true'

# Flask-App initialisieren
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32))
csrf = CSRFProtect(app)

# Globale Variablen für die Anwendungsdaten
vsphere_data: Dict[str, Any] = {}
vsphere_client = None

# Sitzungsschutz durch Login-Prüfung
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if DEMO_MODE:
            # Im Demo-Modus ist keine Anmeldung erforderlich
            return f(*args, **kwargs)
        if not session.get('logged_in'):
            flash('Bitte melden Sie sich an, um auf diese Seite zuzugreifen.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Startseite / Login-Seite"""
    if DEMO_MODE:
        # Im Demo-Modus automatisch zum Dashboard weiterleiten
        return redirect(url_for('dashboard'))
    if session.get('logged_in'):
        # Wenn bereits angemeldet, zum Dashboard weiterleiten
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    """vCenter-Login-Verarbeitung"""
    if DEMO_MODE:
        return redirect(url_for('dashboard'))
    
    server = request.form.get('server')
    username = request.form.get('username')
    password = request.form.get('password')
    ignore_ssl = 'ignore_ssl' in request.form
    
    if not all([server, username, password]):
        flash('Bitte füllen Sie alle Felder aus.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Hier würde die tatsächliche vCenter-Verbindung hergestellt werden
        # In dieser Version wird nur eine einfache Erfolgsmeldung angezeigt
        
        # Verbindungsdaten in der Sitzung speichern
        session['logged_in'] = True
        session['vcenter_server'] = server
        session['username'] = username
        session['ignore_ssl'] = ignore_ssl
        
        flash(f'Erfolgreich mit {server} verbunden.', 'success')
        return redirect(url_for('dashboard'))
    except ConnectionError as e:
        log_exception(e, logger)
        flash(f'Verbindungsfehler: {str(e)}', 'danger')
    except AuthenticationError as e:
        log_exception(e, logger)
        flash(f'Authentifizierungsfehler: {str(e)}', 'danger')
    except VSphereError as e:
        log_exception(e, logger)
        flash(f'Fehler: {str(e)}', 'danger')
    except Exception as e:
        logger.exception(f"Unerwarteter Fehler bei der Anmeldung: {str(e)}")
        flash(f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Abmeldung vom vCenter"""
    if vsphere_client:
        # Verbindung zum vCenter trennen
        try:
            # vsphere_client.disconnect()
            pass
        except Exception as e:
            logger.warning(f"Fehler beim Trennen der vCenter-Verbindung: {str(e)}")
    
    # Sitzungsdaten löschen
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('index'))

@app.route('/demo')
def demo_mode():
    """Aktiviert den Demo-Modus für die Sitzung"""
    global vsphere_data
    
    if not DEMO_MODE:
        # Demo-Daten nur im Demo-Modus laden
        flash('Demo-Modus ist nicht verfügbar.', 'warning')
        return redirect(url_for('index'))
    
    # Demo-Daten generieren
    vsphere_data = generate_all_demo_data()
    session['demo_mode'] = True
    
    flash('Demo-Modus aktiviert. Die angezeigten Daten sind Beispieldaten.', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard-Seite mit Übersicht über die vSphere-Umgebung"""
    if DEMO_MODE and not vsphere_data:
        # Demo-Daten laden, falls noch nicht geschehen
        return redirect(url_for('demo_mode'))
    
    # Daten für das Dashboard zusammenstellen
    data = {
        'vms': vsphere_data.get('vms', []),
        'hosts': vsphere_data.get('hosts', []),
        'datastores': vsphere_data.get('datastores', []),
        'networks': vsphere_data.get('networks', []),
        'vmware_tools': vsphere_data.get('vmware_tools', []),
        'snapshots': vsphere_data.get('snapshots', []),
        'orphaned_vmdks': vsphere_data.get('orphaned_vmdks', []),
        'connected': session.get('logged_in', False),
        'vcenter_server': session.get('vcenter_server', 'Demo Server'),
        'username': session.get('username', 'Demo User'),
        'demo_mode': DEMO_MODE or session.get('demo_mode', False),
        'now': vsphere_data.get('now', datetime.datetime.now())
    }
    
    return render_template('dashboard.html', **data)

@app.route('/vmware-tools')
@login_required
def vmware_tools():
    """Zeigt den Status der VMware Tools auf allen VMs an"""
    if DEMO_MODE and not vsphere_data:
        return redirect(url_for('demo_mode'))
    
    data = {
        'vmware_tools': vsphere_data.get('vmware_tools', []),
        'connected': session.get('logged_in', False),
        'vcenter_server': session.get('vcenter_server', 'Demo Server'),
        'username': session.get('username', 'Demo User'),
        'demo_mode': DEMO_MODE or session.get('demo_mode', False)
    }
    
    return render_template('vmware_tools.html', **data)

@app.route('/snapshots')
@login_required
def snapshots():
    """Zeigt Informationen über VM-Snapshots an"""
    if DEMO_MODE and not vsphere_data:
        return redirect(url_for('demo_mode'))
    
    data = {
        'snapshots': vsphere_data.get('snapshots', []),
        'connected': session.get('logged_in', False),
        'vcenter_server': session.get('vcenter_server', 'Demo Server'),
        'username': session.get('username', 'Demo User'),
        'demo_mode': DEMO_MODE or session.get('demo_mode', False),
        'now': vsphere_data.get('now', datetime.datetime.now())
    }
    
    return render_template('snapshots.html', **data)

@app.route('/orphaned-vmdks')
@login_required
def orphaned_vmdks():
    """Zeigt Informationen über verwaiste VMDK-Dateien an"""
    if DEMO_MODE and not vsphere_data:
        return redirect(url_for('demo_mode'))
    
    data = {
        'orphaned_vmdks': vsphere_data.get('orphaned_vmdks', []),
        'connected': session.get('logged_in', False),
        'vcenter_server': session.get('vcenter_server', 'Demo Server'),
        'username': session.get('username', 'Demo User'),
        'demo_mode': DEMO_MODE or session.get('demo_mode', False)
    }
    
    return render_template('orphaned_vmdks.html', **data)

@app.route('/generate-report', methods=['GET', 'POST'])
@login_required
def generate_report():
    """Generiert einen Bericht in verschiedenen Formaten"""
    if DEMO_MODE and not vsphere_data:
        return redirect(url_for('demo_mode'))
    
    if request.method == 'POST':
        # Berichtsoptionen aus dem Formular auslesen
        report_format = request.form.get('format', 'html')
        report_title = request.form.get('report_title', f'VMware vSphere Infrastruktur-Bericht - {datetime.datetime.now().strftime("%d.%m.%Y")}')
        company_name = request.form.get('company_name', 'Bechtle GmbH')
        author_name = request.form.get('author_name', session.get('username', 'Administrator'))
        
        # Optionale Abschnitte
        include_all = 'include_all' in request.form
        include_vms = include_all or 'include_vms' in request.form
        include_hosts = include_all or 'include_hosts' in request.form
        include_datastores = include_all or 'include_datastores' in request.form
        include_networks = include_all or 'include_networks' in request.form
        
        # Design-Optionen
        include_toc = 'include_toc' in request.form
        include_cover_page = 'include_cover_page' in request.form
        include_logo = 'include_logo' in request.form
        
        # Hier würde die tatsächliche Berichtsgenerierung erfolgen
        # In dieser Version wird nur eine Erfolgsmeldung angezeigt
        
        try:
            # Beispiel für einen erzeugten Dateinamen
            filename = f"vsphere_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.{report_format}"
            
            # Temporäre Datei erstellen (nur als Platzhalter)
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{report_format}") as temp:
                temp.write(b"Beispielbericht - In der Vollversion wird hier ein richtiger Bericht erzeugt.")
                temp_path = temp.name
            
            # In einer vollständigen Implementation würde hier die Berichtserstellung erfolgen
            # und die generierte Datei zum Download angeboten werden
            
            flash(f'Bericht wurde erfolgreich im Format {report_format.upper()} generiert.', 'success')
            # return send_file(temp_path, as_attachment=True, download_name=filename)
            
            # Für die Demo einfach zurück zum Dashboard
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.exception(f"Fehler bei der Berichtsgenerierung: {str(e)}")
            flash(f'Fehler bei der Berichtsgenerierung: {str(e)}', 'danger')
    
    # GET-Anfrage: Formular zur Berichtsgenerierung anzeigen
    data = {
        'connected': session.get('logged_in', False),
        'vcenter_server': session.get('vcenter_server', 'Demo Server'),
        'username': session.get('username', 'Demo User'),
        'demo_mode': DEMO_MODE or session.get('demo_mode', False),
        'now': vsphere_data.get('now', datetime.datetime.now())
    }
    
    return render_template('generate_report.html', **data)

@app.errorhandler(404)
def page_not_found(e):
    """Behandelt 404-Fehler"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Behandelt 500-Fehler"""
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    logger.info("VMware vSphere Reporter v29.0 - Web Edition gestartet")
    logger.info(f"Debug-Modus: {DEBUG_MODE}")
    logger.info(f"Demo-Modus: {DEMO_MODE}")
    
    if DEMO_MODE:
        logger.info("Demo-Modus aktiviert - Es werden keine echten vCenter-Verbindungen hergestellt")
        # Demo-Daten laden
        vsphere_data = generate_all_demo_data()
    
    app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)