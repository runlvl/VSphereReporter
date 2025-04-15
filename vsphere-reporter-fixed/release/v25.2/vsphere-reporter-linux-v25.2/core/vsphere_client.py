#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere API client using pyVmomi
"""

import ssl
import atexit
import logging
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

logger = logging.getLogger(__name__)

class VSphereClient:
    """Client for connecting to vSphere environment"""
    
    def __init__(self, server, username, password, ignore_ssl=False):
        """
        Initialize the vSphere client
        
        Args:
            server (str): vCenter server address
            username (str): vCenter username
            password (str): vCenter password
            ignore_ssl (bool): Whether to ignore SSL certificate verification
        """
        self.server = server
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.service_instance = None
        self.content = None
        
    def connect(self):
        """
        Connect to the vCenter server
        
        Raises:
            Exception: If connection fails
        """
        try:
            if self.ignore_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                context.verify_mode = ssl.CERT_NONE
            else:
                context = None
                
            self.service_instance = SmartConnect(
                host=self.server,
                user=self.username,
                pwd=self.password,
                sslContext=context
            )
            
            # Register disconnect function to run at exit
            atexit.register(Disconnect, self.service_instance)
            
            # Get the vSphere service content
            self.content = self.service_instance.RetrieveContent()
            
            logger.info(f"Connected to vCenter server: {self.server}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to vCenter: {str(e)}")
            raise Exception(f"Failed to connect to vCenter: {str(e)}")
            
    def disconnect(self):
        """Disconnect from the vCenter server"""
        if self.service_instance:
            Disconnect(self.service_instance)
            self.service_instance = None
            self.content = None
            logger.info(f"Disconnected from vCenter server: {self.server}")
            
    def get_container_view(self, obj_type, container=None):
        """
        Get a view of container objects of a specific type
        
        Args:
            obj_type (list): List of object types to get
            container (vim.ManagedEntity): Container to start the view from
            
        Returns:
            vim.view.ContainerView: Container view of the specified objects
        """
        if not self.content:
            raise Exception("Not connected to vCenter")
            
        if container is None:
            container = self.content.rootFolder
            
        view_manager = self.content.viewManager
        container_view = view_manager.CreateContainerView(
            container=container,
            type=obj_type,
            recursive=True
        )
        
        return container_view
        
    def get_all_objects(self, obj_type):
        """
        Get all objects of a specific type
        
        Args:
            obj_type (list): List of object types to get
            
        Returns:
            list: List of objects of the specified type
        """
        container_view = self.get_container_view(obj_type)
        objects = container_view.view
        container_view.Destroy()
        
        return objects
    
    def get_virtual_machines(self):
        """
        Get all virtual machines
        
        Returns:
            list: List of virtual machines
        """
        return self.get_all_objects([vim.VirtualMachine])
        
    def get_hosts(self):
        """
        Get all ESXi hosts
        
        Returns:
            list: List of ESXi hosts
        """
        return self.get_all_objects([vim.HostSystem])
        
    def get_datastores(self):
        """
        Get all datastores
        
        Returns:
            list: List of datastores
        """
        return self.get_all_objects([vim.Datastore])
        
    def get_clusters(self):
        """
        Get all clusters
        
        Returns:
            list: List of clusters
        """
        return self.get_all_objects([vim.ClusterComputeResource])
        
    def get_resource_pools(self):
        """
        Get all resource pools
        
        Returns:
            list: List of resource pools
        """
        return self.get_all_objects([vim.ResourcePool])
        
    def get_networks(self):
        """
        Get all networks
        
        Returns:
            list: List of networks
        """
        return self.get_all_objects([vim.Network])
        
    def get_datacenters(self):
        """
        Get all datacenters
        
        Returns:
            list: List of datacenters
        """
        return self.get_all_objects([vim.Datacenter])
