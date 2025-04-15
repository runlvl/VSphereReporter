#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter Demo
Zeigt die Benutzeroberfläche und einen simulierten Datenfluss für Demonstrationszwecke

Diese Demo benötigt keine echte vCenter-Verbindung und kann auf beliebigen Systemen ausgeführt werden.
"""

import sys
import os
import datetime
import random
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser

# Demo-Modus aktivieren, um simulierte Daten zu verwenden
os.environ['VSPHERE_REPORTER_DEMO'] = '1'

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                                QWidget, QPushButton, QLabel, QComboBox, QCheckBox,
                                QProgressBar, QGroupBox, QTabWidget, QTextEdit, 
                                QMessageBox, QFileDialog, QSplitter, QFrame)
    from PyQt5.QtGui import QIcon, QFont, QPixmap
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
except ImportError:
    print("PyQt5 ist nicht installiert. Installiere mit: pip install PyQt5")
    sys.exit(1)

# Bechtle Farbpalette
BECHTLE_BLUE = "#00355e"
BECHTLE_ORANGE = "#da6f1e"
BECHTLE_GREEN = "#23a96a"
BECHTLE_LIGHT_GRAY = "#f3f3f3"
BECHTLE_DARK_GRAY = "#5a5a5a"

class DemoHTTPServer:
    """Einfacher HTTP-Server zum Anzeigen der HTML-Demo"""
    def __init__(self, port=5001):
        self.port = port
        self.server = None
        self.server_thread = None
        
    def start(self):
        """Startet den HTTP-Server in einem separaten Thread"""
        try:
            handler = SimpleHTTPRequestHandler
            self.server = HTTPServer(('0.0.0.0', self.port), handler)
            
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print(f"Demo-Server läuft auf http://localhost:{self.port}")
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Port {self.port} ist bereits belegt, versuche einen anderen Port")
                self.port += 1
                self.start()  # Rekursiv mit erhöhtem Port probieren
            else:
                print(f"Fehler beim Starten des HTTP-Servers: {e}")
        except Exception as e:
            print(f"Unerwarteter Fehler beim Starten des HTTP-Servers: {e}")
        
    def stop(self):
        """Stoppt den HTTP-Server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

class DataCollectorThread(QThread):
    """Thread zum Sammeln von Daten (simuliert)"""
    update_progress = pyqtSignal(int, str)
    collection_complete = pyqtSignal(dict)
    
    def __init__(self, host, username, password, ignore_ssl):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        self._is_cancelled = False
        
    def run(self):
        """Führt die simulierte Datensammlung durch"""
        try:
            # Verbindung simulieren
            self.update_progress.emit(5, f"Verbinde mit vCenter {self.host}...")
            time.sleep(1)
            
            # VM-Zählung simulieren
            self.update_progress.emit(15, "Zähle VMs...")
            time.sleep(0.5)
            
            # VMware Tools-Versionen simulieren
            self.update_progress.emit(30, "Sammle VMware Tools-Versionen...")
            time.sleep(1.5)
            
            # Snapshots simulieren
            self.update_progress.emit(50, "Sammle Snapshot-Informationen...")
            time.sleep(1)
            
            # VMDK-Sammlung simulieren
            self.update_progress.emit(60, "Starte VMDK-Erkennung (V25.2-POWER)...")
            time.sleep(0.8)
            
            # Verbesserte VMDK-Erkennung simulieren
            self.update_progress.emit(75, "PowerShell-ähnliche VMDK-Erkennung...")
            time.sleep(1.2)
            
            # Orphaned VMDK-Erkennung simulieren
            self.update_progress.emit(85, "Identifiziere verwaiste VMDKs...")
            time.sleep(1)
            
            # Generiere simulierte Daten
            data = self._generate_demo_data()
            
            # Fertig
            self.update_progress.emit(100, "Datensammlung abgeschlossen")
            self.collection_complete.emit(data)
            
        except Exception as e:
            self.update_progress.emit(0, f"Fehler bei der Datensammlung: {str(e)}")
            
    def _generate_demo_data(self):
        """Generiert Demo-Daten für die Anzeige"""
        # VMware Tools
        vmware_tools = []
        tool_versions = [
            "10.3.5", "10.3.10", "11.0.0", "11.0.5", "11.1.0", 
            "11.2.5", "11.3.0", "11.3.5", "12.0.0", "12.1.0"
        ]
        
        for i in range(25):
            version_index = min(int(i / 3), len(tool_versions) - 1)
            vmware_tools.append({
                'vm': f"vm-{i:03d}.example.local",
                'version': tool_versions[version_index],
                'status': random.choice(["OK", "Wird aktualisiert", "Veraltet"])
            })
        
        # Snapshots
        snapshots = []
        for i in range(15):
            days_old = random.randint(1, 365)
            date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            snapshots.append({
                'vm': f"vm-{random.randint(1, 100):03d}.example.local",
                'name': f"Snapshot-{i}",
                'date': date,
                'days_old': days_old,
                'size_mb': random.randint(100, 50000)
            })
        
        # Sortiere Snapshots nach Alter (älteste zuerst)
        snapshots.sort(key=lambda x: x['days_old'], reverse=True)
        
        # Verwaiste VMDKs
        orphaned_vmdks = []
        for i in range(10):
            days_old = random.randint(10, 500)
            date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            orphaned_vmdks.append({
                'datastore': f"datastore-{random.randint(1, 5)}",
                'path': f"[datastore-{random.randint(1, 5)}] orphaned/orphaned-disk-{i}.vmdk",
                'name': f"orphaned-disk-{i}.vmdk",
                'size_mb': random.randint(1000, 100000),
                'modification_time': date
            })
            
        return {
            'vmware_tools': vmware_tools,
            'snapshots': snapshots,
            'orphaned_vmdks': orphaned_vmdks
        }
        
    def cancel(self):
        """Bricht die Datensammlung ab"""
        self._is_cancelled = True

class DemoMainWindow(QMainWindow):
    """Demo-Hauptfenster für den VMware vSphere Reporter"""
    def __init__(self):
        super().__init__()
        
        self.data = None
        self.http_server = DemoHTTPServer(port=5001)
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle("VMware vSphere Reporter v25.2")
        self.setMinimumSize(800, 600)
        
        # Hauptlayout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Kopfzeile mit Bechtle-Logo
        header = QHBoxLayout()
        logo_label = QLabel()
        try:
            # Versuche, das Logo zu laden
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, 'images', 'logo_bechtle.png')
            if os.path.exists(logo_path):
                logo = QPixmap(logo_path)
                logo_label.setPixmap(logo.scaled(200, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                logo_label.setText("Bechtle Logo")
                logo_label.setStyleSheet(f"color: {BECHTLE_BLUE}; font-weight: bold; font-size: 18px;")
        except Exception:
            logo_label.setText("Bechtle Logo")
            logo_label.setStyleSheet(f"color: {BECHTLE_BLUE}; font-weight: bold; font-size: 18px;")
        
        header.addWidget(logo_label)
        header.addStretch()
        
        title_label = QLabel("VMware vSphere Reporter v25.2")
        title_label.setStyleSheet(f"color: {BECHTLE_BLUE}; font-weight: bold; font-size: 18px;")
        header.addWidget(title_label)
        header.addStretch()
        
        main_layout.addLayout(header)
        
        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {BECHTLE_ORANGE};")
        main_layout.addWidget(line)
        
        # Verbindungs-Bereich
        connection_group = QGroupBox("vCenter-Verbindung")
        connection_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; border: 1px solid {BECHTLE_LIGHT_GRAY}; border-radius: 5px; margin-top: 1ex; }} QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }}")
        connection_layout = QVBoxLayout(connection_group)
        
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("vCenter:"))
        self.host_combo = QComboBox()
        self.host_combo.setEditable(True)
        self.host_combo.addItem("vcenter.demo.local")
        host_layout.addWidget(self.host_combo)
        connection_layout.addLayout(host_layout)
        
        credentials_layout = QHBoxLayout()
        credentials_layout.addWidget(QLabel("Benutzername:"))
        self.username_edit = QComboBox()
        self.username_edit.setEditable(True)
        self.username_edit.addItem("administrator@vsphere.local")
        credentials_layout.addWidget(self.username_edit)
        
        credentials_layout.addWidget(QLabel("Passwort:"))
        self.password_edit = QComboBox()
        self.password_edit.setEditable(True)
        self.password_edit.addItem("demo-password")
        # Passwort verbergen für mehr Realismus
        self.password_edit.setStyleSheet("QComboBox { echo-mode: password; }")
        credentials_layout.addWidget(self.password_edit)
        
        self.ignore_ssl_check = QCheckBox("Unsichere SSL-Verbindungen zulassen")
        self.ignore_ssl_check.setChecked(True)
        
        connection_layout.addLayout(credentials_layout)
        connection_layout.addWidget(self.ignore_ssl_check)
        
        connect_button = QPushButton("Verbinden")
        connect_button.setStyleSheet(f"background-color: {BECHTLE_BLUE}; color: white; font-weight: bold; padding: 8px;")
        connect_button.clicked.connect(self.connect_to_vcenter)
        connection_layout.addWidget(connect_button)
        
        main_layout.addWidget(connection_group)
        
        # Berichtsoptionen
        report_options_group = QGroupBox("Berichtsoptionen")
        report_options_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; border: 1px solid {BECHTLE_LIGHT_GRAY}; border-radius: 5px; margin-top: 1ex; }} QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }}")
        report_options_layout = QVBoxLayout(report_options_group)
        
        # Checkboxen für Berichtsoptionen
        self.tools_check = QCheckBox("VMware Tools (sortiert nach ältester Version)")
        self.tools_check.setChecked(True)
        report_options_layout.addWidget(self.tools_check)
        
        self.snapshot_check = QCheckBox("Snapshots (sortiert nach Alter, älteste zuerst)")
        self.snapshot_check.setChecked(True)
        report_options_layout.addWidget(self.snapshot_check)
        
        self.vmdk_check = QCheckBox("Verwaiste VMDK-Dateien")
        self.vmdk_check.setChecked(True)
        report_options_layout.addWidget(self.vmdk_check)
        
        # Exportformate
        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel("Exportformat:"))
        self.export_combo = QComboBox()
        self.export_combo.addItems(["HTML", "DOCX", "PDF"])
        export_layout.addWidget(self.export_combo)
        export_layout.addStretch()
        
        report_options_layout.addLayout(export_layout)
        
        # Bericht generieren Button
        self.generate_button = QPushButton("Bericht generieren")
        self.generate_button.setStyleSheet(f"background-color: {BECHTLE_GREEN}; color: white; font-weight: bold; padding: 8px;")
        self.generate_button.setEnabled(False)
        self.generate_button.clicked.connect(self.generate_report)
        report_options_layout.addWidget(self.generate_button)
        
        main_layout.addWidget(report_options_group)
        
        # Fortschrittsanzeige
        progress_group = QGroupBox("Fortschritt")
        progress_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; border: 1px solid {BECHTLE_LIGHT_GRAY}; border-radius: 5px; margin-top: 1ex; }} QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }}")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Bereit zur Verbindung mit vCenter")
        progress_layout.addWidget(self.status_label)
        
        main_layout.addWidget(progress_group)
        
        # Ergebnisse Tabs
        self.results_tabs = QTabWidget()
        self.results_tabs.setStyleSheet(f"QTabBar::tab:selected {{ background-color: {BECHTLE_BLUE}; color: white; font-weight: bold; }}")
        
        # VMware Tools Tab
        self.tools_tab = QTextEdit()
        self.tools_tab.setReadOnly(True)
        self.results_tabs.addTab(self.tools_tab, "VMware Tools")
        
        # Snapshots Tab
        self.snapshots_tab = QTextEdit()
        self.snapshots_tab.setReadOnly(True)
        self.results_tabs.addTab(self.snapshots_tab, "Snapshots")
        
        # Verwaiste VMDKs Tab
        self.vmdks_tab = QTextEdit()
        self.vmdks_tab.setReadOnly(True)
        self.results_tabs.addTab(self.vmdks_tab, "Verwaiste VMDKs")
        
        main_layout.addWidget(self.results_tabs)
        
        # Demo-Buttons
        demo_layout = QHBoxLayout()
        
        open_demo_button = QPushButton("Demo im Browser öffnen")
        open_demo_button.setStyleSheet(f"background-color: {BECHTLE_BLUE}; color: white; padding: 8px;")
        open_demo_button.clicked.connect(self.open_demo_in_browser)
        demo_layout.addWidget(open_demo_button)
        
        demo_layout.addStretch()
        
        exit_button = QPushButton("Beenden")
        exit_button.setStyleSheet(f"background-color: {BECHTLE_DARK_GRAY}; color: white; padding: 8px;")
        exit_button.clicked.connect(self.close)
        demo_layout.addWidget(exit_button)
        
        main_layout.addLayout(demo_layout)
        
        self.setCentralWidget(main_widget)
        
        # HTTP-Server für die Demo starten
        self.http_server.start()
        
        # Demo-HTML-Datei generieren
        self._generate_demo_html()
        
    def _generate_demo_html(self):
        """Generiert eine Demo-HTML-Datei im Bechtle-Design"""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>VMware vSphere Reporter Demo</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        .header {{
            background-color: {BECHTLE_BLUE};
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .feature {{
            background-color: #f5f5f5;
            border-left: 5px solid {BECHTLE_ORANGE};
            padding: 15px;
            margin-bottom: 15px;
        }}
        .nav-fixed {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background-color: {BECHTLE_BLUE};
            color: white;
            display: flex;
            align-items: center;
            padding: 0 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 9999;
        }}
        .logo {{
            height: 30px;
            margin-right: 20px;
        }}
        .nav-title {{
            font-size: 18px;
            font-weight: bold;
            flex: 1;
        }}
        .nav-links {{
            display: flex;
            list-style-type: none;
            margin: 0;
            padding: 0;
        }}
        .nav-links li {{
            margin: 0 10px;
        }}
        .nav-links a {{
            color: rgba(255, 255, 255, 0.85);
            text-decoration: none;
            padding: 20px 12px;
            display: inline-block;
        }}
        .nav-links a:hover, .nav-links a.active {{
            color: white;
            background-color: rgba(255, 255, 255, 0.1);
        }}
    </style>
</head>
<body>
    <!-- Navigation Bar Demo -->
    <nav class='nav-fixed'>
        <div class='nav-title'>VMware vSphere Reporter</div>
        <ul class='nav-links'>
            <li><a href='#' class='active'>Übersicht</a></li>
            <li><a href='#'>VMware Tools</a></li>
            <li><a href='#'>Snapshots</a></li>
            <li><a href='#'>Verwaiste VMDKs</a></li>
            <li><a href='#'>VMs</a></li>
        </ul>
    </nav>
    
    <div style='height: 70px;'></div>
    
    <div class='container'>
        <div class='header'>
            <h1>VMware vSphere Reporter Demo</h1>
            <p>Version 25.2</p>
        </div>
        
        <h2>Neue Features</h2>
        
        <div class='feature'>
            <h3>Vollständig überarbeitete VMDK-Erkennung</h3>
            <p>Die Version 25.2 bietet eine komplett neu implementierte Methode zur 
            Erkennung verwaister VMDKs mit PowerShell-inspirierter Methodik.</p>
        </div>
        
        <div class='feature'>
            <h3>PowerShell-inspirierter Ansatz für VMDKs</h3>
            <p>Der neu entwickelte Algorithmus basiert auf dem erfolgreichen PowerShell-Skript
            und nutzt einen VM-zentrierten Ansatz zur Erfassung aller Festplatten.</p>
        </div>
        
        <div class='feature'>
            <h3>Verbesserte Pfadvergleiche</h3>
            <p>Mehrere Pfadnormalisierungen werden für präzisere Ergebnisse beim Vergleich von VMDKs eingesetzt.</p>
        </div>
        
        <div class='feature'>
            <h3>Mehrstufige Vergleichslogik</h3>
            <p>Der erweiterte Erkennungsalgorithmus verwendet mehrere Fallback-Mechanismen und
            unterstützt verschiedene VMDK-Pfadformate für eine maximale Erkennungsrate.</p>
        </div>
    </div>
</body>
</html>"""

        # HTML-Datei im aktuellen Verzeichnis speichern
        with open("demo.html", "w", encoding="utf-8") as file:
            file.write(html_content)
    
    def connect_to_vcenter(self):
        """Simuliert eine Verbindung zum vCenter"""
        host = self.host_combo.currentText()
        username = self.username_edit.currentText()
        password = self.password_edit.currentText()
        ignore_ssl = self.ignore_ssl_check.isChecked()
        
        # Verbindungsparameter-Überprüfung
        if not host or not username or not password:
            QMessageBox.warning(self, "Fehlende Eingaben", 
                                "Bitte geben Sie vCenter, Benutzername und Passwort ein.")
            return
        
        # Datensammlung im Thread starten
        self.status_label.setText(f"Verbinde mit vCenter {host}...")
        self.progress_bar.setValue(0)
        
        # Buttons deaktivieren während der Datensammlung
        self.generate_button.setEnabled(False)
        
        # Datensammler-Thread erstellen und starten
        self.collector_thread = DataCollectorThread(host, username, password, ignore_ssl)
        self.collector_thread.update_progress.connect(self.update_progress)
        self.collector_thread.collection_complete.connect(self.display_results)
        self.collector_thread.start()
    
    def update_progress(self, value, message):
        """Aktualisiert die Fortschrittsanzeige"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def display_results(self, data):
        """Zeigt die gesammelten Daten an"""
        self.data = data
        
        # VMware Tools anzeigen
        tools_html = """<h2 style="color: #00355e;">VMware Tools-Versionen</h2>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #00355e; color: white;">
            <th>VM</th>
            <th>Version</th>
            <th>Status</th>
        </tr>"""
        
        for i, tool in enumerate(data['vmware_tools']):
            bg_color = "#f3f3f3" if i % 2 == 0 else "white"
            tools_html += f"""<tr style="background-color: {bg_color};">
                <td>{tool['vm']}</td>
                <td>{tool['version']}</td>
                <td>{tool['status']}</td>
            </tr>"""
        
        tools_html += "</table>"
        self.tools_tab.setHtml(tools_html)
        
        # Snapshots anzeigen
        snapshots_html = """<h2 style="color: #00355e;">VM-Snapshots</h2>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #00355e; color: white;">
            <th>VM</th>
            <th>Name</th>
            <th>Datum</th>
            <th>Alter (Tage)</th>
            <th>Größe (MB)</th>
        </tr>"""
        
        for i, snapshot in enumerate(data['snapshots']):
            # Warnfarbe für alte Snapshots
            if snapshot['days_old'] > 30:
                bg_color = "#ffcccc"  # Hellrot für alte Snapshots
            elif snapshot['days_old'] > 14:
                bg_color = "#ffffcc"  # Hellgelb für mittelalte Snapshots
            else:
                bg_color = "#f3f3f3" if i % 2 == 0 else "white"
                
            date_str = snapshot['date'].strftime("%Y-%m-%d %H:%M")
            snapshots_html += f"""<tr style="background-color: {bg_color};">
                <td>{snapshot['vm']}</td>
                <td>{snapshot['name']}</td>
                <td>{date_str}</td>
                <td>{snapshot['days_old']}</td>
                <td>{snapshot['size_mb']}</td>
            </tr>"""
        
        snapshots_html += "</table>"
        self.snapshots_tab.setHtml(snapshots_html)
        
        # Verwaiste VMDKs anzeigen
        vmdks_html = """<h2 style="color: #00355e;">Verwaiste VMDK-Dateien</h2>
        <p>Verwaiste VMDK-Dateien sind Festplatten, die keiner VM zugeordnet sind.</p>
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #00355e; color: white;">
            <th>Datastore</th>
            <th>Pfad</th>
            <th>Name</th>
            <th>Größe (MB)</th>
            <th>Letzte Änderung</th>
        </tr>"""
        
        for i, vmdk in enumerate(data['orphaned_vmdks']):
            bg_color = "#f3f3f3" if i % 2 == 0 else "white"
            date_str = vmdk['modification_time'].strftime("%Y-%m-%d %H:%M")
            vmdks_html += f"""<tr style="background-color: {bg_color};">
                <td>{vmdk['datastore']}</td>
                <td>{vmdk['path']}</td>
                <td>{vmdk['name']}</td>
                <td>{vmdk['size_mb']}</td>
                <td>{date_str}</td>
            </tr>"""
        
        vmdks_html += "</table>"
        self.vmdks_tab.setHtml(vmdks_html)
        
        # Button aktivieren
        self.generate_button.setEnabled(True)
        self.status_label.setText("Datensammlung abgeschlossen")
    
    def generate_report(self):
        """Generiert einen Bericht im gewählten Format"""
        if not self.data:
            QMessageBox.warning(self, "Keine Daten", "Bitte verbinden Sie sich zuerst mit dem vCenter.")
            return
        
        export_format = self.export_combo.currentText()
        
        # Speicherort wählen
        file_extensions = {
            "HTML": "*.html",
            "DOCX": "*.docx",
            "PDF": "*.pdf"
        }
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Bericht speichern", "", 
            f"{export_format}-Dateien ({file_extensions[export_format]})"
        )
        
        if not file_path:
            return
        
        # Simuliere Berichtserstellung
        self.status_label.setText(f"Erstelle {export_format}-Bericht...")
        self.progress_bar.setValue(0)
        
        # Simuliere Fortschritt
        for i in range(1, 101):
            self.progress_bar.setValue(i)
            time.sleep(0.01)
            QApplication.processEvents()
        
        # Nachricht anzeigen
        QMessageBox.information(self, "Bericht erstellt", 
                            f"Der {export_format}-Bericht wurde erfolgreich erstellt:\n\n{file_path}")
        
        self.status_label.setText(f"{export_format}-Bericht wurde gespeichert unter: {file_path}")
    
    def open_demo_in_browser(self):
        """Öffnet die Demo im Browser"""
        try:
            url = f"http://localhost:{self.http_server.port}/demo.html"
            print(f"Öffne Demo-URL: {url}")
            webbrowser.open(url)
        except Exception as e:
            print(f"Fehler beim Öffnen des Browsers: {str(e)}")
            QMessageBox.warning(self, "Fehler", f"Konnte Demo nicht im Browser öffnen: {str(e)}")
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        # HTTP-Server stoppen
        self.http_server.stop()
        event.accept()

def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    
    # Bechtle-Farbpalette als Stylesheet anwenden
    app.setStyleSheet(f"""
        QMainWindow, QDialog {{
            background-color: white;
        }}
        QPushButton {{
            min-height: 24px;
            border-radius: 3px;
        }}
        QGroupBox {{
            margin-top: 20px;
        }}
        QComboBox, QLineEdit {{
            min-height: 24px;
            padding: 2px 5px;
            border: 1px solid {BECHTLE_LIGHT_GRAY};
            border-radius: 3px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {BECHTLE_BLUE};
        }}
        QProgressBar {{
            border: 1px solid {BECHTLE_LIGHT_GRAY};
            border-radius: 3px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {BECHTLE_GREEN};
        }}
        QTabWidget::pane {{
            border: 1px solid {BECHTLE_LIGHT_GRAY};
        }}
        QTextEdit {{
            border: 1px solid {BECHTLE_LIGHT_GRAY};
        }}
    """)
    
    window = DemoMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()