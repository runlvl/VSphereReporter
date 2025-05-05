#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
vSphere Client für die Verbindung zum vCenter
"""

import logging
import ssl
import socket
import re
from urllib.error import URLError
from datetime import datetime
import time

from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim
from pyVim.connect import Disconnect, SmartConnect
from pyVmomi import vim

logger = logging.getLogger('vsphere_reporter')

class VSphereClient:
    """Klasse für die Verbindung und Interaktion mit vSphere/vCenter"""
    
    def __init__(self, host, username, password, ignore_ssl=False):
        """
        Initialisiert den vSphere-Client
        
        Args:
            host: vCenter-Hostname oder IP-Adresse
            username: Benutzername für die Authentifizierung
            password: Passwort für die Authentifizierung
            ignore_ssl: Wenn True, werden SSL-Zertifikatsfehler ignoriert
        """
        self.host = host
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.si = None
        self.content = None
        self.is_connected = False
        self.connection_time = None
    
    def connect(self):
        """
        Stellt eine Verbindung zum vCenter her
        
        Raises:
            ConnectionError: Bei Verbindungsproblemen
            AuthenticationError: Bei Authentifizierungsproblemen
            Exception: Bei anderen Fehlern
        """
        logger.info(f"Verbindung zum vCenter {self.host} wird hergestellt...")
        
        try:
            # SSL-Kontext konfigurieren
            if self.ignore_ssl:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                ssl_context.verify_mode = ssl.CERT_NONE
                ssl_context.check_hostname = False
            else:
                ssl_context = ssl.create_default_context()
            
            # Verbindung herstellen
            self.si = SmartConnect(
                host=self.host,
                user=self.username,
                pwd=self.password,
                sslContext=ssl_context
            )
            
            if not self.si:
                raise ConnectionError("Verbindung zum vCenter konnte nicht hergestellt werden")
            
            self.content = self.si.RetrieveContent()
            self.is_connected = True
            self.connection_time = datetime.now()
            
            # vCenter-Version protokollieren
            about = self.content.about
            logger.info(f"Erfolgreich verbunden mit {about.fullName} (API Version: {about.apiVersion})")
            
            return True
            
        except vim.fault.InvalidLogin:
            logger.error(f"Ungültige Anmeldedaten für {self.username}@{self.host}")
            raise
        except (socket.error, socket.timeout, socket.gaierror) as e:
            logger.error(f"Netzwerkfehler beim Verbinden mit {self.host}: {str(e)}")
            raise
        except ssl.SSLError as e:
            logger.error(f"SSL-Fehler beim Verbinden mit {self.host}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Fehler beim Verbinden mit {self.host}: {str(e)}")
            raise
    
    def disconnect(self):
        """Trennt die Verbindung zum vCenter"""
        if self.si:
            try:
                Disconnect(self.si)
                logger.info(f"Verbindung zum vCenter {self.host} getrennt")
            except Exception as e:
                logger.error(f"Fehler beim Trennen der Verbindung: {str(e)}")
            finally:
                self.si = None
                self.content = None
                self.is_connected = False
                self.connection_time = None
    
    def wait_for_task(self, task):
        """
        Wartet auf den Abschluss einer vSphere-Aufgabe
        
        Args:
            task: Die vSphere-Aufgabe
            
        Returns:
            Das Ergebnis der Aufgabe
            
        Raises:
            Exception: Bei Fehlern während der Aufgabenausführung
        """
        task_info = task.info
        while task_info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
            task_info = task.info
        
        if task_info.state == vim.TaskInfo.State.error:
            error = task_info.error
            raise Exception(f"Fehler bei Aufgabe: {error.localizedMessage}")
        
        return task_info.result
    
    def get_all_vms(self):
        """
        Holt alle virtuellen Maschinen im Inventar
        
        Returns:
            list: Liste aller VMs
        """
        logger.debug("Hole alle virtuellen Maschinen...")
        
        try:
            vm_view = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder, 
                type=[vim.VirtualMachine], 
                recursive=True
            )
            vms = vm_view.view
            vm_view.Destroy()
            
            logger.debug(f"{len(vms)} virtuelle Maschinen gefunden")
            return vms
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der virtuellen Maschinen: {str(e)}")
            raise
    
    def get_all_hosts(self):
        """
        Holt alle ESXi-Hosts im Inventar
        
        Returns:
            list: Liste aller Hosts
        """
        logger.debug("Hole alle ESXi-Hosts...")
        
        try:
            host_view = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.HostSystem],
                recursive=True
            )
            hosts = host_view.view
            host_view.Destroy()
            
            logger.debug(f"{len(hosts)} ESXi-Hosts gefunden")
            return hosts
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der ESXi-Hosts: {str(e)}")
            raise
    
    def get_all_datastores(self):
        """
        Holt alle Datastores im Inventar
        
        Returns:
            list: Liste aller Datastores
        """
        logger.debug("Hole alle Datastores...")
        
        try:
            datastore_view = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.Datastore],
                recursive=True
            )
            datastores = datastore_view.view
            datastore_view.Destroy()
            
            logger.debug(f"{len(datastores)} Datastores gefunden")
            return datastores
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Datastores: {str(e)}")
            raise
    
    def get_all_networks(self):
        """
        Holt alle Netzwerke im Inventar
        
        Returns:
            list: Liste aller Netzwerke
        """
        logger.debug("Hole alle Netzwerke...")
        
        try:
            network_view = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.Network, vim.DistributedVirtualPortgroup],
                recursive=True
            )
            networks = network_view.view
            network_view.Destroy()
            
            logger.debug(f"{len(networks)} Netzwerke gefunden")
            return networks
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Netzwerke: {str(e)}")
            raise
    
    def get_all_clusters(self):
        """
        Holt alle Cluster im Inventar
        
        Returns:
            list: Liste aller Cluster
        """
        logger.debug("Hole alle Cluster...")
        
        try:
            cluster_view = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.ClusterComputeResource],
                recursive=True
            )
            clusters = cluster_view.view
            cluster_view.Destroy()
            
            logger.debug(f"{len(clusters)} Cluster gefunden")
            return clusters
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Cluster: {str(e)}")
            raise
    
    def get_all_resource_pools(self):
        """
        Holt alle Resource Pools im Inventar
        
        Returns:
            list: Liste aller Resource Pools
        """
        logger.debug("Hole alle Resource Pools...")
        
        try:
            rp_view = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.ResourcePool],
                recursive=True
            )
            resource_pools = rp_view.view
            rp_view.Destroy()
            
            # Entferne die Standard-Resource-Pools, die automatisch für jeden Cluster und Host erstellt werden
            filtered_pools = []
            for pool in resource_pools:
                # Prüfe, ob es sich um einen Standard-Pool handelt
                is_default_pool = False
                if pool.parent:
                    if isinstance(pool.parent, vim.ClusterComputeResource) and pool.name == "Resources":
                        is_default_pool = True
                    elif isinstance(pool.parent, vim.ComputeResource) and pool.name == "Resources":
                        is_default_pool = True
                
                if not is_default_pool:
                    filtered_pools.append(pool)
            
            logger.debug(f"{len(filtered_pools)} Resource Pools gefunden (ohne Standard-Pools)")
            return filtered_pools
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Resource Pools: {str(e)}")
            raise