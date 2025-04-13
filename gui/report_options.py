#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report options widget for selecting what to include in the report
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QCheckBox,
    QGridLayout, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class ReportOptionsWidget(QScrollArea):
    """Widget for selecting report options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        
        # Create main widget
        self.options_widget = QWidget()
        self.setWidget(self.options_widget)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self.options_widget)
        
        # Create required options group
        required_group = QGroupBox("Required Report Options")
        required_layout = QVBoxLayout()
        
        # VMware Tools option (required)
        self.vmware_tools_check = QCheckBox("VMware Tools Versions (ordered by oldest first)")
        self.vmware_tools_check.setChecked(True)
        self.vmware_tools_check.setEnabled(False)  # Always checked
        required_layout.addWidget(self.vmware_tools_check)
        
        # Snapshot age option (required)
        self.snapshots_check = QCheckBox("Snapshot Age (ordered by oldest first)")
        self.snapshots_check.setChecked(True)
        self.snapshots_check.setEnabled(False)  # Always checked
        required_layout.addWidget(self.snapshots_check)
        
        # Orphaned VMDKs option (required)
        self.orphaned_vmdks_check = QCheckBox("Orphaned VMDK Files (with explanation)")
        self.orphaned_vmdks_check.setChecked(True)
        self.orphaned_vmdks_check.setEnabled(False)  # Always checked
        required_layout.addWidget(self.orphaned_vmdks_check)
        
        required_group.setLayout(required_layout)
        layout.addWidget(required_group)
        
        # Create additional options group
        additional_group = QGroupBox("Additional Report Options")
        additional_layout = QGridLayout()
        
        # VM options
        self.vms_check = QCheckBox("Virtual Machines")
        self.vms_check.setToolTip("Include detailed information about all virtual machines")
        additional_layout.addWidget(self.vms_check, 0, 0)
        
        # Hosts options
        self.hosts_check = QCheckBox("ESXi Hosts")
        self.hosts_check.setToolTip("Include detailed information about all ESXi hosts")
        additional_layout.addWidget(self.hosts_check, 0, 1)
        
        # Datastore options
        self.datastores_check = QCheckBox("Datastores")
        self.datastores_check.setToolTip("Include detailed information about all datastores")
        additional_layout.addWidget(self.datastores_check, 1, 0)
        
        # Cluster options
        self.clusters_check = QCheckBox("Clusters")
        self.clusters_check.setToolTip("Include detailed information about all clusters")
        additional_layout.addWidget(self.clusters_check, 1, 1)
        
        # Resource Pool options
        self.resource_pools_check = QCheckBox("Resource Pools")
        self.resource_pools_check.setToolTip("Include detailed information about all resource pools")
        additional_layout.addWidget(self.resource_pools_check, 2, 0)
        
        # Network options
        self.networks_check = QCheckBox("Networks")
        self.networks_check.setToolTip("Include detailed information about all networks")
        additional_layout.addWidget(self.networks_check, 2, 1)
        
        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)
        
        # Add spacer to the bottom
        layout.addStretch(1)
        
    def get_selected_options(self):
        """Get the list of selected report options"""
        options = []
        
        # Always include required options
        options.append("vmware_tools")
        options.append("snapshots")
        options.append("orphaned_vmdks")
        
        # Add additional selected options
        if self.vms_check.isChecked():
            options.append("vms")
        
        if self.hosts_check.isChecked():
            options.append("hosts")
        
        if self.datastores_check.isChecked():
            options.append("datastores")
        
        if self.clusters_check.isChecked():
            options.append("clusters")
        
        if self.resource_pools_check.isChecked():
            options.append("resource_pools")
        
        if self.networks_check.isChecked():
            options.append("networks")
        
        return options
