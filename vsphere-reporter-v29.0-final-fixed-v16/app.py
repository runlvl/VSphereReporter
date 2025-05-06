"""
VMware vSphere Reporter Web-App
Version 29.0 (v16) - Ultra Debug für VMDK-Probleme

Copyright (c) 2025 Bechtle GmbH
"""

import os
import sys
import time
import secrets
import platform
import datetime
import logging
import socket
import humanize

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, send_file
from vsphere_client import VSphereClient, VSphereConnectionError
from report_generator import ReportGenerator

# Konfiguration
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', 'false').lower() == 'true'
DEMO_MODE = os.environ.get('VSPHERE_REPORTER_DEMO', 'false').lower() == 'true'
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Logger konfigurieren
log_filename = os.path.join(LOG_DIR, f"vsphere_reporter_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starte vSphere Reporter...")

# Flask App erstellen
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['DEMO_MODE'] = DEMO_MODE

# Globale Variablen
vsphere_client = None

# Hilfsfunktionen
def get_client():
    global vsphere_client
    if vsphere_client is None:
        if 'vcenter_host' not in session:
            return None
        
        logger.debug(f"Erstelle neuen VSphereClient für {session.get('vcenter_host')}")
        try:
            vsphere_client = VSphereClient(
                host=session.get('vcenter_host'),
                user=session.get('vcenter_user'),
                password=session.get('vcenter_password'),
                demo_mode=app.config['DEMO_MODE']
            )
            vsphere_client.connect()
        except VSphereConnectionError as e:
            logger.error(f"Verbindungsfehler: {str(e)}")
            flash(f"Verbindungsfehler: {str(e)}", "danger")
            return None
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {str(e)}")
            flash(f"Unerwarteter Fehler: {str(e)}", "danger")
            return None
    
    return vsphere_client

def disconnect_client():
    global vsphere_client
    if vsphere_client:
        try:
            vsphere_client.disconnect()
        except Exception as e:
            logger.warning(f"Fehler beim Trennen der Verbindung: {str(e)}")
        finally:
            vsphere_client = None
            logger.debug("VSphereClient zurückgesetzt")

# Routen
@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    return render_template('login.html', demo_mode=app.config['DEMO_MODE'])

@app.route('/login', methods=['POST'])
def login():
    session.clear()
    
    if request.form.get('demo_mode') and app.config['DEMO_MODE']:
        logger.info("Login im Demo-Modus")
        session['logged_in'] = True
        session['vcenter_host'] = 'demo.vcenter.local'
        session['vcenter_user'] = 'demo_user'
        session['vcenter_password'] = 'demo_password'
        session['demo_mode'] = True
        return redirect(url_for('dashboard'))
    
    vcenter_host = request.form.get('vcenter_host')
    vcenter_user = request.form.get('vcenter_user')
    vcenter_password = request.form.get('vcenter_password')
    
    if not vcenter_host or not vcenter_user or not vcenter_password:
        flash("Bitte füllen Sie alle Felder aus", "danger")
        return redirect(url_for('index'))
    
    try:
        client = VSphereClient(
            host=vcenter_host,
            user=vcenter_user,
            password=vcenter_password,
            demo_mode=False
        )
        client.connect()
        
        session['logged_in'] = True
        session['vcenter_host'] = vcenter_host
        session['vcenter_user'] = vcenter_user
        session['vcenter_password'] = vcenter_password
        session['demo_mode'] = False
        
        logger.info(f"Erfolgreicher Login für {vcenter_user}@{vcenter_host}")
        
        # Verbindung trennen, da wir später eine neue herstellen
        client.disconnect()
        
        return redirect(url_for('dashboard'))
        
    except VSphereConnectionError as e:
        logger.error(f"Login fehlgeschlagen für {vcenter_user}@{vcenter_host}: {str(e)}")
        flash(f"Verbindung fehlgeschlagen: {str(e)}", "danger")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim Login: {str(e)}")
        flash(f"Unerwarteter Fehler: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    disconnect_client()
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    client = get_client()
    if not client:
        return redirect(url_for('index'))
    
    try:
        system_info = {
            'vcenter_host': session.get('vcenter_host'),
            'reporter_version': 'v29.0 (Debug-Build v16)',
            'os_type': platform.system(),
            'hostname': socket.gethostname(),
            'python_version': platform.python_version(),
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'demo_mode': session.get('demo_mode', False)
        }
        
        return render_template('dashboard.html', system_info=system_info)
    except Exception as e:
        logger.error(f"Fehler beim Laden des Dashboards: {str(e)}")
        flash(f"Fehler beim Laden des Dashboards: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/report_options')
def report_options():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    return render_template('report_options.html')

@app.route('/generate_report', methods=['POST'])
def generate_report():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    options = {
        'vmware_tools': request.form.get('vmware_tools') == 'on',
        'snapshots': request.form.get('snapshots') == 'on',
        'orphaned_vmdks': request.form.get('orphaned_vmdks') == 'on',
    }
    
    session['report_options'] = options
    
    return redirect(url_for('view_report'))

@app.route('/view_report')
def view_report():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    if 'report_options' not in session:
        flash("Bitte wählen Sie Berichtsoptionen", "warning")
        return redirect(url_for('report_options'))
    
    options = session['report_options']
    client = get_client()
    
    if not client:
        return redirect(url_for('index'))
    
    try:
        # Daten sammeln
        vmware_tools_data = client.get_vmware_tools_data() if options.get('vmware_tools') else []
        snapshots_data = client.get_snapshots_data() if options.get('snapshots') else []
        orphaned_vmdks_data = client.get_orphaned_vmdks_data() if options.get('orphaned_vmdks') else []
        
        # Debug-Informationen in den Log schreiben
        logger.debug(f"VMware Tools Daten: {len(vmware_tools_data)} Einträge gesammelt")
        logger.debug(f"Snapshot Daten: {len(snapshots_data)} Einträge gesammelt")
        logger.debug(f"Orphaned VMDK Daten: {len(orphaned_vmdks_data)} Einträge gesammelt")
        
        return render_template(
            'report_view.html',
            vmware_tools=options.get('vmware_tools'),
            snapshots=options.get('snapshots'),
            orphaned_vmdks=options.get('orphaned_vmdks'),
            vmware_tools_data=vmware_tools_data,
            snapshots_data=snapshots_data,
            orphaned_vmdks_data=orphaned_vmdks_data
        )
    except Exception as e:
        logger.error(f"Fehler beim Generieren des Berichts: {str(e)}")
        flash(f"Fehler beim Generieren des Berichts: {str(e)}", "danger")
        return redirect(url_for('report_options'))

@app.route('/vmware_tools')
def vmware_tools():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    client = get_client()
    if not client:
        return redirect(url_for('index'))
    
    try:
        vmware_tools_data = client.get_vmware_tools_data()
        return render_template('vmware_tools.html', vmware_tools_data=vmware_tools_data)
    except Exception as e:
        logger.error(f"Fehler beim Laden der VMware Tools Daten: {str(e)}")
        flash(f"Fehler beim Laden der VMware Tools Daten: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/snapshots')
def snapshots():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    client = get_client()
    if not client:
        return redirect(url_for('index'))
    
    try:
        snapshots_data = client.get_snapshots_data()
        return render_template('snapshots.html', snapshots_data=snapshots_data)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Snapshot-Daten: {str(e)}")
        flash(f"Fehler beim Laden der Snapshot-Daten: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/orphaned_vmdks')
def orphaned_vmdks():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    client = get_client()
    if not client:
        return redirect(url_for('index'))
    
    try:
        logger.debug("Route /orphaned_vmdks aufgerufen, rufe get_orphaned_vmdks_data() auf")
        orphaned_vmdks_data = client.get_orphaned_vmdks_data()
        if orphaned_vmdks_data:
            logger.debug(f"Anzahl gefundener VMDKs: {len(orphaned_vmdks_data)}")
        else:
            logger.warning("Keine VMDKs gefunden oder leere Liste zurückgegeben")
            
        return render_template('orphaned_vmdks.html', orphaned_vmdks_data=orphaned_vmdks_data)
    except Exception as e:
        logger.error(f"Fehler beim Laden der VMDK-Daten: {str(e)}")
        flash(f"Fehler beim Laden der VMDK-Daten: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    return render_template('about.html')

@app.route('/export_report/<format>')
def export_report(format):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    if 'report_options' not in session:
        flash("Bitte wählen Sie Berichtsoptionen", "warning")
        return redirect(url_for('report_options'))
    
    options = session['report_options']
    client = get_client()
    
    if not client:
        return redirect(url_for('index'))
    
    try:
        # Daten sammeln
        vmware_tools_data = client.get_vmware_tools_data() if options.get('vmware_tools') else []
        snapshots_data = client.get_snapshots_data() if options.get('snapshots') else []
        orphaned_vmdks_data = client.get_orphaned_vmdks_data() if options.get('orphaned_vmdks') else []
        
        # Report Generator erstellen
        generator = ReportGenerator(
            vcenter_host=session.get('vcenter_host'),
            vmware_tools_data=vmware_tools_data if options.get('vmware_tools') else None,
            snapshots_data=snapshots_data if options.get('snapshots') else None,
            orphaned_vmdks_data=orphaned_vmdks_data if options.get('orphaned_vmdks') else None
        )
        
        # Berichte im gewünschten Format generieren
        report_path = None
        
        if format == 'html':
            report_path = generator.generate_html_report()
        elif format == 'pdf':
            report_path = generator.generate_pdf_report()
        elif format == 'docx':
            report_path = generator.generate_docx_report()
        else:
            flash("Ungültiges Berichtsformat", "danger")
            return redirect(url_for('view_report'))
        
        # Bericht zum Download anbieten
        if report_path and os.path.exists(report_path):
            return send_file(
                report_path,
                as_attachment=True,
                download_name=os.path.basename(report_path)
            )
        else:
            flash("Fehler beim Generieren des Berichts", "danger")
            return redirect(url_for('view_report'))
        
    except Exception as e:
        logger.error(f"Fehler beim Exportieren des Berichts: {str(e)}")
        flash(f"Fehler beim Exportieren des Berichts: {str(e)}", "danger")
        return redirect(url_for('view_report'))

# Fehlerbehandlung
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Hauptfunktion
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="VMware vSphere Reporter Web App")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    logger.info(f"Starte vSphere Reporter auf Port {args.port}...")
    app.run(host=args.host, port=args.port, debug=args.debug)