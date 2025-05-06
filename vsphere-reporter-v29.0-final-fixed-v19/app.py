"""
VMware vSphere Reporter v19.1 - Produktionsversion
Verbesserte Benutzeroberfläche mit robuster VMDK-Erkennung und optimierter Performance

Diese Version basiert auf dem erfolgreichen Ansatz aus v18, wurde jedoch mit einer
verbesserten Präsentation, Fehlerbehandlung und optimierter Metadatenextraktion ausgestattet.
Zusätzlich enthält Version 19.1 erweiterte Metadaten-Fallbacks und unterdrückt Flask-Warnungen.

© 2025 Bechtle GmbH - Alle Rechte vorbehalten
"""

import os
import logging
import time
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from logging.handlers import RotatingFileHandler

from vsphere_client import VSphereClient

# Konfiguration
DEBUG_MODE = os.environ.get('VSPHERE_REPORTER_DEBUG', 'False').lower() in ['true', '1', 't']
PORT = int(os.environ.get('VSPHERE_REPORTER_PORT', 5000))
VERSION = '19.1'
APP_NAME = 'VMware vSphere Reporter'

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
    
    # Sammle Daten
    raw_data = vsphere_client.collect_all_vmdk_files()
    
    # Verarbeite die Daten je nach Demo-Modus oder Echtdaten
    # Stellen sicher, dass wir auch bei Echtzeitdaten die richtige Struktur bekommen
    if isinstance(raw_data, dict):
        # Raw_data ist ein Dictionary, wir extrahieren orphaned_vmdks
        orphaned_vmdks = raw_data.get('orphaned_vmdks', [])
        app.logger.info(f"Anzahl gefundener verwaister VMDKs: {len(orphaned_vmdks)}")
        
        # Debug-Log der ersten VMDK falls vorhanden
        if orphaned_vmdks and len(orphaned_vmdks) > 0:
            app.logger.info(f"Beispiel-VMDK: {orphaned_vmdks[0]}")
    else:
        # Fallback für unerwartete Datentypen
        app.logger.warning(f"Unerwarteter Datentyp für VMDK-Daten: {type(raw_data)}")
        orphaned_vmdks = []
    
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
    
    # In dieser Version ist die Berichterstellung noch nicht implementiert
    flash('Berichterstellung ist in dieser Version noch nicht implementiert.', 'info')
    return redirect(url_for('dashboard'))

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
        logger.info(f"Starte {APP_NAME}...")
        port = get_available_port(PORT)
        if port != PORT:
            logger.info(f"Port {PORT} ist belegt, verwende Port {port}")
        
        logger.info(f"Starte {APP_NAME} auf Port {port}...")
        app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)
    except Exception as e:
        logger.error(f"Fehler beim Starten der Anwendung: {str(e)}")

if __name__ == '__main__':
    main()