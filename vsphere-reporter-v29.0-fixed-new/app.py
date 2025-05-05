#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web-Anwendung

Dies ist die Hauptdatei der Flask-Anwendung, die alle Routen und
Funktionen für die Web-Oberfläche bereitstellt.

Copyright (c) 2025 Bechtle GmbH
"""

import os
import logging
import tempfile
from datetime import datetime
from functools import wraps

# Flask und Erweiterungen importieren
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file, jsonify, abort
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired

# Lokale Module importieren
import demo_data
from webapp.vsphere_client import VSphereClient
from webapp.report_generator_module import ReportGenerator
# from webapp.report_generator_module import ReportGenerator
from webapp.utils.error_handler import handle_vsphere_errors, VSphereReporterError

# Logging-Konfiguration
logger = logging.getLogger(__name__)

# App-Konfiguration
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vsphere-reporter-v29-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'vsphere-reporter-exports')
app.config['DEMO_MODE'] = os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't')
app.config['JSON_AS_ASCII'] = False  # Stellt sicher, dass JSON-Antworten Unicode-Zeichen korrekt verarbeiten
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Stelle sicher, dass das Export-Verzeichnis existiert
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# CSRF-Schutz aktivieren
csrf = CSRFProtect(app)

# Login-Formular definieren
class LoginForm(FlaskForm):
    server = StringField('vCenter-Server', validators=[DataRequired()])
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    ignore_ssl = BooleanField('SSL-Zertifikatsprüfung überspringen')

# vSphere-Client global verfügbar machen
vsphere_client = None

# Hilfsfunktionen

def login_required(f):
    """
    Decorator, der prüft, ob ein Benutzer angemeldet ist.
    Wenn nicht, wird er zur Anmeldeseite weitergeleitet.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated', False) and not app.config['DEMO_MODE']:
            flash('Bitte melden Sie sich an, um diese Seite aufzurufen.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routen

@app.route('/')
def index():
    """
    Startseite der Anwendung.
    Zeigt das Dashboard an, wenn der Benutzer angemeldet ist,
    ansonsten die Anmeldeseite.
    """
    if session.get('is_authenticated', False) or app.config['DEMO_MODE']:
        # Statistiken abrufen
        try:
            if app.config['DEMO_MODE']:
                stats = demo_data.get_dashboard_stats()
                charts = demo_data.get_dashboard_charts()
            else:
                # In einer Produktionsumgebung würden wir hier echte Daten abrufen
                stats = demo_data.get_dashboard_stats()
                charts = demo_data.get_dashboard_charts()
            
            return render_template('dashboard.html', 
                                stats=stats, 
                                charts=charts,
                                demo_mode=app.config['DEMO_MODE'])
        except Exception as e:
            logger.error(f"Fehler beim Laden des Dashboards: {e}")
            flash(f"Fehler beim Laden des Dashboards: {str(e)}", 'danger')
            return render_template('dashboard.html', 
                                stats={}, 
                                charts={},
                                demo_mode=app.config['DEMO_MODE'])
    else:
        return redirect(url_for('login'))

@app.route('/vmware-tools')
@login_required
def vmware_tools():
    """
    Zeigt den Status der VMware Tools für alle VMs an.
    """
    try:
        if app.config['DEMO_MODE']:
            vms_with_tools = demo_data.generate_vmware_tools_data(30)
        else:
            # In einer Produktionsumgebung würden wir hier echte Daten abrufen
            vms_with_tools = vsphere_client.get_vmware_tools_status()
        
        return render_template('vmware_tools.html', 
                            vms_with_tools=vms_with_tools,
                            demo_mode=app.config['DEMO_MODE'])
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der VMware Tools-Daten: {e}")
        flash(f"Fehler beim Abrufen der VMware Tools-Daten: {str(e)}", 'danger')
        return render_template('vmware_tools.html', 
                            vms_with_tools=[],
                            demo_mode=app.config['DEMO_MODE'])

@app.route('/snapshots')
@login_required
def snapshots():
    """
    Zeigt eine Liste aller VM-Snapshots an.
    """
    try:
        if app.config['DEMO_MODE']:
            snapshot_data = demo_data.generate_snapshots_data(20)
        else:
            # In einer Produktionsumgebung würden wir hier echte Daten abrufen
            snapshot_data = vsphere_client.get_snapshots()
        
        return render_template('snapshots.html', 
                            snapshots=snapshot_data,
                            demo_mode=app.config['DEMO_MODE'])
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Snapshot-Daten: {e}")
        flash(f"Fehler beim Abrufen der Snapshot-Daten: {str(e)}", 'danger')
        return render_template('snapshots.html', 
                            snapshots=[],
                            demo_mode=app.config['DEMO_MODE'])

@app.route('/orphaned-vmdks')
@login_required
def orphaned_vmdks():
    """
    Zeigt eine Liste aller verwaisten VMDK-Dateien an.
    """
    try:
        if app.config['DEMO_MODE']:
            vmdk_data = demo_data.generate_orphaned_vmdks_data(15)
            logger.info(f"Generierte {len(vmdk_data)} verwaiste VMDKs für Demo-Modus")
        else:
            # In einer Produktionsumgebung würden wir hier echte Daten abrufen
            vmdk_data = vsphere_client.get_orphaned_vmdks()
            logger.info(f"Abgerufene {len(vmdk_data)} verwaiste VMDKs vom vCenter")
        
        # Stelle sicher, dass vmdk_data nicht None ist
        if vmdk_data is None:
            vmdk_data = []
            logger.warning("Keine verwaisten VMDK-Daten gefunden, verwende leere Liste")
        
        return render_template('orphaned_vmdks.html', 
                            orphaned_vmdks=vmdk_data,
                            demo_mode=app.config['DEMO_MODE'])
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der verwaisten VMDK-Daten: {e}")
        flash(f"Fehler beim Abrufen der verwaisten VMDK-Daten: {str(e)}", 'danger')
        return render_template('orphaned_vmdks.html', 
                            orphaned_vmdks=[],
                            demo_mode=app.config['DEMO_MODE'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Anmeldeseite für die Verbindung zum vCenter.
    """
    form = LoginForm()
    
    if form.validate_on_submit():
        server = form.server.data
        username = form.username.data
        password = form.password.data
        ignore_ssl = form.ignore_ssl.data
        
        try:
            global vsphere_client
            vsphere_client = VSphereClient(server, username, password, ignore_ssl)
            vsphere_client.connect()
            
            # Anmeldedaten in der Session speichern
            session['is_authenticated'] = True
            session['vcenter_server'] = server
            session['username'] = username
            
            flash(f'Erfolgreich mit {server} verbunden.', 'success')
            return redirect(url_for('index'))
            
        except VSphereReporterError as e:
            flash(f'Verbindungsfehler: {str(e)}', 'danger')
            logger.error(f'Verbindungsfehler: {str(e)}')
            
        except Exception as e:
            flash(f'Unerwarteter Fehler: {str(e)}', 'danger')
            logger.error(f'Unerwarteter Fehler bei der Anmeldung: {str(e)}')
    
    # Demo-Modus für die Anzeige auf True setzen, damit der Button immer angezeigt wird
    return render_template('login.html', form=form, demo_mode=True)

@app.route('/demo-login')
def demo_login():
    """
    Aktiviert den Demo-Modus ohne vCenter-Verbindung.
    """
    # Demo-Modus aktivieren
    app.config['DEMO_MODE'] = True
    os.environ['VSPHERE_REPORTER_DEMO'] = 'True'
    
    # Session-Variablen setzen
    session['is_authenticated'] = True
    session['vcenter_server'] = 'Demo vCenter'
    session['username'] = 'demo-user@vsphere.local'
    
    # Stellen Sie sicher, dass vsphere_client auf None gesetzt ist, damit keine Fehler auftreten
    global vsphere_client
    vsphere_client = None
    
    logger.info("Demo-Modus aktiviert - vsphere_client auf None gesetzt")
    flash('Demo-Modus aktiviert. Sie verwenden simulierte Daten.', 'info')
    return redirect(url_for('index'))

@app.route('/disconnect')
def disconnect():
    """
    Trennt die Verbindung zum vCenter und meldet den Benutzer ab.
    """
    try:
        global vsphere_client
        if vsphere_client and not app.config['DEMO_MODE']:
            vsphere_client.disconnect()
            vsphere_client = None
    except Exception as e:
        logger.warning(f"Fehler beim Trennen der Verbindung: {e}")
    
    # Session zurücksetzen
    session.clear()
    
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('login'))

@app.route('/export/<format>')
@login_required
def export(format):
    """
    Exportiert alle Berichte in verschiedenen Formaten.
    
    Args:
        format (str): Das gewünschte Format (html, pdf, docx)
    """
    if format not in ['html', 'pdf', 'docx']:
        flash(f'Ungültiges Format: {format}', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Daten sammeln
        if app.config['DEMO_MODE']:
            vmware_tools = demo_data.generate_vmware_tools_data(30)
            snapshots = demo_data.generate_snapshots_data(20)
            orphaned_vmdks = demo_data.generate_orphaned_vmdks_data(15)
        else:
            vmware_tools = vsphere_client.get_vmware_tools_status()
            snapshots = vsphere_client.get_snapshots()
            orphaned_vmdks = vsphere_client.get_orphaned_vmdks()
        
        # Report-Generator initialisieren mit benannten Parametern
        generator = ReportGenerator(
            output_dir=app.config['UPLOAD_FOLDER'], 
            vcenter_server=session.get('vcenter_server', 'Demo vCenter'),
            username=session.get('username', 'demo-user'),
            demo_mode=app.config['DEMO_MODE']
        )
        
        # Basierend auf dem Format exportieren
        # Für alle Formate die gleichen Daten
        data = {'vmware_tools': vmware_tools, 'snapshots': snapshots, 'orphaned_vmdks': orphaned_vmdks}
        
        # Generiere Dateinamen mit Zeitstempel
        filename = f"vsphere_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        # Basierend auf dem Format exportieren
        if format == 'html':
            report_file = generator.generate_html_report(filename, data)
            return send_file(report_file, as_attachment=True)
            
        elif format == 'pdf':
            report_file = generator.generate_pdf_report(filename, data)
            return send_file(report_file, as_attachment=True)
            
        elif format == 'docx':
            report_file = generator.generate_docx_report(filename, data)
            return send_file(report_file, as_attachment=True)
    
    except Exception as e:
        flash(f'Fehler beim Exportieren: {str(e)}', 'danger')
        logger.error(f"Fehler beim Exportieren im Format {format}: {str(e)}")
        return redirect(url_for('index'))

@app.route('/export-single/<report_type>/<format>')
@login_required
def export_single(report_type, format):
    """
    Exportiert einen einzelnen Bericht in verschiedenen Formaten.
    
    Args:
        report_type (str): Der Berichtstyp (vmware-tools, snapshots, orphaned-vmdks)
        format (str): Das gewünschte Format (html, pdf, docx)
    """
    if format not in ['html', 'pdf', 'docx']:
        flash(f'Ungültiges Format: {format}', 'danger')
        return redirect(url_for('index'))
    
    if report_type not in ['vmware-tools', 'snapshots', 'orphaned-vmdks']:
        flash(f'Ungültiger Berichtstyp: {report_type}', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Daten sammeln
        data = {}
        
        if report_type == 'vmware-tools':
            if app.config['DEMO_MODE']:
                data['vmware_tools'] = demo_data.generate_vmware_tools_data(30)
            else:
                data['vmware_tools'] = vsphere_client.get_vmware_tools_status()
        
        elif report_type == 'snapshots':
            if app.config['DEMO_MODE']:
                data['snapshots'] = demo_data.generate_snapshots_data(20)
            else:
                data['snapshots'] = vsphere_client.get_snapshots()
        
        elif report_type == 'orphaned-vmdks':
            if app.config['DEMO_MODE']:
                data['orphaned_vmdks'] = demo_data.generate_orphaned_vmdks_data(15)
            else:
                data['orphaned_vmdks'] = vsphere_client.get_orphaned_vmdks()
        
        # Report-Generator initialisieren mit benannten Parametern
        generator = ReportGenerator(
            output_dir=app.config['UPLOAD_FOLDER'], 
            vcenter_server=session.get('vcenter_server', 'Demo vCenter'),
            username=session.get('username', 'demo-user'),
            demo_mode=app.config['DEMO_MODE']
        )
        
        # Basierend auf dem Format exportieren
        filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format == 'html':
            report_file = generator.generate_html_report(filename, data)
            return send_file(report_file, as_attachment=True)
        elif format == 'pdf':
            report_file = generator.generate_pdf_report(filename, data)
            return send_file(report_file, as_attachment=True)
        elif format == 'docx':
            report_file = generator.generate_docx_report(filename, data)
            return send_file(report_file, as_attachment=True)
        
    except Exception as e:
        flash(f'Fehler beim Exportieren: {str(e)}', 'danger')
        logger.error(f"Fehler beim Exportieren von {report_type} im Format {format}: {str(e)}")
        return redirect(url_for(report_type.replace('-', '_')))

# Fehlerseitenhandler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', demo_mode=app.config['DEMO_MODE']), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', error_details=str(e), demo_mode=app.config['DEMO_MODE']), 500

# Nur zu Debugging-Zwecken
@app.route('/debug')
def debug():
    """
    Debug-Route, die nur verfügbar ist, wenn der Debug-Modus aktiviert ist.
    """
    if not app.debug:
        abort(404)
    
    # Debugging-Informationen sammeln
    debug_info = {
        'demo_mode': app.config['DEMO_MODE'],
        'authenticated': session.get('is_authenticated', False),
        'vcenter': session.get('vcenter_server', 'Nicht verbunden'),
        'username': session.get('username', 'Nicht angemeldet'),
        'client_connected': vsphere_client.connected if vsphere_client else False,
        'environment': {k: v for k, v in os.environ.items() if k.startswith('VSPHERE_')}
    }
    
    return jsonify(debug_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)