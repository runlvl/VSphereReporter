#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Copyright (c) 2025 Bechtle GmbH

VSphere-Client für die Verbindung mit vCenter Servern und die Ausführung von API-Aufrufen.
"""

import logging
import socket
import ssl
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Union, Tuple

# Versuche, die vSphere-API-Module zu importieren
try:
    import pyVim
    import pyVmomi
    from pyVim.connect import SmartConnect, Disconnect
    from pyVmomi import vim
except ImportError:
    logging.error("Die vSphere API (pyVmomi) ist nicht installiert. Die Anwendung wird im Demo-Modus ausgeführt.")

# Importiere Fehlerbehandlungsfunktionen
from webapp.utils.error_handler import handle_vsphere_error, ConnectionError, AuthenticationError, PermissionError, OperationError

logger = logging.getLogger(__name__)

class VSphereClient:
    """
    Client für die Verbindung zu vCenter Servern und die Ausführung von API-Aufrufen.
    
    Diese Klasse bietet eine einheitliche Schnittstelle für alle API-Aufrufe an einen
    vCenter Server und kapselt die pyVmomi-API ein.
    """
    
    def __init__(self, host: str, username: str, password: str, ignore_ssl: bool = False):
        """
        Initialisiere den vSphere-Client.
        
        Args:
            host (str): Hostname oder IP-Adresse des vCenter-Servers.
            username (str): Benutzername für die Authentifizierung.
            password (str): Passwort für die Authentifizierung.
            ignore_ssl (bool, optional): SSL-Zertifikat ignorieren. Standard ist False.
        """
        self.host = host
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.service_instance = None
        self.content = None
        
        # SSL-Kontext konfigurieren
        if ignore_ssl:
            self.ssl_context = ssl._create_unverified_context()
        else:
            self.ssl_context = ssl.create_default_context()
    
    @handle_vsphere_error
    def connect(self) -> None:
        """
        Verbindung zum vCenter-Server herstellen.
        
        Raises:
            ConnectionError: Wenn keine Verbindung hergestellt werden kann.
            AuthenticationError: Bei ungültigen Anmeldedaten.
            PermissionError: Bei fehlenden Berechtigungen.
            OperationError: Bei anderen Fehlern.
        """
        logger.info(f"Verbinde mit vCenter {self.host} als {self.username}")
        try:
            # Überprüfe, ob Port in der Host-Adresse enthalten ist
            parsed_url = urlparse(f"//{self.host}")
            port = parsed_url.port or 443  # Standardport 443, wenn nicht angegeben
            host = parsed_url.hostname or self.host
            
            # Verbindung herstellen
            self.service_instance = SmartConnect(
                host=host,
                user=self.username,
                pwd=self.password,
                port=port,
                sslContext=self.ssl_context
            )
            
            if not self.service_instance:
                raise ConnectionError(self.host, "Verbindung konnte nicht hergestellt werden")
            
            # Inhalte abrufen
            self.content = self.service_instance.RetrieveContent()
            logger.info(f"Verbindung zu {self.host} erfolgreich hergestellt")
        except vim.fault.InvalidLogin as e:
            logger.error(f"Ungültige Anmeldedaten für {self.username}@{self.host}: {str(e)}")
            raise AuthenticationError(self.host, self.username, str(e))
        except vim.fault.NoPermission as e:
            logger.error(f"Keine Berechtigung für {self.username}@{self.host}: {str(e)}")
            raise PermissionError("connect", str(e))
        except (socket.error, socket.timeout) as e:
            logger.error(f"Netzwerkfehler bei der Verbindung zu {self.host}: {str(e)}")
            raise ConnectionError(self.host, f"Netzwerkfehler: {str(e)}")
        except Exception as e:
            logger.exception(f"Unerwarteter Fehler bei der Verbindung zu {self.host}: {str(e)}")
            raise OperationError("connect", str(e))
    
    @handle_vsphere_error
    def disconnect(self) -> None:
        """
        Verbindung zum vCenter-Server trennen.
        """
        if self.service_instance:
            logger.info(f"Trenne Verbindung zu {self.host}")
            Disconnect(self.service_instance)
            self.service_instance = None
            self.content = None
    
    @handle_vsphere_error
    def get_vms(self) -> List[vim.VirtualMachine]:
        """
        Abrufen aller virtuellen Maschinen vom vCenter.
        
        Returns:
            List[vim.VirtualMachine]: Liste der virtuellen Maschinen.
            
        Raises:
            ConnectionError: Wenn keine Verbindung besteht.
            OperationError: Bei anderen Fehlern.
        """
        if not self.content:
            raise ConnectionError(self.host, "Nicht mit vCenter verbunden")
        
        logger.info("Rufe virtuelle Maschinen ab")
        try:
            container_view = self.content.viewManager.CreateContainerView(
                self.content.rootFolder, [vim.VirtualMachine], True
            )
            vms = container_view.view
            container_view.Destroy()
            logger.info(f"{len(vms)} virtuelle Maschinen gefunden")
            return vms
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen der VMs: {str(e)}")
            raise OperationError("get_vms", str(e))
    
    @handle_vsphere_error
    def get_hosts(self) -> List[vim.HostSystem]:
        """
        Abrufen aller ESXi-Hosts vom vCenter.
        
        Returns:
            List[vim.HostSystem]: Liste der ESXi-Hosts.
            
        Raises:
            ConnectionError: Wenn keine Verbindung besteht.
            OperationError: Bei anderen Fehlern.
        """
        if not self.content:
            raise ConnectionError(self.host, "Nicht mit vCenter verbunden")
        
        logger.info("Rufe ESXi-Hosts ab")
        try:
            container_view = self.content.viewManager.CreateContainerView(
                self.content.rootFolder, [vim.HostSystem], True
            )
            hosts = container_view.view
            container_view.Destroy()
            logger.info(f"{len(hosts)} ESXi-Hosts gefunden")
            return hosts
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen der Hosts: {str(e)}")
            raise OperationError("get_hosts", str(e))
    
    @handle_vsphere_error
    def get_datastores(self) -> List[vim.Datastore]:
        """
        Abrufen aller Datastores vom vCenter.
        
        Returns:
            List[vim.Datastore]: Liste der Datastores.
            
        Raises:
            ConnectionError: Wenn keine Verbindung besteht.
            OperationError: Bei anderen Fehlern.
        """
        if not self.content:
            raise ConnectionError(self.host, "Nicht mit vCenter verbunden")
        
        logger.info("Rufe Datastores ab")
        try:
            container_view = self.content.viewManager.CreateContainerView(
                self.content.rootFolder, [vim.Datastore], True
            )
            datastores = container_view.view
            container_view.Destroy()
            logger.info(f"{len(datastores)} Datastores gefunden")
            return datastores
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen der Datastores: {str(e)}")
            raise OperationError("get_datastores", str(e))
    
    @handle_vsphere_error
    def get_networks(self) -> List[vim.Network]:
        """
        Abrufen aller Netzwerke vom vCenter.
        
        Returns:
            List[vim.Network]: Liste der Netzwerke.
            
        Raises:
            ConnectionError: Wenn keine Verbindung besteht.
            OperationError: Bei anderen Fehlern.
        """
        if not self.content:
            raise ConnectionError(self.host, "Nicht mit vCenter verbunden")
        
        logger.info("Rufe Netzwerke ab")
        try:
            container_view = self.content.viewManager.CreateContainerView(
                self.content.rootFolder, [vim.Network], True
            )
            networks = container_view.view
            container_view.Destroy()
            logger.info(f"{len(networks)} Netzwerke gefunden")
            return networks
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen der Netzwerke: {str(e)}")
            raise OperationError("get_networks", str(e))
    
    @handle_vsphere_error
    def get_clusters(self) -> List[vim.ClusterComputeResource]:
        """
        Abrufen aller Cluster vom vCenter.
        
        Returns:
            List[vim.ClusterComputeResource]: Liste der Cluster.
            
        Raises:
            ConnectionError: Wenn keine Verbindung besteht.
            OperationError: Bei anderen Fehlern.
        """
        if not self.content:
            raise ConnectionError(self.host, "Nicht mit vCenter verbunden")
        
        logger.info("Rufe Cluster ab")
        try:
            container_view = self.content.viewManager.CreateContainerView(
                self.content.rootFolder, [vim.ClusterComputeResource], True
            )
            clusters = container_view.view
            container_view.Destroy()
            logger.info(f"{len(clusters)} Cluster gefunden")
            return clusters
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen der Cluster: {str(e)}")
            raise OperationError("get_clusters", str(e))
    
    @handle_vsphere_error
    def get_datacenters(self) -> List[vim.Datacenter]:
        """
        Abrufen aller Datacenter vom vCenter.
        
        Returns:
            List[vim.Datacenter]: Liste der Datacenter.
            
        Raises:
            ConnectionError: Wenn keine Verbindung besteht.
            OperationError: Bei anderen Fehlern.
        """
        if not self.content:
            raise ConnectionError(self.host, "Nicht mit vCenter verbunden")
        
        logger.info("Rufe Datacenter ab")
        try:
            container_view = self.content.viewManager.CreateContainerView(
                self.content.rootFolder, [vim.Datacenter], True
            )
            datacenters = container_view.view
            container_view.Destroy()
            logger.info(f"{len(datacenters)} Datacenter gefunden")
            return datacenters
        except Exception as e:
            logger.exception(f"Fehler beim Abrufen der Datacenter: {str(e)}")
            raise OperationError("get_datacenters", str(e))
    
    @handle_vsphere_error
    def wait_for_task(self, task: vim.Task) -> Any:
        """
        Warten auf den Abschluss einer vCenter-Aufgabe.
        
        Args:
            task (vim.Task): Die vCenter-Aufgabe.
            
        Returns:
            Any: Das Ergebnis der Aufgabe.
            
        Raises:
            OperationError: Bei Fehler während der Ausführung der Aufgabe.
        """
        logger.debug(f"Warte auf Abschluss der Aufgabe: {task.info.descriptionId}")
        
        task_done = False
        while not task_done:
            if task.info.state == vim.TaskInfo.State.success:
                logger.debug("Aufgabe erfolgreich abgeschlossen")
                return task.info.result
            
            if task.info.state == vim.TaskInfo.State.error:
                error_msg = task.info.error.msg
                logger.error(f"Aufgabe fehlgeschlagen: {error_msg}")
                raise OperationError("task", error_msg)
    
    def get_version(self) -> str:
        """
        Abrufen der vCenter-Version.
        
        Returns:
            str: Die vCenter-Version.
            
        Raises:
            ConnectionError: Wenn keine Verbindung besteht.
        """
        if not self.service_instance:
            raise ConnectionError(self.host, "Nicht mit vCenter verbunden")
        
        about = self.service_instance.content.about
        return f"{about.fullName} ({about.version})"