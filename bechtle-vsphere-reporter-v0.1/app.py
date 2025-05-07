#!/usr/bin/env python3
"""
Bechtle vSphere Reporter v0.1
Webanwendung für VMware vSphere-Berichte

Diese Datei ist der Haupteinstiegspunkt für die Anwendung.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory

# Eigene Module importieren
from vsphere_client import VSphereClient
from data_collector import DataCollector
from report_generator import ReportGenerator
from demo_data import get_demo_client, DemoDataCollector

# Konfiguration
DEFAULT_PORT = 5000
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
PORT = int(os.environ.get('VSPHERE_REPORTER_PORT', DEFAULT_PORT))

# Konfiguriere Logging
log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(log_dir, f'vsphere_reporter_{timestamp}.log')

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('vsphere_reporter')
logger.info(f"Bechtle vSphere Reporter v0.1 wird gestartet. Debug-Modus: {DEBUG_MODE}")

# Initialisierung der Flask-App
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')

# Stelle sicher, dass das Verzeichnis für Berichte existiert
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Globale Variablen für die Anwendung
vsphere_client = None
data_collector = None
report_generator = None

def require_login(f):
    """Decorator zum Überprüfen des Login-Status"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Bitte melden Sie sich an, um auf diese Seite zuzugreifen.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_demo_mode():
    """Initialisiert den Demo-Modus mit synthetischen Daten"""
    global vsphere_client, data_collector, report_generator
    vsphere_client = get_demo_client()
    data_collector = DemoDataCollector(vsphere_client)
    report_generator = ReportGenerator(data_collector)
    session['demo_mode'] = True
    session['logged_in'] = True
    session['server'] = vsphere_client.server
    session['username'] = vsphere_client.username
    logger.info("Demo-Modus aktiviert")

@app.route('/')
def index():
    """Dashboard-Ansicht"""
    connection_status = {
        'connected': session.get('logged_in', False),
        'server': session.get('server', ''),
        'username': session.get('username', ''),
        'demo_mode': session.get('demo_mode', False)
    }
    return render_template('index.html', connection_status=connection_status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login-Seite und Anmeldung am vCenter"""
    if request.method == 'POST':
        if request.form.get('demo_mode'):
            # Demo-Modus aktivieren
            init_demo_mode()
            flash('Demo-Modus aktiviert. Die angezeigten Daten sind synthetisch generiert.', 'success')
            return redirect(url_for('index'))
        
        server = request.form.get('server')
        username = request.form.get('username')
        password = request.form.get('password')
        ignore_ssl = 'ignore_ssl' in request.form
        
        if not server or not username or not password:
            flash('Bitte füllen Sie alle erforderlichen Felder aus.', 'error')
            return render_template('login.html')
        
        try:
            global vsphere_client, data_collector, report_generator
            vsphere_client = VSphereClient(server, username, password, ignore_ssl)
            vsphere_client.connect()
            
            data_collector = DataCollector(vsphere_client)
            report_generator = ReportGenerator(data_collector)
            
            session['logged_in'] = True
            session['server'] = server
            session['username'] = username
            session['demo_mode'] = False
            
            flash(f'Erfolgreich verbunden mit {server}', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Verbindungsfehler: {str(e)}")
            flash(f'Verbindungsfehler: {str(e)}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Abmeldung vom vCenter"""
    if vsphere_client and vsphere_client.is_connected():
        try:
            vsphere_client.disconnect()
        except Exception as e:
            logger.error(f"Fehler beim Trennen der Verbindung: {str(e)}")
    
    # Session zurücksetzen
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('login'))

@app.route('/report', methods=['GET', 'POST'])
@require_login
def report():
    """Seite zur Berichtserstellung"""
    if request.method == 'POST':
        # Berichtsoptionen sammeln
        options = {
            'vmware_tools': 'vmware_tools' in request.form,
            'snapshots': 'snapshots' in request.form,
            'orphaned_vmdks': 'orphaned_vmdks' in request.form,
            'format_html': 'format_html' in request.form,
            'format_pdf': 'format_pdf' in request.form,
            'format_docx': 'format_docx' in request.form
        }
        
        # Mindestens ein Berichtsinhalt und ein Format müssen ausgewählt sein
        if not any([options['vmware_tools'], options['snapshots'], options['orphaned_vmdks']]):
            flash('Bitte wählen Sie mindestens einen Berichtsinhalt aus.', 'error')
            return render_template('report.html', options=options)
        
        if not any([options['format_html'], options['format_pdf'], options['format_docx']]):
            flash('Bitte wählen Sie mindestens ein Berichtsformat aus.', 'error')
            return render_template('report.html', options=options)
        
        try:
            logger.info("Berichtserstellung gestartet")
            output_files = report_generator.generate_report(options)
            session['report_files'] = output_files
            
            if output_files:
                flash(f'Bericht erfolgreich erstellt. {len(output_files)} Dateien generiert.', 'success')
                return redirect(url_for('download'))
            else:
                flash('Keine Berichtsdateien konnten generiert werden.', 'error')
                return render_template('report.html', options=options)
        except Exception as e:
            logger.error(f"Fehler bei der Berichtserstellung: {str(e)}")
            flash(f'Fehler bei der Berichtserstellung: {str(e)}', 'error')
            return render_template('report.html', options=options)
    
    # GET-Anfrage: Zeige das Formular mit Standardoptionen
    options = {
        'vmware_tools': True,
        'snapshots': True,
        'orphaned_vmdks': True,
        'format_html': True,
        'format_pdf': False,
        'format_docx': False
    }
    return render_template('report.html', options=options)

@app.route('/download')
@require_login
def download():
    """Downloadseite für generierte Berichte"""
    report_files = session.get('report_files', [])
    return render_template('download.html', report_files=report_files)

@app.route('/download/<filename>')
@require_login
def download_file(filename):
    """Download eines generierten Berichts"""
    return send_from_directory(app.config['REPORTS_FOLDER'], filename, as_attachment=True)

@app.route('/about')
def about():
    """Über-Seite mit Informationen zur Anwendung"""
    return render_template('about.html')

def main():
    """Haupteinstiegspunkt für die Anwendung"""
    # Kommandozeilenargumente parsen
    parser = argparse.ArgumentParser(description='Bechtle vSphere Reporter v0.1')
    parser.add_argument('--port', type=int, default=PORT,
                       help=f'Port, auf dem der Webserver läuft (Standard: {PORT})')
    parser.add_argument('--debug', action='store_true', help='Debug-Modus aktivieren')
    
    args = parser.parse_args()
    
    # Starte den Flask-Server
    app.run(host='0.0.0.0', port=args.port, debug=args.debug or DEBUG_MODE)

if __name__ == '__main__':
    main()