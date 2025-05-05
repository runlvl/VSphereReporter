#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - vSphere Client
Copyright (c) 2025 Bechtle GmbH

Modul für die Verbindung zu vCenter-Servern und Zugriff auf vSphere-Daten
"""

import logging
import os
import ssl

# Im Demo-Modus benötigen wir keine VMware-Abhängigkeiten
try:
    from pyVim import connect
    from pyVmomi import vim
except ImportError:
    # Demo-Modus
    connect = None
    vim = None

from webapp.utils.error_handler import handle_vsphere_error, ConnectionError, AuthenticationError

class VSphereClient:
    """Client für die Verbindung zu vCenter-Servern und Zugriff auf vSphere-Daten"""
    
    def __init__(self, host, user, password, ignore_ssl=False):
        """
        Initialisiere den vSphere-Client
        
        Args:
            host: Hostname oder IP-Adresse des vCenter-Servers
            user: Benutzername für die Anmeldung
            password: Passwort für die Anmeldung
            ignore_ssl: SSL-Zertifikat ignorieren (True/False)
        """
        self.host = host
        self.user = user
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.service_instance = None
        self.content = None
        self.is_connected = False
        
        # Prüfe, ob wir im Demo-Modus sind
        self.demo_mode = os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() == 'true'
        if self.demo_mode:
            logging.info("Demo-Modus aktiviert - keine tatsächliche Verbindung wird hergestellt")
    
    @handle_vsphere_error
    def connect(self):
        """
        Stelle eine Verbindung zum vCenter-Server her
        
        Returns:
            Das Content-Objekt des vCenter-Servers
            
        Raises:
            ConnectionError: Bei Verbindungsproblemen
            AuthenticationError: Bei Authentifizierungsproblemen
        """
        # Im Demo-Modus simulieren wir eine erfolgreiche Verbindung
        if self.demo_mode:
            logging.info(f"Demo-Modus: Simuliere Verbindung zu {self.host}")
            self.is_connected = True
            return {}
        
        # Überprüfe, ob die VMware-Module verfügbar sind
        if connect is None or vim is None:
            raise ImportError("PyVmomi ist nicht installiert. Bitte installieren Sie PyVmomi oder verwenden "
                             "Sie den Demo-Modus durch Setzen der Umgebungsvariable VSPHERE_REPORTER_DEMO=true")
        
        # Konfiguriere SSL-Kontext
        ssl_context = None
        if self.ignore_ssl:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Stelle Verbindung her
        logging.info(f"Verbinde mit vCenter: {self.host}")
        try:
            self.service_instance = connect.SmartConnect(
                host=self.host,
                user=self.user,
                pwd=self.password,
                sslContext=ssl_context
            )
            
            if not self.service_instance:
                raise ConnectionError(f"Konnte keine Verbindung zu {self.host} herstellen")
            
            # Lade Content-Objekt
            self.content = self.service_instance.RetrieveContent()
            self.is_connected = True
            
            logging.info(f"Verbindung zu {self.host} erfolgreich hergestellt")
            return self.content
            
        except Exception as e:
            self.is_connected = False
            self.service_instance = None
            self.content = None
            raise
    
    def disconnect(self):
        """Trennt die Verbindung zum vCenter-Server"""
        if self.demo_mode:
            logging.info("Demo-Modus: Simuliere Trennung der Verbindung")
            self.is_connected = False
            return
        
        if self.service_instance and self.is_connected:
            connect.Disconnect(self.service_instance)
            self.is_connected = False
            self.service_instance = None
            self.content = None
            logging.info(f"Verbindung zu {self.host} getrennt")
    
    def get_all_vms(self):
        """
        Holt alle virtuellen Maschinen aus dem vCenter
        
        Returns:
            Liste von vim.VirtualMachine-Objekten
        """
        if self.demo_mode:
            logging.info("Demo-Modus: Simuliere Abruf von VMs")
            return []
        
        if not self.is_connected or not self.content:
            raise ConnectionError("Keine Verbindung zum vCenter")
        
        container = self.content.viewManager.CreateContainerView(
            container=self.content.rootFolder,
            type=[vim.VirtualMachine],
            recursive=True
        )
        
        vms = container.view
        container.Destroy()
        
        return vms
    
    def get_all_hosts(self):
        """
        Holt alle ESXi-Hosts aus dem vCenter
        
        Returns:
            Liste von vim.HostSystem-Objekten
        """
        if self.demo_mode:
            logging.info("Demo-Modus: Simuliere Abruf von Hosts")
            return []
        
        if not self.is_connected or not self.content:
            raise ConnectionError("Keine Verbindung zum vCenter")
        
        container = self.content.viewManager.CreateContainerView(
            container=self.content.rootFolder,
            type=[vim.HostSystem],
            recursive=True
        )
        
        hosts = container.view
        container.Destroy()
        
        return hosts
    
    def get_all_datastores(self):
        """
        Holt alle Datastores aus dem vCenter
        
        Returns:
            Liste von vim.Datastore-Objekten
        """
        if self.demo_mode:
            logging.info("Demo-Modus: Simuliere Abruf von Datastores")
            return []
        
        if not self.is_connected or not self.content:
            raise ConnectionError("Keine Verbindung zum vCenter")
        
        container = self.content.viewManager.CreateContainerView(
            container=self.content.rootFolder,
            type=[vim.Datastore],
            recursive=True
        )
        
        datastores = container.view
        container.Destroy()
        
        return datastores
    
    def get_all_networks(self):
        """
        Holt alle Netzwerke aus dem vCenter
        
        Returns:
            Liste von vim.Network-Objekten
        """
        if self.demo_mode:
            logging.info("Demo-Modus: Simuliere Abruf von Netzwerken")
            return []
        
        if not self.is_connected or not self.content:
            raise ConnectionError("Keine Verbindung zum vCenter")
        
        container = self.content.viewManager.CreateContainerView(
            container=self.content.rootFolder,
            type=[vim.Network],
            recursive=True
        )
        
        networks = container.view
        container.Destroy()
        
        return networks
    
    def get_all_clusters(self):
        """
        Holt alle Cluster aus dem vCenter
        
        Returns:
            Liste von vim.ClusterComputeResource-Objekten
        """
        if self.demo_mode:
            logging.info("Demo-Modus: Simuliere Abruf von Clustern")
            return []
        
        if not self.is_connected or not self.content:
            raise ConnectionError("Keine Verbindung zum vCenter")
        
        container = self.content.viewManager.CreateContainerView(
            container=self.content.rootFolder,
            type=[vim.ClusterComputeResource],
            recursive=True
        )
        
        clusters = container.view
        container.Destroy()
        
        return clusters
    
    def get_all_datacenters(self):
        """
        Holt alle Datacenter aus dem vCenter
        
        Returns:
            Liste von vim.Datacenter-Objekten
        """
        if self.demo_mode:
            logging.info("Demo-Modus: Simuliere Abruf von Datacentern")
            return []
        
        if not self.is_connected or not self.content:
            raise ConnectionError("Keine Verbindung zum vCenter")
        
        container = self.content.viewManager.CreateContainerView(
            container=self.content.rootFolder,
            type=[vim.Datacenter],
            recursive=True
        )
        
        datacenters = container.view
        container.Destroy()
        
        return datacenters