#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Main Window
The main application window for the VMware vSphere Reporter
"""

import os
import sys
import logging
import platform
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QCheckBox, 
                            QGroupBox, QTextEdit, QMessageBox, QFileDialog,
                            QSplitter, QAction, QMenu, QToolBar, QStatusBar,
                            QDialog, QTabWidget, QFrame, QSpacerItem,
                            QSizePolicy, QProgressBar)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QObject

from gui.connection_dialog import ConnectionDialog
from gui.progress_dialog import ProgressDialog
from gui.report_options import ReportOptionsPanel
from core.vsphere_client import VSphereClient
from core.data_collector import DataCollector
from core.report_generator import ReportGenerator
# Dynamischer Import des Loggers
import importlib.util
import sys

# Versuche zuerst den normalen Import
try:
    from utils.logger import get_logger
except ImportError:
    # Fallback: Dynamischer Import
    logger_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', 'logger.py')
    if os.path.exists(logger_path):
        spec = importlib.util.spec_from_file_location("logger_module", logger_path)
        logger_module = importlib.util.module_from_spec(spec)
        sys.modules["logger_module"] = logger_module
        spec.loader.exec_module(logger_module)
        
        # Füge die fehlende get_logger-Funktion hinzu, falls sie nicht existiert
        if not hasattr(logger_module, 'get_logger'):
            def get_logger(name=None):
                if name is None:
                    return logger_module.setup_logger()
                else:
                    logger = logger_module.setup_logger()
                    return logging.getLogger(name)
            logger_module.get_logger = get_logger
            
        # Importiere get_logger aus dem dynamisch geladenen Modul
        get_logger = logger_module.get_logger
    else:
        # Letzter Fallback: Eigene Logger-Funktion
        print("WARNUNG: Logger-Modul konnte nicht geladen werden, verwende Fallback-Logger")
        def get_logger(name=None):
            if name is None:
                logger = logging.getLogger()
            else:
                logger = logging.getLogger(name)
                
            if not logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            return logger

# Bechtle-Farbschema
BECHTLE_DARK_BLUE = "#00355e"
BECHTLE_ORANGE = "#da6f1e"
BECHTLE_GREEN = "#23a96a"
BECHTLE_LIGHT_GRAY = "#f3f3f3"
BECHTLE_DARK_GRAY = "#5a5a5a"

class GenerateReportWorker(QObject):
    """Worker-Thread für die Report-Generierung"""
    finished = pyqtSignal(bool, list, str)
    status_update = pyqtSignal(str)
    
    def __init__(self, vsphere_client, options, output_dir):
        super().__init__()
        self.vsphere_client = vsphere_client
        self.options = options
        self.output_dir = output_dir
        self.logger = get_logger(__name__)
        
    def generate(self):
        """Generiere den Report"""
        try:
            self.logger.info("Starte Report-Generierung")
            self.status_update.emit("Sammle Daten von vSphere...")
            
            # Sammle Daten
            collector = DataCollector(self.vsphere_client)
            
            # Generiere Report
            generator = ReportGenerator(collector)
            
            self.status_update.emit("Generiere Reports...")
            output_files = generator.generate_reports(
                output_dir=self.output_dir,
                formats=self.options.get('formats', ['html']),
                optional_sections=self.options.get('sections', {})
            )
            
            self.logger.info(f"Report-Generierung abgeschlossen: {output_files}")
            self.finished.emit(True, output_files, "")
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Report-Generierung: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.finished.emit(False, [], str(e))

class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""
    
    def __init__(self):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.logger.info("Initialisiere Hauptfenster")
        
        self.vsphere_client = None
        self.connected = False
        self.server = ""
        self.username = ""
        
        self.init_ui()
        
    def init_ui(self):
        """Initialisiere die Benutzeroberfläche"""
        # Setze Fenster-Eigenschaften
        self.setWindowTitle("VMware vSphere Reporter")
        self.resize(900, 700)
        self.setMinimumSize(800, 600)
        
        # Setze Bechtle-Farbschema
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{
                background-color: white;
            }}
            QGroupBox {{
                border: 1px solid {BECHTLE_LIGHT_GRAY};
                border-radius: 3px;
                margin-top: 0.5em;
                padding-top: 0.5em;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: {BECHTLE_DARK_BLUE};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {BECHTLE_DARK_BLUE};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #00477e;
            }}
            QPushButton:disabled {{
                background-color: {BECHTLE_LIGHT_GRAY};
                color: {BECHTLE_DARK_GRAY};
            }}
            QComboBox {{
                border: 1px solid {BECHTLE_LIGHT_GRAY};
                border-radius: 3px;
                padding: 3px;
            }}
            QTextEdit {{
                border: 1px solid {BECHTLE_LIGHT_GRAY};
                border-radius: 3px;
            }}
            QStatusBar {{
                background-color: {BECHTLE_DARK_BLUE};
                color: white;
            }}
        """)
        
        # Setze zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Hauptlayout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Erstelle Menüs
        self.create_menus()
        
        # Erstelle Statusleiste
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Bereit")
        
        # Verbindungsstatus
        connection_frame = QFrame()
        connection_frame.setFrameShape(QFrame.StyledPanel)
        connection_frame.setFrameShadow(QFrame.Raised)
        connection_layout = QHBoxLayout(connection_frame)
        
        connection_label = QLabel("Verbindungsstatus:")
        connection_layout.addWidget(connection_label)
        
        self.connection_status = QLabel("Nicht verbunden")
        self.connection_status.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-weight: bold;")
        connection_layout.addWidget(self.connection_status)
        
        connection_layout.addStretch(1)  # Spacer
        
        self.connect_button = QPushButton("Verbinden")
        self.connect_button.clicked.connect(self.show_connection_dialog)
        connection_layout.addWidget(self.connect_button)
        
        self.disconnect_button = QPushButton("Trennen")
        self.disconnect_button.clicked.connect(self.disconnect)
        self.disconnect_button.setEnabled(False)
        connection_layout.addWidget(self.disconnect_button)
        
        main_layout.addWidget(connection_frame)
        
        # Hauptsplitter (Report-Optionen und Log)
        splitter = QSplitter(Qt.Vertical)
        
        # Report-Optionen
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        
        options_group = QGroupBox("Report-Optionen")
        options_group_layout = QVBoxLayout()
        
        self.report_options = ReportOptionsPanel()
        options_group_layout.addWidget(self.report_options)
        
        options_button_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Alle auswählen")
        self.select_all_button.clicked.connect(self.report_options.select_all)
        options_button_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton("Alle abwählen")
        self.deselect_all_button.clicked.connect(self.report_options.deselect_all)
        options_button_layout.addWidget(self.deselect_all_button)
        
        options_button_layout.addStretch(1)
        
        self.generate_button = QPushButton("Report generieren")
        self.generate_button.clicked.connect(self.generate_report)
        self.generate_button.setEnabled(False)
        self.generate_button.setStyleSheet(f"""
            background-color: {BECHTLE_GREEN};
            color: white;
            font-weight: bold;
            font-size: 14px;
            padding: 8px 15px;
        """)
        options_button_layout.addWidget(self.generate_button)
        
        options_group_layout.addLayout(options_button_layout)
        options_group.setLayout(options_group_layout)
        options_layout.addWidget(options_group)
        
        # Ausgabeverzeichnis
        output_dir_group = QGroupBox("Ausgabeverzeichnis")
        output_dir_layout = QHBoxLayout()
        
        self.output_dir = QLabel(os.path.join(os.path.expanduser("~"), "vsphere_reports"))
        output_dir_layout.addWidget(self.output_dir)
        
        output_dir_button = QPushButton("Ändern")
        output_dir_button.clicked.connect(self.change_output_dir)
        output_dir_layout.addWidget(output_dir_button)
        
        output_dir_group.setLayout(output_dir_layout)
        options_layout.addWidget(output_dir_group)
        
        splitter.addWidget(options_frame)
        
        # Log-Bereich
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        
        log_header_layout = QHBoxLayout()
        log_label = QLabel("Log-Ausgabe:")
        log_header_layout.addWidget(log_label)
        
        log_level_label = QLabel("Log-Level:")
        log_header_layout.addWidget(log_level_label)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.currentTextChanged.connect(self.change_log_level)
        log_header_layout.addWidget(self.log_level_combo)
        
        log_layout.addLayout(log_header_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_frame)
        
        # Setze initiale Größen
        splitter.setSizes([300, 150])
        
        main_layout.addWidget(splitter)
        
        # Verbinde Logger mit Log-Widget
        self.setup_log_handler()
        
        self.logger.info("Benutzeroberfläche initialisiert")
    
    def create_menus(self):
        """Erstelle die Menüs"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("Datei")
        
        connect_action = QAction("Verbinden...", self)
        connect_action.triggered.connect(self.show_connection_dialog)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction("Trennen", self)
        disconnect_action.triggered.connect(self.disconnect)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Report-Menü
        report_menu = menubar.addMenu("Report")
        
        generate_action = QAction("Report generieren...", self)
        generate_action.triggered.connect(self.generate_report)
        report_menu.addAction(generate_action)
        
        # Optionen-Menü
        options_menu = menubar.addMenu("Optionen")
        
        select_all_action = QAction("Alle Optionen auswählen", self)
        select_all_action.triggered.connect(self.report_options.select_all)
        options_menu.addAction(select_all_action)
        
        deselect_all_action = QAction("Alle Optionen abwählen", self)
        deselect_all_action.triggered.connect(self.report_options.deselect_all)
        options_menu.addAction(deselect_all_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("Hilfe")
        
        help_action = QAction("Hilfe", self)
        # help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("Über", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_log_handler(self):
        """Verbinde Logger mit Log-Widget"""
        class QTextEditLogger(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget
                self.widget.setReadOnly(True)
                
            def emit(self, record):
                msg = self.format(record)
                # Setze Farbe basierend auf Log-Level
                color = "black"
                if record.levelno >= logging.ERROR:
                    color = "red"
                elif record.levelno >= logging.WARNING:
                    color = "orange"
                elif record.levelno <= logging.DEBUG:
                    color = "gray"
                
                self.widget.append(f'<span style="color: {color};">{msg}</span>')
                self.widget.ensureCursorVisible()
        
        text_handler = QTextEditLogger(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        text_handler.setLevel(logging.INFO)
        
        # Entferne bestehende Handler
        log = logging.getLogger()
        for handler in log.handlers[:]:
            if isinstance(handler, QTextEditLogger):
                log.removeHandler(handler)
        
        # Füge neuen Handler hinzu
        log.addHandler(text_handler)
    
    def change_log_level(self, level):
        """Ändere das Log-Level"""
        numeric_level = getattr(logging, level, None)
        if isinstance(numeric_level, int):
            for handler in logging.getLogger().handlers:
                if isinstance(handler, logging.Handler):
                    handler.setLevel(numeric_level)
            self.logger.info(f"Log-Level auf {level} gesetzt")
    
    def change_output_dir(self):
        """Ändere das Ausgabeverzeichnis"""
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self, "Ausgabeverzeichnis wählen", 
            self.output_dir.text(), options=options
        )
        
        if directory:
            self.output_dir.setText(directory)
            self.logger.info(f"Ausgabeverzeichnis auf {directory} gesetzt")
    
    def show_connection_dialog(self):
        """Zeige den Verbindungsdialog"""
        dialog = ConnectionDialog(self)
        dialog.accepted.connect(lambda: self.connect_to_vcenter(
            dialog.server, dialog.username, dialog.password, dialog.ignore_ssl
        ))
        dialog.exec_()
    
    def connect_to_vcenter(self, server, username, password, ignore_ssl):
        """Verbinde mit vCenter"""
        self.logger.info(f"Verbindung zu {server} als {username} wird hergestellt...")
        
        # Zeige Fortschrittsdialog
        progress = ProgressDialog("Verbindung wird hergestellt", "Verbindung zu vCenter wird hergestellt...", self)
        progress.show()
        
        # Erstelle Client und verbinde in einem separaten Thread
        self.vsphere_client = VSphereClient(server, username, password, ignore_ssl)
        
        # Nutze QThread für die Verbindung
        class ConnectThread(QThread):
            connected = pyqtSignal(bool, str)
            
            def __init__(self, client):
                super().__init__()
                self.client = client
                
            def run(self):
                success = self.client.connect()
                error = self.client.last_error if not success else ""
                self.connected.emit(success, error)
        
        self.connect_thread = ConnectThread(self.vsphere_client)
        self.connect_thread.connected.connect(lambda success, error: self.connection_finished(
            success, server, username, progress, error
        ))
        self.connect_thread.start()
    
    def connection_finished(self, success, server, username, progress_dialog, error=None):
        """Behandle das Ergebnis des Verbindungsaufbaus"""
        progress_dialog.close()
        
        if success:
            self.logger.info(f"Verbindung zu {server} hergestellt")
            self.connected = True
            self.server = server
            self.username = username
            self.update_connection_status(True, server, username)
            
            # Aktiviere Bedienelemente
            self.generate_button.setEnabled(True)
            self.disconnect_button.setEnabled(True)
            self.connect_button.setEnabled(False)
            
        else:
            error_msg = error if error else "Unbekannter Fehler bei der Verbindung zu vCenter"
            self.logger.error(f"Verbindungsfehler: {error_msg}")
            QMessageBox.critical(self, "Verbindungsfehler", 
                                f"Fehler bei der Verbindung zu {server}:\n\n{error_msg}")
            self.connected = False
            self.update_connection_status(False)
    
    def update_connection_status(self, is_connected, server=None, username=None):
        """Aktualisiere die Anzeige des Verbindungsstatus"""
        if is_connected:
            self.connection_status.setText(f"Verbunden mit {server} als {username}")
            self.connection_status.setStyleSheet(f"color: {BECHTLE_GREEN}; font-weight: bold;")
        else:
            self.connection_status.setText("Nicht verbunden")
            self.connection_status.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-weight: bold;")
    
    def disconnect(self):
        """Trenne die Verbindung zu vCenter"""
        if self.vsphere_client:
            self.vsphere_client.disconnect()
            self.logger.info(f"Verbindung zu {self.server} getrennt")
            
        self.vsphere_client = None
        self.connected = False
        self.server = ""
        self.username = ""
        
        # Deaktiviere Bedienelemente
        self.generate_button.setEnabled(False)
        self.disconnect_button.setEnabled(False)
        self.connect_button.setEnabled(True)
        
        self.update_connection_status(False)
    
    def generate_report(self):
        """Generiere den Report"""
        if not self.connected or not self.vsphere_client:
            QMessageBox.warning(self, "Nicht verbunden", 
                               "Bitte stellen Sie zuerst eine Verbindung zu vCenter her.")
            return
        
        # Optionen sammeln
        options = {
            'formats': self.report_options.get_selected_formats(),
            'sections': self.report_options.get_selected_sections()
        }
        
        # Prüfe, ob ein Format ausgewählt ist
        if not options['formats']:
            QMessageBox.warning(self, "Keine Formate ausgewählt", 
                               "Bitte wählen Sie mindestens ein Ausgabeformat aus.")
            return
        
        # Starte Report-Generierung
        self.logger.info("Starte Report-Generierung")
        
        # Zeige Fortschrittsdialog
        progress = ProgressDialog("Report wird generiert", "Die vSphere-Daten werden gesammelt...", self)
        progress.show()
        
        # Worker für Report-Generierung
        self.report_worker = GenerateReportWorker(
            self.vsphere_client, 
            options, 
            self.output_dir.text()
        )
        
        # Thread für Report-Generierung
        thread = QThread()
        self.report_worker.moveToThread(thread)
        thread.started.connect(self.report_worker.generate)
        
        # Verbinde Signale
        self.report_worker.status_update.connect(progress.update_status)
        self.report_worker.finished.connect(lambda success, files, error: 
                                          self.report_finished(success, files, progress, error))
        thread.finished.connect(thread.deleteLater)
        
        # Starte Thread
        thread.start()
    
    def report_finished(self, success, output_files, progress_dialog, error=None):
        """Behandle das Ergebnis der Report-Generierung"""
        progress_dialog.close()
        
        if success:
            self.logger.info(f"Report-Generierung abgeschlossen: {output_files}")
            
            # Zeige Erfolgsmaeldung mit Links zu den Dateien
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Report generiert")
            
            file_text = "<ul>"
            for file_path in output_files:
                file_name = os.path.basename(file_path)
                file_text += f"<li>{file_name}</li>"
            file_text += "</ul>"
            
            msg_box.setText(f"Die folgenden Reports wurden erfolgreich generiert in: {self.output_dir.text()}")
            msg_box.setInformativeText(file_text)
            
            # Buttons hinzufügen
            msg_box.addButton(QPushButton("Verzeichnis öffnen"), QMessageBox.ActionRole)
            msg_box.addButton(QMessageBox.Ok)
            
            # Dialog anzeigen
            result = msg_box.exec_()
            
            # Wenn "Verzeichnis öffnen" geklickt wurde
            if result == 0:  # Erster Button ist Index 0
                if platform.system() == "Windows":
                    os.startfile(self.output_dir.text())
                elif platform.system() == "Darwin":
                    os.system(f"open {self.output_dir.text()}")
                else:
                    os.system(f"xdg-open {self.output_dir.text()}")
        else:
            error_msg = error if error else "Unbekannter Fehler bei der Report-Generierung"
            self.logger.error(f"Fehler bei der Report-Generierung: {error_msg}")
            QMessageBox.critical(self, "Fehler bei der Report-Generierung", 
                                f"Bei der Generierung des Reports ist ein Fehler aufgetreten:\n\n{error_msg}")
    
    def show_about(self):
        """Zeige den Über-Dialog"""
        QMessageBox.about(self, "Über VMware vSphere Reporter",
                         """<h1>VMware vSphere Reporter</h1>
                         <p>Version 1.0.0</p>
                         <p>Ein umfassendes Reporting-Tool für VMware vSphere-Umgebungen</p>
                         <p>Entwickelt für Bechtle GmbH</p>
                         <p>Copyright &copy; 2025 Bechtle GmbH</p>""")
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        if self.connected and self.vsphere_client:
            self.vsphere_client.disconnect()
            self.logger.info(f"Verbindung zu {self.server} getrennt")
            
        event.accept()