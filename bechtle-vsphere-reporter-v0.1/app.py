"""
Bechtle vSphere Reporter v0.1
Eine umfassende Reporting-Anwendung für VMware vSphere-Umgebungen

Dies ist der Haupteinstiegspunkt für die Webanwendung.
"""

import os
import logging
import argparse
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from vsphere_client import VSphereClient
from data_collector import DataCollector
from report_generator import ReportGenerator

# Konfiguration
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
DEFAULT_PORT = int(os.environ.get('VSPHERE_REPORTER_PORT', 5000))

# App initialisieren
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Logging konfigurieren
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(log_dir, f'vsphere_reporter_{timestamp}.log')

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('vsphere_reporter')
logger.info('Starte Bechtle vSphere Reporter v0.1...')

# Globale Variablen
vsphere_client = None
data_collector = None
report_generator = None
demo_mode = False

@app.route('/')
def index():
    """Startseite der Anwendung"""
    connection_status = {
        'connected': vsphere_client is not None and vsphere_client.is_connected(),
        'server': vsphere_client.server if vsphere_client else None,
        'username': vsphere_client.username if vsphere_client else None,
        'demo_mode': demo_mode
    }
    return render_template('index.html', connection_status=connection_status)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login-Seite zur Verbindung mit vCenter"""
    global vsphere_client, data_collector, report_generator, demo_mode
    
    if request.method == 'POST':
        if request.form.get('demo_mode') == 'on':
            # Demo-Modus aktivieren
            demo_mode = True
            flash('Demo-Modus aktiviert. Es werden Beispieldaten angezeigt.', 'success')
            from demo_data import get_demo_client
            vsphere_client = get_demo_client()
            data_collector = DataCollector(vsphere_client)
            report_generator = ReportGenerator(data_collector)
            return redirect(url_for('index'))
        
        # Normale Anmeldung mit vCenter-Credentials
        server = request.form.get('server')
        username = request.form.get('username')
        password = request.form.get('password')
        ignore_ssl = request.form.get('ignore_ssl') == 'on'
        
        if not server or not username or not password:
            flash('Bitte alle Felder ausfüllen', 'error')
            return render_template('login.html')
        
        try:
            logger.info(f'Verbinde mit vCenter {server} als {username}')
            vsphere_client = VSphereClient(server, username, password, ignore_ssl)
            vsphere_client.connect()
            data_collector = DataCollector(vsphere_client)
            report_generator = ReportGenerator(data_collector)
            demo_mode = False
            flash(f'Erfolgreich mit {server} verbunden', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f'Fehler bei der Verbindung: {str(e)}')
            flash(f'Verbindungsfehler: {str(e)}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Trennt die Verbindung zum vCenter"""
    global vsphere_client, data_collector, report_generator, demo_mode
    
    if vsphere_client:
        vsphere_client.disconnect()
    
    vsphere_client = None
    data_collector = None
    report_generator = None
    demo_mode = False
    
    flash('Erfolgreich abgemeldet', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard mit Übersicht über die vSphere-Umgebung"""
    if not vsphere_client or (not vsphere_client.is_connected() and not demo_mode):
        flash('Bitte zuerst anmelden', 'warning')
        return redirect(url_for('login'))
    
    try:
        # Basis-Statistiken für Dashboard sammeln
        stats = data_collector.get_environment_stats()
        return render_template('dashboard.html', stats=stats, demo_mode=demo_mode)
    except Exception as e:
        logger.error(f'Fehler beim Laden des Dashboards: {str(e)}')
        flash(f'Fehler beim Laden des Dashboards: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/report', methods=['GET', 'POST'])
def report():
    """Berichtsoptionen und -generierung"""
    if not vsphere_client or (not vsphere_client.is_connected() and not demo_mode):
        flash('Bitte zuerst anmelden', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Berichtsoptionen aus dem Formular auslesen
        options = {
            'vmware_tools': request.form.get('vmware_tools') == 'on',
            'snapshots': request.form.get('snapshots') == 'on',
            'orphaned_vmdks': request.form.get('orphaned_vmdks') == 'on',
            'format_html': request.form.get('format_html') == 'on',
            'format_pdf': request.form.get('format_pdf') == 'on',
            'format_docx': request.form.get('format_docx') == 'on',
            'save_history': request.form.get('save_history') == 'on'
        }
        
        # Mindestens ein Format muss ausgewählt sein
        if not (options['format_html'] or options['format_pdf'] or options['format_docx']):
            flash('Bitte mindestens ein Ausgabeformat wählen', 'error')
            return render_template('report.html')
        
        try:
            # Bericht generieren
            logger.info('Starte Berichtsgenerierung mit Optionen: ' + str(options))
            output_files = report_generator.generate_report(options)
            
            # Option für historische Berichte ignorieren (nicht implementiert)
            if options['save_history']:
                logger.info('Historische Berichte sind in dieser Version nicht verfügbar')
            
            return render_template('report_complete.html', output_files=output_files)
        except Exception as e:
            logger.error(f'Fehler bei der Berichtsgenerierung: {str(e)}')
            flash(f'Fehler bei der Berichtsgenerierung: {str(e)}', 'error')
            return render_template('report.html')
    
    return render_template('report.html')

# Historienfunktionen sind in dieser Version entfernt

@app.route('/download/<path:filename>')
def download_file(filename):
    """Ermöglicht das Herunterladen von generierten Berichten"""
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    return send_from_directory(directory=reports_dir, path=filename, as_attachment=True)

@app.route('/api/vmware-tools')
def api_vmware_tools():
    """API-Endpunkt für VMware Tools-Status"""
    if not vsphere_client or (not vsphere_client.is_connected() and not demo_mode):
        return jsonify({"error": "Nicht verbunden"}), 401
    
    try:
        tools_data = data_collector.get_vmware_tools_status()
        return jsonify(tools_data)
    except Exception as e:
        logger.error(f'API-Fehler (VMware Tools): {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/snapshots')
def api_snapshots():
    """API-Endpunkt für Snapshot-Informationen"""
    if not vsphere_client or (not vsphere_client.is_connected() and not demo_mode):
        return jsonify({"error": "Nicht verbunden"}), 401
    
    try:
        snapshot_data = data_collector.get_snapshot_info()
        return jsonify(snapshot_data)
    except Exception as e:
        logger.error(f'API-Fehler (Snapshots): {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/orphaned-vmdks')
def api_orphaned_vmdks():
    """API-Endpunkt für verwaiste VMDK-Dateien"""
    if not vsphere_client or (not vsphere_client.is_connected() and not demo_mode):
        return jsonify({"error": "Nicht verbunden"}), 401
    
    try:
        vmdk_data = data_collector.get_orphaned_vmdks()
        return jsonify(vmdk_data)
    except Exception as e:
        logger.error(f'API-Fehler (VMDKs): {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/about')
def about():
    """Über-Seite mit Informationen zur Anwendung"""
    return render_template('about.html')

def main():
    """Haupteinstiegspunkt für die Anwendung"""
    parser = argparse.ArgumentParser(description='Bechtle vSphere Reporter v0.1')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port zum Starten des Webservers')
    parser.add_argument('--debug', action='store_true', help='Debug-Modus aktivieren')
    
    args = parser.parse_args()
    
    port = args.port
    debug_mode = args.debug or DEBUG_MODE
    
    if debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug-Modus aktiviert")
    
    logger.info(f'Starte Bechtle vSphere Reporter auf Port {port}...')
    
    # Starte die Anwendung
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

if __name__ == '__main__':
    main()