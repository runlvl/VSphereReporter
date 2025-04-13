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
    QSplitter, QTextEdit, QStatusBar
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from gui.connection_dialog import ConnectionDialog
from gui.report_options import ReportOptionsWidget
from gui.progress_dialog import ProgressDialog
from core.vsphere_client import VSphereClient
from core.report_generator import ReportGenerator
from core.data_collector import DataCollector
from utils.helper import get_save_directory

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.vsphere_client = None
        self.connected = False
        self.report_options = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("VMware vSphere Reporter")
        self.setMinimumSize(900, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create top status area
        status_layout = QHBoxLayout()
        self.connection_status = QLabel("Not connected to vCenter")
        self.connection_status.setStyleSheet("color: red;")
        self.connect_button = QPushButton("Connect to vCenter")
        self.connect_button.clicked.connect(self.show_connection_dialog)
        
        status_layout.addWidget(self.connection_status)
        status_layout.addStretch(1)
        status_layout.addWidget(self.connect_button)
        
        main_layout.addLayout(status_layout)
        
        # Create report options widget
        self.report_options_widget = ReportOptionsWidget()
        self.report_options_widget.setEnabled(False)
        main_layout.addWidget(self.report_options_widget)
        
        # Create export options
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
        main_layout.addWidget(export_group)
        
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
            self.connection_status.setStyleSheet("color: green;")
            self.connect_button.setText("Reconnect")
            self.report_options_widget.setEnabled(True)
            self.export_button.setEnabled(True)
            self.statusBar.showMessage("Connected to vCenter successfully", 3000)
        else:
            QMessageBox.critical(self, "Connection Error", 
                                f"Failed to connect to vCenter:\n{error_message}")
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
        QMessageBox.about(
            self, 
            "About VMware vSphere Reporter",
            "VMware vSphere Reporter 1.0.0\n\n"
            "A comprehensive reporting tool for VMware vSphere environments.\n\n"
            "This tool allows you to generate detailed reports about your "
            "vSphere environment including VMware Tools versions, "
            "snapshot status, orphaned VMDKs, and more."
        )
    
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
