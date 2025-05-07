"""
VMware vSphere Reporter - Web App
Vereinfachte Version für maximale Kompatibilität
Version v18 - Rohdatenanzeige und Fehlerdiagnose
"""

import os
import time
import json
import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, session, flash

from vsphere_client import VSphereClient

# Konfiguration
DEBUG_MODE = True  # Debug-Modus immer aktiviert in v18
SECRET_KEY = os.urandom(24)
LOG_DIR = 'logs'

# Stelle sicher, dass das Logs-Verzeichnis existiert
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Logdateiname mit Zeitstempel
log_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(LOG_DIR, f'vsphere_reporter_{log_timestamp}.log')

# Konfiguriere Logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('vsphere_reporter')
logger.info(f"Starte vSphere Reporter v18 (Diagnose-Version)...")

# Initialisiere Flask-App
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['JSON_SORT_KEYS'] = False  # JSON-Ausgabe mit originaler Reihenfolge

# Globale Variable für den Client
vsphere_client = VSphereClient()

@app.route('/')
def index():
    """Startseite"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login-Seite"""
    if request.method == 'POST':
        try:
            server = request.form.get('server', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            ignore_ssl = 'ignore_ssl' in request.form
            
            # Prüfe, ob alle Felder ausgefüllt sind
            if not server or not username or not password:
                return render_template('login.html', error="Bitte füllen Sie alle Felder aus.")
            
            # Versuche Verbindung herzustellen
            if vsphere_client.connect_to_server(
                host=server,
                username=username,
                password=password,
                disable_ssl_verification=ignore_ssl
            ):
                # Speichere Verbindungsdaten in der Session
                session['connected'] = True
                session['server'] = server
                session['username'] = username
                session['ignore_ssl'] = ignore_ssl
                
                return redirect(url_for('dashboard'))
            else:
                # Verbindung fehlgeschlagen
                error_messages = vsphere_client.error_log[-5:] if vsphere_client.error_log else []
                error_text = "Verbindung fehlgeschlagen. Details siehe Fehlerprotokolle."
                logger.error(f"Login fehlgeschlagen: {error_text}")
                return render_template('login.html', error=error_text)
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Login: {str(e)}")
            logger.error(traceback.format_exc())
            return render_template('login.html', error=f"Unerwarteter Fehler: {str(e)}")
    
    # GET-Anfrage
    return render_template('login.html')

@app.route('/demo_mode')
def demo_mode():
    """Aktiviere Demo-Modus"""
    vsphere_client.set_demo_mode(True)
    session['connected'] = True
    session['server'] = 'demo.vcenter.local'
    session['username'] = 'demo@vsphere.local'
    session['ignore_ssl'] = True
    session['demo_mode'] = True
    
    logger.info("Demo-Modus aktiviert")
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard nach erfolgreicher Anmeldung"""
    if not session.get('connected'):
        return redirect(url_for('login'))
    
    connection_info = {
        'host': session.get('server', 'Nicht verbunden'),
        'username': session.get('username', 'Nicht angemeldet'),
        'demo_mode': session.get('demo_mode', False)
    }
    
    return render_template('dashboard.html', connection_info=connection_info)

@app.route('/collect_vmdk_data', methods=['POST'])
def collect_vmdk_data():
    """Sammle VMDK-Daten"""
    if not session.get('connected'):
        return redirect(url_for('login'))
    
    try:
        # Sammle die Daten
        vsphere_client.error_log = []  # Lösche vorherige Fehler
        logger.info("Starte Sammlung von VMDK-Daten...")
        
        raw_data = vsphere_client.collect_all_vmdk_files()
        
        # Speichere die Daten in der Session (nur die Anzahl, nicht die vollen Daten)
        session['data_collected'] = True
        
        # Leite zur Rohdatenanzeige weiter
        flash("Datensammlung abgeschlossen", "success")
        return redirect(url_for('raw_data'))
        
    except Exception as e:
        logger.error(f"Fehler bei der Datensammlung: {str(e)}")
        logger.error(traceback.format_exc())
        vsphere_client.log_error(f"Fehler bei der Datensammlung: {str(e)}", e)
        flash(f"Fehler bei der Datensammlung: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/raw_data')
def raw_data():
    """Zeige Rohdaten"""
    if not session.get('connected'):
        return redirect(url_for('login'))
    
    # Sammle die Daten, falls noch nicht gesammelt
    if not session.get('data_collected'):
        return redirect(url_for('collect_vmdk_data'))
    
    # Hole die Rohdaten
    raw_data = vsphere_client.raw_data
    error_log = vsphere_client.error_log
    
    return render_template('raw_data.html', raw_data=raw_data, error_log=error_log)

@app.route('/logout')
def logout():
    """Logout und Trennen der Verbindung"""
    if session.get('connected') and not session.get('demo_mode'):
        vsphere_client.disconnect()
    
    session.clear()
    flash("Sie wurden erfolgreich abgemeldet", "info")
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    """404 Fehlerseite"""
    return render_template('error.html', error="Seite nicht gefunden"), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500 Fehlerseite"""
    return render_template('error.html', error="Interner Serverfehler"), 500

if __name__ == '__main__':
    logger.info("Starte Webserver...")
    app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)