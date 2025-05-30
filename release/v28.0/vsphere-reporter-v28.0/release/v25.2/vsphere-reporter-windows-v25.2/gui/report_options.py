#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Report Options Panel
Panel zur Auswahl der Report-Optionen
"""

import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QGroupBox, 
                            QCheckBox, QLabel, QSpacerItem, QSizePolicy,
                            QHBoxLayout, QScrollArea, QFrame)
from PyQt5.QtCore import Qt

# Bechtle-Farbschema
BECHTLE_DARK_BLUE = "#00355e"
BECHTLE_ORANGE = "#da6f1e"
BECHTLE_GREEN = "#23a96a"
BECHTLE_LIGHT_GRAY = "#f3f3f3"
BECHTLE_DARK_GRAY = "#5a5a5a"

class ReportOptionsPanel(QWidget):
    """Panel zur Auswahl der Report-Optionen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialisiere die Benutzeroberfläche"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ScrollArea für alle Inhalte, damit sie bei kleinen Fenstern scrollbar sind
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Container für alle Optionen
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Format-Auswahl
        format_group = QGroupBox("Ausgabeformate")
        format_layout = QHBoxLayout()
        
        self.format_html = QCheckBox("HTML")
        self.format_html.setChecked(True)
        format_layout.addWidget(self.format_html)
        
        self.format_docx = QCheckBox("DOCX")
        format_layout.addWidget(self.format_docx)
        
        self.format_pdf = QCheckBox("PDF")
        format_layout.addWidget(self.format_pdf)
        
        format_layout.addStretch(1)
        
        format_group.setLayout(format_layout)
        scroll_layout.addWidget(format_group)
        
        # Pflichtbestandteile
        mandatory_group = QGroupBox("Pflichtbestandteile")
        mandatory_layout = QGridLayout()
        mandatory_layout.setColumnStretch(1, 1)  # Beschreibungsspalte soll sich ausdehnen
        
        # VMware Tools Versionen
        tools_checkbox = QCheckBox("VMware Tools Versionen")
        tools_checkbox.setChecked(True)
        tools_checkbox.setEnabled(False)  # Kann nicht deaktiviert werden
        mandatory_layout.addWidget(tools_checkbox, 0, 0)
        
        tools_description = QLabel("Zeigt VMware Tools Versionen, sortiert nach ältesten zuerst")
        tools_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        tools_description.setWordWrap(True)  # Ermöglicht Textumbruch
        mandatory_layout.addWidget(tools_description, 0, 1)
        
        # Snapshot-Alter
        snapshot_checkbox = QCheckBox("Snapshot-Alter")
        snapshot_checkbox.setChecked(True)
        snapshot_checkbox.setEnabled(False)  # Kann nicht deaktiviert werden
        mandatory_layout.addWidget(snapshot_checkbox, 1, 0)
        
        snapshot_description = QLabel("Zeigt VM-Snapshots, sortiert nach ältesten zuerst")
        snapshot_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        snapshot_description.setWordWrap(True)  # Ermöglicht Textumbruch
        mandatory_layout.addWidget(snapshot_description, 1, 1)
        
        # Verwaiste VMDKs
        orphaned_checkbox = QCheckBox("Verwaiste VMDK-Dateien")
        orphaned_checkbox.setChecked(True)
        orphaned_checkbox.setEnabled(False)  # Kann nicht deaktiviert werden
        mandatory_layout.addWidget(orphaned_checkbox, 2, 0)
        
        orphaned_description = QLabel("Zeigt VMDK-Dateien, die keiner VM zugeordnet sind")
        orphaned_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        orphaned_description.setWordWrap(True)  # Ermöglicht Textumbruch
        mandatory_layout.addWidget(orphaned_description, 2, 1)
        
        mandatory_group.setLayout(mandatory_layout)
        scroll_layout.addWidget(mandatory_group)
        
        # Optionale Bestandteile
        optional_group = QGroupBox("Optionale Bestandteile")
        optional_layout = QGridLayout()
        optional_layout.setColumnStretch(1, 1)  # Beschreibungsspalte soll sich ausdehnen
        
        # VMs
        self.vms_checkbox = QCheckBox("Virtuelle Maschinen")
        self.vms_checkbox.setChecked(True)
        optional_layout.addWidget(self.vms_checkbox, 0, 0)
        
        vms_description = QLabel("Liste aller virtuellen Maschinen mit Details")
        vms_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        vms_description.setWordWrap(True)  # Ermöglicht Textumbruch
        optional_layout.addWidget(vms_description, 0, 1)
        
        # Hosts
        self.hosts_checkbox = QCheckBox("ESXi-Hosts")
        self.hosts_checkbox.setChecked(True)
        optional_layout.addWidget(self.hosts_checkbox, 1, 0)
        
        hosts_description = QLabel("Liste aller ESXi-Hosts mit Hardware-Details")
        hosts_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        hosts_description.setWordWrap(True)  # Ermöglicht Textumbruch
        optional_layout.addWidget(hosts_description, 1, 1)
        
        # Datastores
        self.datastores_checkbox = QCheckBox("Datastores")
        self.datastores_checkbox.setChecked(True)
        optional_layout.addWidget(self.datastores_checkbox, 2, 0)
        
        datastores_description = QLabel("Liste aller Datastores mit Kapazitäts- und Performance-Details")
        datastores_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        datastores_description.setWordWrap(True)  # Ermöglicht Textumbruch
        optional_layout.addWidget(datastores_description, 2, 1)
        
        # Cluster
        self.clusters_checkbox = QCheckBox("Cluster")
        self.clusters_checkbox.setChecked(True)
        optional_layout.addWidget(self.clusters_checkbox, 3, 0)
        
        clusters_description = QLabel("Liste aller Cluster mit HA- und DRS-Konfigurationen")
        clusters_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        clusters_description.setWordWrap(True)  # Ermöglicht Textumbruch
        optional_layout.addWidget(clusters_description, 3, 1)
        
        # Resource Pools
        self.resource_pools_checkbox = QCheckBox("Resource Pools")
        self.resource_pools_checkbox.setChecked(True)
        optional_layout.addWidget(self.resource_pools_checkbox, 4, 0)
        
        resource_pools_description = QLabel("Liste aller Resource Pools mit Ressourcen-Zuteilungen")
        resource_pools_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        resource_pools_description.setWordWrap(True)  # Ermöglicht Textumbruch
        optional_layout.addWidget(resource_pools_description, 4, 1)
        
        # Netzwerke
        self.networks_checkbox = QCheckBox("Netzwerke")
        self.networks_checkbox.setChecked(True)
        optional_layout.addWidget(self.networks_checkbox, 5, 0)
        
        networks_description = QLabel("Liste aller Netzwerke (vSwitches, Port Groups, DVS)")
        networks_description.setStyleSheet(f"color: {BECHTLE_DARK_GRAY};")
        networks_description.setWordWrap(True)  # Ermöglicht Textumbruch
        optional_layout.addWidget(networks_description, 5, 1)
        
        optional_group.setLayout(optional_layout)
        scroll_layout.addWidget(optional_group)
        
        # Abstandhalter am Ende, der sich nach oben ausdehnt (wichtig für dynamische Größe)
        scroll_layout.addStretch(1)
        
        # Scroll-Content setzen
        scroll_area.setWidget(scroll_content)
        
        # Scroll-Bereich zum Hauptlayout hinzufügen
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)
        
        # Setzt die Größenrichtlinie, damit der Bereich minimierbar ist, aber auch skalieren kann
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(100)  # Minimale Höhe, damit immer etwas sichtbar ist
        
    def select_all(self):
        """Wähle alle optionalen Bestandteile aus"""
        self.vms_checkbox.setChecked(True)
        self.hosts_checkbox.setChecked(True)
        self.datastores_checkbox.setChecked(True)
        self.clusters_checkbox.setChecked(True)
        self.resource_pools_checkbox.setChecked(True)
        self.networks_checkbox.setChecked(True)
        
        self.format_html.setChecked(True)
        self.format_docx.setChecked(True)
        self.format_pdf.setChecked(True)
        
        self.logger.info("Alle Report-Optionen ausgewählt")
        
    def deselect_all(self):
        """Deselektiere alle optionalen Bestandteile"""
        self.vms_checkbox.setChecked(False)
        self.hosts_checkbox.setChecked(False)
        self.datastores_checkbox.setChecked(False)
        self.clusters_checkbox.setChecked(False)
        self.resource_pools_checkbox.setChecked(False)
        self.networks_checkbox.setChecked(False)
        
        self.format_html.setChecked(True)  # HTML ist Pflichtformat
        self.format_docx.setChecked(False)
        self.format_pdf.setChecked(False)
        
        self.logger.info("Alle optionalen Report-Optionen abgewählt")
        
    def get_selected_options(self):
        """Gibt die ausgewählten Optionen zurück
        
        Returns:
            dict: Dictionary mit den ausgewählten Optionen
        """
        formats = []
        if self.format_html.isChecked():
            formats.append("html")
        if self.format_docx.isChecked():
            formats.append("docx")
        if self.format_pdf.isChecked():
            formats.append("pdf")
            
        sections = {
            "vms": self.vms_checkbox.isChecked(),
            "hosts": self.hosts_checkbox.isChecked(),
            "datastores": self.datastores_checkbox.isChecked(),
            "clusters": self.clusters_checkbox.isChecked(),
            "resource_pools": self.resource_pools_checkbox.isChecked(),
            "networks": self.networks_checkbox.isChecked()
        }
        
        return {
            "formats": formats,
            "sections": sections
        }