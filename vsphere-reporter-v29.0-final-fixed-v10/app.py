#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter v29.0
A comprehensive reporting tool for VMware vSphere environments

Final Fixed Version 10 - Simplified Web Interface
Copyright (c) 2025 Bechtle GmbH
"""

import os
import sys
import logging
import datetime
import socket
import json
from functools import wraps
from pathlib import Path
import humanize
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify, send_from_directory

# Import custom modules
import demo_data
from vsphere_client import VSphereClient, VSphereConnectionError
from report_generator import ReportGenerator

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(log_dir, f'vsphere_reporter_{log_timestamp}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['REPORTS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

# Custom error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session['authenticated']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_available_port(start_port=5000, max_attempts=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return start_port  # Fallback to start_port if no port is available

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if 'demo_mode' in request.form:
            session['authenticated'] = True
            session['demo_mode'] = True
            session['vsphere_host'] = 'demo.vcenter.local'
            session['vsphere_user'] = 'demo@vsphere.local'
            flash('Demo-Modus aktiviert. Beispieldaten werden verwendet.', 'success')
            return redirect(url_for('dashboard'))
        
        vsphere_host = request.form.get('vsphere_host', '').strip()
        vsphere_user = request.form.get('vsphere_user', '').strip()
        vsphere_password = request.form.get('vsphere_password', '')
        ignore_ssl = 'ignore_ssl' in request.form
        
        if not vsphere_host or not vsphere_user or not vsphere_password:
            error = 'Bitte füllen Sie alle Felder aus.'
        else:
            try:
                client = VSphereClient(vsphere_host, vsphere_user, vsphere_password, ignore_ssl)
                if client.connect():
                    session['authenticated'] = True
                    session['demo_mode'] = False
                    session['vsphere_host'] = vsphere_host
                    session['vsphere_user'] = vsphere_user
                    session['vsphere_password'] = vsphere_password
                    session['ignore_ssl'] = ignore_ssl
                    flash('Erfolgreich mit vCenter Server verbunden.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    error = 'Verbindung zum vCenter fehlgeschlagen.'
            except VSphereConnectionError as e:
                error = f'Verbindungsfehler: {str(e)}'
            except Exception as e:
                logger.exception("Unerwarteter Fehler bei der Anmeldung")
                error = f'Ein unerwarteter Fehler ist aufgetreten: {str(e)}'
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        if session.get('demo_mode', False):
            # Use demo data
            total_vms = demo_data.get_total_vms()
            total_hosts = demo_data.get_total_hosts()
            total_datastores = demo_data.get_total_datastores()
            total_clusters = demo_data.get_total_clusters()
            vms_by_power_state = demo_data.get_vms_by_power_state()
            outdated_tools = demo_data.get_outdated_tools_count()
            snapshots_count = demo_data.get_snapshots_count()
            orphaned_vmdks_count = demo_data.get_orphaned_vmdks_count()
        else:
            # Use real vCenter connection
            client = VSphereClient(
                session['vsphere_host'], 
                session['vsphere_user'], 
                session['vsphere_password'], 
                session.get('ignore_ssl', False)
            )
            client.connect()
            
            total_vms = client.get_total_vms()
            total_hosts = client.get_total_hosts()
            total_datastores = client.get_total_datastores()
            total_clusters = client.get_total_clusters()
            vms_by_power_state = client.get_vms_by_power_state()
            outdated_tools = client.get_outdated_tools_count()
            snapshots_count = client.get_snapshots_count()
            orphaned_vmdks_count = client.get_orphaned_vmdks_count()
        
        return render_template('dashboard.html',
                              vsphere_host=session['vsphere_host'],
                              vsphere_user=session['vsphere_user'],
                              total_vms=total_vms,
                              total_hosts=total_hosts,
                              total_datastores=total_datastores,
                              total_clusters=total_clusters,
                              vms_by_power_state=vms_by_power_state,
                              outdated_tools=outdated_tools,
                              snapshots_count=snapshots_count,
                              orphaned_vmdks_count=orphaned_vmdks_count,
                              demo_mode=session.get('demo_mode', False))
    except Exception as e:
        logger.exception("Error in dashboard")
        flash(f'Fehler beim Laden des Dashboards: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/report_options')
@login_required
def report_options():
    return render_template('report_options.html')

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    try:
        # Get selected report options
        selected_options = {}
        for option in ['vmware_tools', 'snapshots', 'orphaned_vmdks', 'vm_hardware', 'datastores', 'hosts', 'clusters']:
            selected_options[option] = option in request.form
        
        # Get selected export formats
        export_formats = []
        for format_option in ['html', 'pdf', 'docx']:
            if format_option in request.form:
                export_formats.append(format_option)
        
        if not export_formats:
            flash('Bitte wählen Sie mindestens ein Exportformat.', 'error')
            return redirect(url_for('report_options'))
        
        # Generate report
        generator = ReportGenerator(
            session.get('demo_mode', False),
            session.get('vsphere_host'),
            session.get('vsphere_user'),
            session.get('vsphere_password'),
            session.get('ignore_ssl', False)
        )
        
        # Generate unique report ID
        report_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create report directory
        report_dir = os.path.join(app.config['REPORTS_FOLDER'], report_id)
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate report with selected options
        report_files = generator.generate_report(
            report_dir,
            export_formats,
            selected_options
        )
        
        # Store report information in session
        session['current_report_id'] = report_id
        session['current_report_files'] = report_files
        session['selected_options'] = selected_options
        
        return redirect(url_for('report_view'))
    
    except Exception as e:
        logger.exception("Error generating report")
        flash(f'Fehler bei der Berichtsgenerierung: {str(e)}', 'error')
        return redirect(url_for('report_options'))

@app.route('/report_view')
@login_required
def report_view():
    report_id = session.get('current_report_id')
    report_files = session.get('current_report_files', {})
    selected_options = session.get('selected_options', {})
    
    if not report_id or not report_files:
        flash('Kein Bericht verfügbar. Bitte generieren Sie zuerst einen Bericht.', 'info')
        return redirect(url_for('report_options'))
    
    return render_template('report_view.html', 
                          report_id=report_id,
                          report_files=report_files,
                          selected_options=selected_options)

@app.route('/download_report/<path:filename>')
@login_required
def download_report(filename):
    report_id = session.get('current_report_id')
    if not report_id:
        flash('Kein Bericht verfügbar. Bitte generieren Sie zuerst einen Bericht.', 'info')
        return redirect(url_for('report_options'))
    
    report_dir = os.path.join(app.config['REPORTS_FOLDER'], report_id)
    return send_from_directory(report_dir, filename, as_attachment=True)

@app.route('/view_vmware_tools')
@login_required
def view_vmware_tools():
    try:
        if session.get('demo_mode', False):
            vmware_tools_data = demo_data.get_vmware_tools_data()
        else:
            # Use real vCenter connection
            client = VSphereClient(
                session['vsphere_host'], 
                session['vsphere_user'], 
                session['vsphere_password'], 
                session.get('ignore_ssl', False)
            )
            client.connect()
            vmware_tools_data = client.get_vmware_tools_data()
        
        # Sort by VMware Tools status (outdated first)
        vmware_tools_data.sort(key=lambda x: (x['version'] == 'Not installed', x['status'] == 'Outdated', x['status'] == 'Up-to-date'))
        
        return render_template('vmware_tools.html', vmware_tools_data=vmware_tools_data)
    except Exception as e:
        logger.exception("Error retrieving VMware Tools data")
        flash(f'Fehler beim Abrufen der VMware Tools-Daten: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/view_snapshots')
@login_required
def view_snapshots():
    try:
        if session.get('demo_mode', False):
            snapshots_data = demo_data.get_snapshots_data()
        else:
            # Use real vCenter connection
            client = VSphereClient(
                session['vsphere_host'], 
                session['vsphere_user'], 
                session['vsphere_password'], 
                session.get('ignore_ssl', False)
            )
            client.connect()
            snapshots_data = client.get_snapshots_data()
        
        # Add human-readable age
        for snapshot in snapshots_data:
            creation_time = snapshot.get('creation_time')
            if creation_time:
                # Ensure both datetimes are timezone-aware or naive to avoid comparison errors
                if creation_time.tzinfo:
                    now = datetime.datetime.now(creation_time.tzinfo)
                else:
                    now = datetime.datetime.now()
                
                age_seconds = (now - creation_time).total_seconds()
                snapshot['age_days'] = age_seconds / (60 * 60 * 24)  # Convert to days
                snapshot['age_human'] = humanize.naturaldelta(datetime.timedelta(seconds=age_seconds))
        
        # Sort by age (oldest first)
        snapshots_data.sort(key=lambda x: x.get('creation_time', datetime.datetime.now()))
        
        return render_template('snapshots.html', snapshots_data=snapshots_data)
    except Exception as e:
        logger.exception("Error retrieving snapshots data")
        flash(f'Fehler beim Abrufen der Snapshot-Daten: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/view_orphaned_vmdks')
@login_required
def view_orphaned_vmdks():
    try:
        if session.get('demo_mode', False):
            orphaned_vmdks_data = demo_data.get_orphaned_vmdks_data()
        else:
            # Use real vCenter connection
            client = VSphereClient(
                session['vsphere_host'], 
                session['vsphere_user'], 
                session['vsphere_password'], 
                session.get('ignore_ssl', False)
            )
            client.connect()
            orphaned_vmdks_data = client.get_orphaned_vmdks_data()
        
        # Add human-readable size
        for vmdk in orphaned_vmdks_data:
            size_bytes = vmdk.get('size_bytes', 0)
            vmdk['size_human'] = humanize.naturalsize(size_bytes)
        
        # Sort by size (largest first)
        orphaned_vmdks_data.sort(key=lambda x: x.get('size_bytes', 0), reverse=True)
        
        return render_template('orphaned_vmdks.html', orphaned_vmdks_data=orphaned_vmdks_data)
    except Exception as e:
        logger.exception("Error retrieving orphaned VMDKs data")
        flash(f'Fehler beim Abrufen der verwaisten VMDK-Daten: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    return render_template('about.html', version="29.0")

@app.route('/logout')
def logout():
    session.clear()
    flash('Sie wurden erfolgreich abgemeldet.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port)