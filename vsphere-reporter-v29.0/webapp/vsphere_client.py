#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
vSphere Client für die Verbindung zum vCenter
"""

import time
import logging
import ssl

import pyVim.connect
import pyVmomi
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from webapp.utils.error_handler import handle_vsphere_error, ConnectionError, AuthenticationError

logger = logging.getLogger('vsphere_reporter')

class VSphereClient:
    """Hauptklasse für die Interaktion mit vSphere API"""
    
    def __init__(self, host, username, password, ignore_ssl=False, port=443):
        """
        Initialisiert eine neue Instanz des vSphere Clients
        
        Args:
            host (str): Hostname oder IP-Adresse des vCenter-Servers
            username (str): Benutzername für die Authentifizierung
            password (str): Passwort für die Authentifizierung
            ignore_ssl (bool): SSL-Zertifikatsprüfung ignorieren, wenn True
            port (int): Port für die Verbindung, standardmäßig 443
        """
        self.host = host
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.port = port
        self.service_instance = None
        self.content = None
        self.is_connected = False

    @handle_vsphere_error
    def connect(self):
        """
        Stellt eine Verbindung zum vCenter-Server her
        
        Raises:
            ConnectionError: Wenn die Verbindung fehlschlägt
            AuthenticationError: Wenn die Authentifizierung fehlschlägt
        """
        if self.is_connected:
            logger.info(f"Bereits verbunden mit {self.host}")
            return
            
        logger.info(f"Verbinde mit vCenter {self.host}...")
        
        ssl_context = None
        if self.ignore_ssl:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.verify_mode = ssl.CERT_NONE
        
        try:
            self.service_instance = SmartConnect(
                host=self.host,
                user=self.username,
                pwd=self.password,
                port=self.port,
                sslContext=ssl_context
            )
            
            if not self.service_instance:
                raise ConnectionError(f"Konnte keine Verbindung zu {self.host} herstellen")
            
            self.content = self.service_instance.RetrieveContent()
            self.is_connected = True
            logger.info(f"Erfolgreich verbunden mit vCenter {self.host}")
            
            # API-Version und Serverinformationen protokollieren
            about = self.content.about
            logger.info(f"vCenter Version: {about.version} ({about.build})")
            logger.info(f"vCenter Name: {about.name}")
            logger.info(f"vCenter Instanz-UUID: {about.instanceUuid}")
            logger.info(f"API-Typ: {about.apiType}")
            
        except Exception as e:
            logger.error(f"Fehler beim Verbinden mit {self.host}: {str(e)}")
            self.is_connected = False
            raise
    
    @handle_vsphere_error
    def disconnect(self):
        """Trennt die Verbindung zum vCenter-Server"""
        if self.service_instance and self.is_connected:
            Disconnect(self.service_instance)
            self.service_instance = None
            self.content = None
            self.is_connected = False
            logger.info(f"Verbindung zu {self.host} getrennt")
    
    def get_all_vms(self):
        """
        Holt alle virtuellen Maschinen aus dem vCenter
        
        Returns:
            list: Liste aller VM-Objekte
        """
        if not self.is_connected:
            raise ConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        vms = container.view
        container.Destroy()
        
        logger.info(f"{len(vms)} VMs gefunden")
        return vms
    
    def get_all_hosts(self):
        """
        Holt alle ESXi-Hosts aus dem vCenter
        
        Returns:
            list: Liste aller Host-Objekte
        """
        if not self.is_connected:
            raise ConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.HostSystem], True
        )
        hosts = container.view
        container.Destroy()
        
        logger.info(f"{len(hosts)} ESXi-Hosts gefunden")
        return hosts
    
    def get_all_datastores(self):
        """
        Holt alle Datastores aus dem vCenter
        
        Returns:
            list: Liste aller Datastore-Objekte
        """
        if not self.is_connected:
            raise ConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Datastore], True
        )
        datastores = container.view
        container.Destroy()
        
        logger.info(f"{len(datastores)} Datastores gefunden")
        return datastores
    
    def get_all_clusters(self):
        """
        Holt alle Cluster aus dem vCenter
        
        Returns:
            list: Liste aller Cluster-Objekte
        """
        if not self.is_connected:
            raise ConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.ClusterComputeResource], True
        )
        clusters = container.view
        container.Destroy()
        
        logger.info(f"{len(clusters)} Cluster gefunden")
        return clusters
    
    def get_all_networks(self):
        """
        Holt alle Netzwerke aus dem vCenter
        
        Returns:
            list: Liste aller Netzwerk-Objekte
        """
        if not self.is_connected:
            raise ConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Network], True
        )
        networks = container.view
        container.Destroy()
        
        logger.info(f"{len(networks)} Netzwerke gefunden")
        return networks
    
    def get_all_distributed_switches(self):
        """
        Holt alle verteilten Switches aus dem vCenter
        
        Returns:
            list: Liste aller Distributed Switch-Objekte
        """
        if not self.is_connected:
            raise ConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.DistributedVirtualSwitch], True
        )
        switches = container.view
        container.Destroy()
        
        logger.info(f"{len(switches)} Distributed Switches gefunden")
        return switches
    
    def get_all_resource_pools(self):
        """
        Holt alle Resource Pools aus dem vCenter
        
        Returns:
            list: Liste aller Resource Pool-Objekte
        """
        if not self.is_connected:
            raise ConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.ResourcePool], True
        )
        pools = container.view
        container.Destroy()
        
        logger.info(f"{len(pools)} Resource Pools gefunden")
        return pools
    
    def wait_for_task(self, task, timeout=300):
        """
        Wartet auf den Abschluss einer vCenter-Aufgabe
        
        Args:
            task: Die zu überwachende vCenter-Aufgabe
            timeout: Zeitlimit in Sekunden (Standardwert: 300)
            
        Returns:
            Das Ergebnis der Aufgabe
            
        Raises:
            Exception: Wenn die Aufgabe fehlschlägt oder das Zeitlimit überschritten wird
        """
        start_time = time.time()
        
        while True:
            if task.info.state == vim.TaskInfo.State.success:
                logger.debug(f"Aufgabe erfolgreich abgeschlossen: {task.info.descriptionId}")
                return task.info.result
                
            if task.info.state == vim.TaskInfo.State.error:
                logger.error(f"Aufgabe fehlgeschlagen: {task.info.error.msg}")
                raise task.info.error
                
            if time.time() - start_time > timeout:
                logger.error(f"Zeitüberschreitung bei Aufgabe {task.info.descriptionId}")
                raise TimeoutError(f"Zeitlimit von {timeout} Sekunden für Aufgabe überschritten")
                
            # Kurze Pause, um CPU-Nutzung zu reduzieren
            time.sleep(0.5)