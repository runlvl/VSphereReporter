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
from images.bechtle_logo import get_bechtle_logo_for_qt, BECHTLE_COLORS
from core.data_collector import DataCollector
from core.report_generator import ReportGenerator

# Bechtle Farbschema
BECHTLE_DARK_BLUE = '#00355e'   # Primärfarbe
BECHTLE_ORANGE = '#da6f1e'      # Sekundärfarbe
BECHTLE_GREEN = '#23a96a'       # Akzentfarbe
BECHTLE_LIGHT_GRAY = '#f3f3f3'  # Hintergrundfarbe
BECHTLE_TEXT = '#5a5a5a'        # Textfarbe
BECHTLE_DARK_GRAY = '#5a5a5a'   # Dunkles Grau
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

# Diese Konstanten können entfernt werden, da wir sie bereits oben definiert haben

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
        self.is_running = False
        self.abort_requested = False
        
    def generate(self):
        """Generiere den Report"""
        self.is_running = True
        try:
            self.logger.info("Starte Report-Generierung")
            self.status_update.emit("Sammle Daten von vSphere...")
            
            # Prüfe regelmäßig, ob die Ausführung abgebrochen werden soll
            if self.abort_requested:
                self.logger.info("Report-Generierung abgebrochen")
                self.finished.emit(False, [], "Report-Generierung wurde abgebrochen.")
                self.is_running = False
                return
            
            # Sammle Daten
            collector = DataCollector(self.vsphere_client)
            self.logger.info("DataCollector initialisiert")
            
            # Generiere Report
            generator = ReportGenerator(collector)
            self.logger.info("ReportGenerator initialisiert")
            
            self.status_update.emit("Generiere Reports...")
            try:
                output_files = generator.generate_reports(
                    output_dir=self.output_dir,
                    formats=self.options.get('formats', ['html']),
                    optional_sections=self.options.get('sections', {})
                )
                
                if output_files and len(output_files) > 0:
                    self.logger.info(f"Report-Generierung abgeschlossen: {output_files}")
                    self.finished.emit(True, output_files, "")
                else:
                    self.logger.warning("Keine Report-Dateien wurden generiert")
                    self.finished.emit(
                        False, [], 
                        "Die Generierung wurde abgeschlossen, aber es wurden keine Report-Dateien erstellt. "
                        "Bitte prüfen Sie das Log für weitere Details."
                    )
            except Exception as report_err:
                self.logger.error(f"Fehler beim Generieren der Reports: {str(report_err)}")
                import traceback
                self.logger.error(traceback.format_exc())
                # Trotz des Fehlers in generate_reports geben wir einen leeren Report zurück,
                # aber mit einer Fehlermeldung, die den Benutzer informiert, was schief ging
                self.finished.emit(
                    False, [], 
                    f"Fehler beim Generieren der Reports: {str(report_err)}"
                )
            
        except Exception as e:
            self.logger.error(f"Fehler bei der Report-Generierung: {str(e)}")
            import traceback
            error_trace = traceback.format_exc()
            self.logger.error(error_trace)
            
            # Mehr Diagnoseinformationen protokollieren
            self.logger.error("--- Diagnose-Informationen ---")
            self.logger.error(f"Output-Verzeichnis: {self.output_dir}")
            self.logger.error(f"Gewählte Formate: {self.options.get('formats', [])}")
            self.logger.error(f"Gewählte Sektionen: {self.options.get('sections', {})}")
            
            # Überprüfen Sie die Templates und Verzeichnisse
            import os
            template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
            self.logger.error(f"Template-Verzeichnis: {template_dir}")
            self.logger.error(f"Template-Verzeichnis existiert: {os.path.exists(template_dir)}")
            
            if os.path.exists(template_dir):
                templates = [f for f in os.listdir(template_dir)]
                self.logger.error(f"Gefundene Templates: {templates}")
            
            self.finished.emit(False, [], f"Fehler bei der Report-Generierung: {str(e)}\n\nDetails: {error_trace[:500]}...")
        finally:
            # Stellen Sie sicher, dass is_running zurückgesetzt wird
            self.is_running = False

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
        
        # Lade Bechtle-Logo
        self.bechtle_logo = get_bechtle_logo_for_qt()
        if self.bechtle_logo:
            self.setWindowIcon(QIcon(self.bechtle_logo))
        
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
        
        # Header im Bechtle-Design - analog zur Linux-Version
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BECHTLE_LIGHT_GRAY};
                color: {BECHTLE_TEXT};
                margin: 0px;
                padding: 0px;
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo Container
        logo_container = QFrame()
        logo_container.setStyleSheet("background-color: transparent;")
        logo_container.setFixedWidth(120)
        logo_container_layout = QVBoxLayout(logo_container)
        logo_container_layout.setContentsMargins(0, 5, 0, 5)
        logo_container_layout.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_label = QLabel()
        logo_path = "images/logo_bechtle.png"  # Standard blaues Logo für hellen Hintergrund
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                # Skaliere das Logo proportional
                logo_pixmap = logo_pixmap.scaled(100, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(logo_pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
        else:
            # Fallback Text-Logo, falls das Bild nicht gefunden wird
            logo_label.setText("BECHTLE")
            logo_label.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-size: 18px; font-weight: bold;")
            logo_label.setAlignment(Qt.AlignCenter)
        
        logo_container_layout.addWidget(logo_label)
        header_layout.addWidget(logo_container)
        
        # Slogan Container
        slogan_container = QFrame()
        slogan_container.setStyleSheet("background-color: transparent;")
        slogan_layout = QVBoxLayout(slogan_container)
        slogan_layout.setContentsMargins(5, 5, 5, 5)
        slogan_layout.setSpacing(2)
        
        # Cloud Solutions Text
        cloud_label = QLabel("Cloud Solutions")
        cloud_label.setStyleSheet(f"color: {BECHTLE_ORANGE}; font-size: 14px; font-weight: bold;")
        cloud_label.setAlignment(Qt.AlignLeft)
        slogan_layout.addWidget(cloud_label)
        
        # Datacenter & Endpoint Text
        datacenter_label = QLabel("Datacenter & Endpoint")
        datacenter_label.setStyleSheet(f"color: {BECHTLE_TEXT}; font-size: 12px;")
        datacenter_label.setAlignment(Qt.AlignLeft)
        slogan_layout.addWidget(datacenter_label)
        
        header_layout.addWidget(slogan_container)
        
        # Vertikaler Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFixedHeight(50)
        separator.setStyleSheet(f"color: {BECHTLE_DARK_BLUE};")
        separator.setContentsMargins(15, 0, 15, 0)
        header_layout.addWidget(separator)
        
        # Anwendungsname Container
        app_container = QFrame()
        app_container.setStyleSheet("background-color: transparent;")
        app_layout = QVBoxLayout(app_container)
        app_layout.setContentsMargins(5, 5, 5, 5)
        app_layout.setSpacing(2)
        
        # Anwendungsname
        app_label = QLabel("VMware vSphere Reporter")
        app_label.setStyleSheet(f"color: {BECHTLE_DARK_BLUE}; font-size: 16px; font-weight: bold;")
        app_label.setAlignment(Qt.AlignLeft)
        app_layout.addWidget(app_label)
        
        # Version
        version_label = QLabel("Version 24.0")
        version_label.setStyleSheet(f"color: {BECHTLE_TEXT}; font-size: 10px;")
        version_label.setAlignment(Qt.AlignLeft)
        app_layout.addWidget(version_label)
        
        header_layout.addWidget(app_container, 1)  # Gibt dem App-Container den restlichen Platz
        header_layout.addStretch(1)  # Platz rechts zum Ausdehnen
        
        main_layout.addWidget(header_frame)
        
        # Erstelle Report-Optionen und andere UI-Elemente zuerst, bevor wir Menüs erstellen
        
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
        
        # Nachdem alle UI-Elemente initialisiert wurden, erstellen wir die Menüs
        self.create_menus()
        
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
        
        # Beende laufende Threads, falls vorhanden
        if hasattr(self, 'report_thread') and self.report_thread and self.report_thread.isRunning():
            self.logger.warning("Es läuft bereits ein Report-Thread - beende diesen zuerst")
            if hasattr(self, 'report_worker') and self.report_worker:
                self.report_worker.abort_requested = True
            self.report_thread.quit()
            self.report_thread.wait(2000)  # 2 Sekunden warten
            if self.report_thread.isRunning():
                self.logger.warning("Thread konnte nicht beendet werden, versuche es nochmal")
                self.report_thread.terminate()
                self.report_thread.wait(1000)  # 1 Sekunde warten
        
        # Optionen sammeln
        selected_options = self.report_options.get_selected_options()
        options = {
            'formats': selected_options['formats'],
            'sections': selected_options['sections']
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
        
        # Speichere die Thread-Referenz
        self.report_thread = thread
        
        # Verbinde Signale
        self.report_worker.status_update.connect(progress.update_status)
        self.report_worker.finished.connect(lambda success, files, error: 
                                          self.report_finished(success, files, progress, error, thread))
        thread.finished.connect(thread.deleteLater)
        self.report_worker.finished.connect(self.report_worker.deleteLater)
        
        # Fortschrittsdialog für Abbruch vorbereiten
        progress.enable_cancel(lambda: self.cancel_report_generation(thread))
        
        # Starte Thread
        thread.start()
    
    def report_finished(self, success, output_files, progress_dialog, error=None, thread=None):
        """Behandle das Ergebnis der Report-Generierung"""
        progress_dialog.close()
        
        # Thread sicher beenden
        if thread and thread.isRunning():
            thread.quit()
            thread.wait(2000)  # 2 Sekunden warten, damit der Thread ordnungsgemäß beendet wird
        
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
    
    def cancel_report_generation(self, thread):
        """Bricht die laufende Report-Generierung ab"""
        self.logger.info("Abbruch der Report-Generierung angefordert")
        
        if hasattr(self, 'report_worker') and self.report_worker and hasattr(self.report_worker, 'abort_requested'):
            self.report_worker.abort_requested = True
            self.logger.info("Worker über Abbruch informiert")
        
        if thread and thread.isRunning():
            thread.quit()
            success = thread.wait(2000)  # 2 Sekunden warten
            
            if not success or thread.isRunning():
                self.logger.warning("Thread konnte nicht ordnungsgemäß beendet werden")
                thread.terminate()
                self.logger.warning("Thread wurde forciert beendet")
            else:
                self.logger.info("Thread erfolgreich beendet")
    
    def show_about(self):
        """Zeige den Über-Dialog"""
        QMessageBox.about(self, "Über VMware vSphere Reporter",
                         """<h1>VMware vSphere Reporter</h1>
                         <p>Version 24.0</p>
                         <p>Ein umfassendes Reporting-Tool für VMware vSphere-Umgebungen</p>
                         <p>Entwickelt für Bechtle GmbH</p>
                         <p>Copyright &copy; 2025 Bechtle GmbH</p>""")
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        self.logger.info("Anwendung wird beendet...")
        
        # Verbindung zum vCenter trennen, falls vorhanden
        if self.connected and self.vsphere_client:
            self.vsphere_client.disconnect()
            self.logger.info(f"Verbindung zu {self.server} getrennt")
        
        # Alle laufenden Threads beenden
        if hasattr(self, 'report_thread') and self.report_thread and self.report_thread.isRunning():
            self.logger.info("Beende laufenden Report-Thread...")
            
            # Versuche den Worker zu benachrichtigen
            if hasattr(self, 'report_worker') and self.report_worker and hasattr(self.report_worker, 'abort_requested'):
                self.report_worker.abort_requested = True
                self.logger.info("Worker über Abbruch informiert")
            
            # Thread beenden
            self.report_thread.quit()
            success = self.report_thread.wait(3000)  # 3 Sekunden warten
            
            if not success or self.report_thread.isRunning():
                self.logger.warning("Thread konnte nicht ordnungsgemäß beendet werden")
                # Forcieren beenden (nicht ideal, aber verhindert hängende Threads)
                self.report_thread.terminate()
                self.logger.warning("Thread wurde forciert beendet")
            else:
                self.logger.info("Thread erfolgreich beendet")
            
        self.logger.info("Anwendung wird beendet")
        event.accept()