#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main application window for VMware vSphere Reporter
"""

import os
import sys
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QMessageBox, QFileDialog, 
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QComboBox, QGroupBox, QCheckBox, QTabWidget,
    QSplitter, QTextEdit, QStatusBar, QFrame
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette

from gui.connection_dialog import ConnectionDialog
from gui.report_options import ReportOptionsWidget
from gui.progress_dialog import ProgressDialog
from core.vsphere_client import VSphereClient
from core.report_generator import ReportGenerator
from core.data_collector import DataCollector
from utils.helper import get_save_directory
from utils.logger import set_log_level, get_log_level_name, get_log_level_from_name
from images.bechtle_logo import get_bechtle_logo_for_qt, BECHTLE_COLORS

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.vsphere_client = None
        self.connected = False
        self.report_options = None
        
        # Bechtle corporate colors
        self.bechtle_primary = BECHTLE_COLORS['primary']
        self.bechtle_secondary = BECHTLE_COLORS['secondary']
        self.bechtle_accent = BECHTLE_COLORS['accent']
        self.bechtle_bg = BECHTLE_COLORS['bg']
        self.bechtle_text = BECHTLE_COLORS['text']
        
        # Apply Bechtle style
        self.apply_bechtle_style()
        
        # Initialize UI
        self.init_ui()
        
    def apply_bechtle_style(self):
        """Apply Bechtle corporate style to the application"""
        # Set application palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.bechtle_bg))
        palette.setColor(QPalette.WindowText, QColor(self.bechtle_text))
        palette.setColor(QPalette.Base, QColor(self.bechtle_bg))
        palette.setColor(QPalette.AlternateBase, QColor(self.bechtle_bg))
        palette.setColor(QPalette.ToolTipBase, QColor('white'))
        palette.setColor(QPalette.ToolTipText, QColor(self.bechtle_text))
        palette.setColor(QPalette.Text, QColor(self.bechtle_text))
        palette.setColor(QPalette.Button, QColor(self.bechtle_bg))
        palette.setColor(QPalette.ButtonText, QColor(self.bechtle_primary))
        palette.setColor(QPalette.BrightText, QColor('white'))
        palette.setColor(QPalette.Highlight, QColor(self.bechtle_primary))
        palette.setColor(QPalette.HighlightedText, QColor('white'))
        self.setPalette(palette)
        
        # Set stylesheet
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ 
                background-color: {self.bechtle_bg}; 
                color: {self.bechtle_text};
            }}
            QGroupBox {{ 
                border: 1px solid {self.bechtle_primary}; 
                border-radius: 5px; 
                margin-top: 1ex; 
                font-weight: bold;
                padding: 10px;
            }}
            QGroupBox::title {{ 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 5px; 
                color: {self.bechtle_primary};
            }}
            QPushButton {{ 
                background-color: {self.bechtle_primary}; 
                color: white; 
                border: none; 
                border-radius: 3px; 
                padding: 5px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background-color: {self.bechtle_secondary}; 
            }}
            QPushButton:disabled {{ 
                background-color: #cccccc; 
                color: #666666; 
            }}
            QComboBox, QLineEdit {{ 
                border: 1px solid {self.bechtle_primary}; 
                border-radius: 3px; 
                padding: 2px 5px; 
                background-color: white;
                color: {self.bechtle_text};
            }}
            QTabWidget::pane {{ 
                border: 1px solid {self.bechtle_primary}; 
                border-radius: 3px; 
            }}
            QTabBar::tab {{ 
                background-color: {self.bechtle_bg}; 
                border: 1px solid {self.bechtle_primary}; 
                border-bottom: none; 
                border-top-left-radius: 3px; 
                border-top-right-radius: 3px; 
                padding: 5px 10px; 
                color: {self.bechtle_text};
            }}
            QTabBar::tab:selected {{ 
                background-color: {self.bechtle_primary}; 
                color: white;
            }}
            QCheckBox::indicator:checked {{ 
                background-color: {self.bechtle_accent}; 
            }}
        """)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("VMware vSphere Reporter | Bechtle AG")
        self.setMinimumSize(900, 700)
        self.resize(900, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create header with Bechtle branding
        self.create_bechtle_header(main_layout)
        
        # Create top status area
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 10, 0, 10)
        
        status_label = QLabel("Connection Status:")
        status_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        status_label.setStyleSheet(f"color: {self.bechtle_primary};")
        
        self.connection_status = QLabel("Not connected to vCenter")
        self.connection_status.setStyleSheet(f"color: {self.bechtle_secondary}; font-weight: bold;")
        
        self.connect_button = QPushButton("Connect to vCenter")
        self.connect_button.clicked.connect(self.show_connection_dialog)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.connection_status)
        status_layout.addStretch(1)
        status_layout.addWidget(self.connect_button)
        
        main_layout.addLayout(status_layout)
        
        # Create report options widget
        self.report_options_widget = ReportOptionsWidget()
        self.report_options_widget.setEnabled(False)
        main_layout.addWidget(self.report_options_widget)
        
        # Create export options and log settings
        options_frame = QFrame()
        options_layout = QHBoxLayout(options_frame)
        options_layout.setContentsMargins(0, 0, 0, 0)
        
        # Export options section
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        
        self.export_format = QComboBox()
        self.export_format.addItems(["HTML", "DOCX", "PDF", "All Formats"])
        format_layout.addWidget(self.export_format)
        format_layout.addStretch(1)
        
        export_layout.addLayout(format_layout)
        
        self.export_button = QPushButton("Generate Report")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.generate_report)
        export_layout.addWidget(self.export_button)
        
        export_group.setLayout(export_layout)
        options_layout.addWidget(export_group)
        
        # Log settings section
        log_settings_group = QGroupBox("Log Settings")
        log_settings_layout = QVBoxLayout()
        
        log_level_layout = QHBoxLayout()
        log_level_layout.addWidget(QLabel("Log Detail Level:"))
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        # Set default to INFO (index 1)
        self.log_level_combo.setCurrentIndex(1)
        self.log_level_combo.currentIndexChanged.connect(self.change_log_level)
        log_level_layout.addWidget(self.log_level_combo)
        
        log_settings_layout.addLayout(log_level_layout)
        
        log_info_label = QLabel(
            "Debug: Shows all messages including detailed diagnostics\n"
            "Info: Normal operational messages (Default)\n"
            "Warning: Issues that might need attention\n"
            "Error: Serious issues affecting functionality\n"
            "Critical: Critical errors requiring immediate attention"
        )
        log_info_label.setStyleSheet("font-size: 10px; color: #666666;")
        log_settings_layout.addWidget(log_info_label)
        
        log_settings_group.setLayout(log_settings_layout)
        options_layout.addWidget(log_settings_group)
        
        main_layout.addWidget(options_frame)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Center the window
        self.center()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        connect_action = QAction("&Connect to vCenter", self)
        connect_action.setShortcut("Ctrl+C")
        connect_action.setStatusTip("Connect to vCenter server")
        connect_action.triggered.connect(self.show_connection_dialog)
        file_menu.addAction(connect_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About VMware vSphere Reporter")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
    def center(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen)
        self.move(frame_geometry.topLeft())
        
    def show_connection_dialog(self):
        """Show the connection dialog"""
        dialog = ConnectionDialog(self)
        if dialog.exec_():
            # Get connection details
            server = dialog.server_edit.text()
            username = dialog.username_edit.text()
            password = dialog.password_edit.text()
            ignore_ssl = dialog.ignore_ssl_check.isChecked()
            
            # Show progress dialog
            progress = ProgressDialog("Connecting to vCenter", "Establishing connection to vCenter server...", self)
            progress.show()
            
            # Create connection worker
            self.connection_worker = ConnectionWorker(server, username, password, ignore_ssl)
            self.connection_worker.finished.connect(progress.close)
            self.connection_worker.finished.connect(self.connection_finished)
            self.connection_worker.start()
    
    def connection_finished(self, success, client, error_message=None):
        """Handle connection completion"""
        if success:
            self.vsphere_client = client
            self.connected = True
            self.connection_status.setText(f"Connected to: {self.vsphere_client.server}")
            self.connection_status.setStyleSheet(f"color: {self.bechtle_accent}; font-weight: bold;")
            self.connect_button.setText("Reconnect")
            self.report_options_widget.setEnabled(True)
            self.export_button.setEnabled(True)
            self.statusBar.showMessage("Connected to vCenter successfully", 3000)
        else:
            QMessageBox.critical(self, "Connection Error", 
                                f"Failed to connect to vCenter:\n{error_message}")
            self.connection_status.setStyleSheet(f"color: {self.bechtle_secondary}; font-weight: bold;")
            self.statusBar.showMessage("Connection failed", 3000)
    
    def generate_report(self):
        """Generate the report based on selected options"""
        if not self.connected:
            QMessageBox.warning(self, "Not Connected", 
                               "Please connect to a vCenter server first.")
            return
        
        # Get selected report options
        options = self.report_options_widget.get_selected_options()
        if not options:
            QMessageBox.warning(self, "No Options Selected", 
                               "Please select at least one report option.")
            return
        
        # Get export format
        export_format = self.export_format.currentText()
        
        # Get save directory
        save_dir = get_save_directory(self)
        if not save_dir:
            return
        
        # Show progress dialog
        progress = ProgressDialog("Generating Report", "Collecting data from vCenter...", self)
        progress.show()
        
        # Create report worker
        self.report_worker = ReportWorker(
            self.vsphere_client, 
            options, 
            export_format, 
            save_dir
        )
        self.report_worker.progress_update.connect(progress.set_status)
        self.report_worker.progress_value.connect(progress.set_progress)
        self.report_worker.finished.connect(progress.close)
        self.report_worker.finished.connect(self.report_finished)
        self.report_worker.start()
    
    def report_finished(self, success, output_files, error_message=None):
        """Handle report generation completion"""
        if success:
            message = f"Report generated successfully.\n\nFiles created:\n"
            for file_path in output_files:
                message += f"- {file_path}\n"
            
            QMessageBox.information(self, "Report Generated", message)
            self.statusBar.showMessage("Report generated successfully", 3000)
        else:
            QMessageBox.critical(self, "Report Generation Error", 
                                f"Failed to generate report:\n{error_message}")
            self.statusBar.showMessage("Report generation failed", 3000)
    
    def show_about_dialog(self):
        """Show the about dialog"""
        # Apply Bechtle style to the about dialog
        about_text = (
            f"<html>"
            f"<head>"
            f"<style>"
            f"body {{ font-family: 'Segoe UI', Arial, sans-serif; }}"
            f"h1 {{ color: {self.bechtle_primary}; }}"
            f"h2 {{ color: {self.bechtle_secondary}; }}"
            f".accent {{ color: {self.bechtle_accent}; }}"
            f"</style>"
            f"</head>"
            f"<body>"
            f"<h1>VMware vSphere Reporter</h1>"
            f"<p><b>Version 1.0.0</b></p>"
            f"<p>A comprehensive reporting tool for VMware vSphere environments.</p>"
            f"<p>This tool allows you to generate detailed reports about your "
            f"vSphere environment including:</p>"
            f"<ul>"
            f"<li><span class='accent'>VMware Tools versions</span> (sorted by oldest first)</li>"
            f"<li><span class='accent'>VM Snapshot status</span> (sorted by age)</li>"
            f"<li><span class='accent'>Orphaned VMDK files</span></li>"
            f"<li>And more...</li>"
            f"</ul>"
            f"<p>© 2025 Bechtle AG</p>"
            f"</body>"
            f"</html>"
        )
        
        # Create custom styled message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About VMware vSphere Reporter")
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Set icon
        logo_pixmap = get_bechtle_logo_for_qt()
        if logo_pixmap:
            msg_box.setIconPixmap(logo_pixmap)
        
        # Show the dialog
        msg_box.exec_()
    
    def create_bechtle_header(self, layout):
        """Create header with Bechtle branding"""
        try:
            # Create a frame for the header
            header_frame = QFrame()
            header_frame.setStyleSheet(f"background-color: {self.bechtle_bg}; border: none;")
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(0, 0, 0, 10)
            
            # Try to load logo
            logo_pixmap = get_bechtle_logo_for_qt()
            
            # Left side - logo
            logo_frame = QFrame()
            logo_frame.setStyleSheet(f"background-color: {self.bechtle_bg}; border: none;")
            logo_layout = QVBoxLayout(logo_frame)
            logo_layout.setContentsMargins(10, 0, 10, 0)
            
            if logo_pixmap:
                logo_label = QLabel()
                logo_label.setPixmap(logo_pixmap)
                logo_layout.addWidget(logo_label)
            else:
                # Fallback to text if image can't be loaded
                logo_text = QLabel("BECHTLE")
                logo_text.setFont(QFont("Segoe UI", 18, QFont.Bold))
                logo_text.setStyleSheet(f"color: {self.bechtle_primary};")
                logo_layout.addWidget(logo_text)
            
            header_layout.addWidget(logo_frame)
            
            # First slogan frame - Bechtle branding
            slogan_frame = QFrame()
            slogan_frame.setStyleSheet(f"background-color: {self.bechtle_bg}; border: none;")
            slogan_layout = QVBoxLayout(slogan_frame)
            slogan_layout.setContentsMargins(0, 5, 0, 0)
            slogan_layout.setSpacing(0)
            
            slogan_main = QLabel("Cloud Solutions")
            slogan_main.setFont(QFont("Segoe UI", 14, QFont.Bold))
            slogan_main.setStyleSheet(f"color: {self.bechtle_secondary};")  # Orange color for main slogan
            slogan_layout.addWidget(slogan_main)
            
            slogan_sub = QLabel("Datacenter & Endpoint")
            slogan_sub.setFont(QFont("Segoe UI", 12))
            slogan_sub.setStyleSheet(f"color: {self.bechtle_text};")  # Dark gray for sub-slogan
            slogan_layout.addWidget(slogan_sub)
            
            header_layout.addWidget(slogan_frame)
            
            # Vertical separator line
            separator = QFrame()
            separator.setFrameShape(QFrame.VLine)
            separator.setFixedWidth(2)
            separator.setStyleSheet(f"background-color: {self.bechtle_primary};")
            header_layout.addWidget(separator, 0, Qt.AlignCenter)
            
            # Second slogan frame - Application name
            app_frame = QFrame()
            app_frame.setStyleSheet(f"background-color: {self.bechtle_bg}; border: none;")
            app_layout = QVBoxLayout(app_frame)
            app_layout.setContentsMargins(10, 5, 0, 0)
            app_layout.setSpacing(0)
            
            app_name = QLabel("VMware vSphere Reporter")
            app_name.setFont(QFont("Segoe UI", 16, QFont.Bold))
            app_name.setStyleSheet(f"color: {self.bechtle_primary};")  # Primary blue color for app name
            app_layout.addWidget(app_name)
            
            # Version text
            version_text = QLabel("Version 1.0.0")
            version_text.setFont(QFont("Segoe UI", 10))
            version_text.setStyleSheet(f"color: {self.bechtle_text};")
            app_layout.addWidget(version_text)
            
            header_layout.addWidget(app_frame)
            
            # Add stretch at the end to push everything to the left
            header_layout.addStretch(1)
            
            # Add the header to the main layout
            layout.addWidget(header_frame)
            
            # Add a horizontal line
            separator_line = QFrame()
            separator_line.setFrameShape(QFrame.HLine)
            separator_line.setFixedHeight(2)
            separator_line.setStyleSheet(f"background-color: {self.bechtle_primary};")
            layout.addWidget(separator_line)
            
        except Exception as e:
            logger.warning(f"Could not create Bechtle header: {str(e)}")
    
    def change_log_level(self, index):
        """
        Change the logging level based on the combo box selection
        
        Args:
            index (int): Index of the selected item in the combo box
        """
        log_level_name = self.log_level_combo.currentText()
        log_level = get_log_level_from_name(log_level_name)
        
        # Set the new log level
        set_log_level(log_level)
        
        # Show confirmation in status bar
        self.statusBar.showMessage(f"Log level changed to {log_level_name}", 3000)
        logger.info(f"Log level changed to {log_level_name}")
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.connected and self.vsphere_client:
            self.vsphere_client.disconnect()
        event.accept()


class ConnectionWorker(QThread):
    """Thread worker for vCenter connection"""
    finished = pyqtSignal(bool, object, str)
    
    def __init__(self, server, username, password, ignore_ssl):
        super().__init__()
        self.server = server
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        
    def run(self):
        """Run the connection process"""
        try:
            client = VSphereClient(
                self.server,
                self.username,
                self.password,
                self.ignore_ssl
            )
            client.connect()
            self.finished.emit(True, client, None)
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            self.finished.emit(False, None, str(e))


class ReportWorker(QThread):
    """Thread worker for report generation"""
    progress_update = pyqtSignal(str)
    progress_value = pyqtSignal(int)
    finished = pyqtSignal(bool, list, str)
    
    def __init__(self, vsphere_client, options, export_format, save_dir):
        super().__init__()
        self.vsphere_client = vsphere_client
        self.options = options
        self.export_format = export_format
        self.save_dir = save_dir
        
    def run(self):
        """Run the report generation process"""
        try:
            # Create data collector
            self.progress_update.emit("Collecting data from vCenter...")
            self.progress_value.emit(10)
            
            collector = DataCollector(self.vsphere_client)
            
            # Collect data based on selected options
            data = {}
            option_count = len(self.options)
            for i, option in enumerate(self.options):
                progress = int(10 + (i / option_count) * 40)
                self.progress_value.emit(progress)
                self.progress_update.emit(f"Collecting data: {option}...")
                
                if option == "vmware_tools":
                    data["vmware_tools"] = collector.collect_vmware_tools_info()
                elif option == "snapshots":
                    data["snapshots"] = collector.collect_snapshot_info()
                elif option == "orphaned_vmdks":
                    data["orphaned_vmdks"] = collector.collect_orphaned_vmdks()
                elif option == "vms":
                    data["vms"] = collector.collect_vm_info()
                elif option == "hosts":
                    data["hosts"] = collector.collect_host_info()
                elif option == "datastores":
                    data["datastores"] = collector.collect_datastore_info()
                elif option == "clusters":
                    data["clusters"] = collector.collect_cluster_info()
                elif option == "resource_pools":
                    data["resource_pools"] = collector.collect_resource_pool_info()
                elif option == "networks":
                    data["networks"] = collector.collect_network_info()
            
            # Generate reports
            self.progress_update.emit("Generating reports...")
            self.progress_value.emit(60)
            
            report_generator = ReportGenerator(data)
            
            output_files = []
            
            # Export based on selected format
            if self.export_format in ["HTML", "All Formats"]:
                self.progress_update.emit("Generating HTML report...")
                self.progress_value.emit(70)
                html_path = report_generator.export_to_html(self.save_dir)
                output_files.append(html_path)
                
            if self.export_format in ["DOCX", "All Formats"]:
                self.progress_update.emit("Generating DOCX report...")
                self.progress_value.emit(80)
                docx_path = report_generator.export_to_docx(self.save_dir)
                output_files.append(docx_path)
                
            if self.export_format in ["PDF", "All Formats"]:
                self.progress_update.emit("Generating PDF report...")
                self.progress_value.emit(90)
                pdf_path = report_generator.export_to_pdf(self.save_dir)
                output_files.append(pdf_path)
            
            self.progress_value.emit(100)
            self.finished.emit(True, output_files, None)
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            self.finished.emit(False, [], str(e))
