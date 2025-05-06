#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter v29.0
VSphere Client Module

Final Fixed Version 10 - Simplified Structure
Copyright (c) 2025 Bechtle GmbH
"""

import logging
import datetime
import ssl
import os
from pyVim import connect
from pyVmomi import vim, vmodl

logger = logging.getLogger(__name__)

class VSphereConnectionError(Exception):
    """Exception raised for vSphere connection errors"""
    pass

class VSphereClient:
    """Client for VMware vSphere API interactions"""
    
    def __init__(self, host, user, password, ignore_ssl=False):
        """Initialize the vSphere client with connection parameters
        
        Args:
            host (str): vCenter hostname or IP
            user (str): vCenter username
            password (str): vCenter password
            ignore_ssl (bool): Whether to ignore SSL certificate validation
        """
        self.host = host
        self.user = user
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.service_instance = None
        self.content = None
    
    def connect(self):
        """Connect to vCenter server
        
        Returns:
            bool: True if connection successful, False otherwise
        
        Raises:
            VSphereConnectionError: If connection fails
        """
        try:
            if self.ignore_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                context.verify_mode = ssl.CERT_NONE
            else:
                context = None
            
            logger.info(f"Verbinde mit vCenter {self.host}...")
            self.service_instance = connect.SmartConnect(
                host=self.host,
                user=self.user,
                pwd=self.password,
                sslContext=context
            )
            
            if not self.service_instance:
                raise VSphereConnectionError("Konnte keine Verbindung zum vCenter herstellen")
            
            self.content = self.service_instance.RetrieveContent()
            logger.info(f"Erfolgreich mit vCenter {self.host} verbunden")
            return True
        
        except vmodl.MethodFault as e:
            logger.error(f"vSphere API-Fehler: {str(e)}")
            raise VSphereConnectionError(f"vSphere API-Fehler: {str(e)}")
        except Exception as e:
            logger.error(f"Verbindungsfehler: {str(e)}")
            raise VSphereConnectionError(f"Verbindungsfehler: {str(e)}")
    
    def disconnect(self):
        """Disconnect from vCenter server"""
        if self.service_instance:
            connect.Disconnect(self.service_instance)
            self.service_instance = None
            self.content = None
            logger.info(f"Verbindung zu vCenter {self.host} getrennt")
    
    def get_total_vms(self):
        """Get total number of VMs in the environment
        
        Returns:
            int: Total number of VMs
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        vm_count = len(container.view)
        container.Destroy()
        return vm_count
    
    def get_total_hosts(self):
        """Get total number of hosts in the environment
        
        Returns:
            int: Total number of hosts
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.HostSystem], True
        )
        host_count = len(container.view)
        container.Destroy()
        return host_count
    
    def get_total_datastores(self):
        """Get total number of datastores in the environment
        
        Returns:
            int: Total number of datastores
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Datastore], True
        )
        datastore_count = len(container.view)
        container.Destroy()
        return datastore_count
    
    def get_total_clusters(self):
        """Get total number of clusters in the environment
        
        Returns:
            int: Total number of clusters
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.ClusterComputeResource], True
        )
        cluster_count = len(container.view)
        container.Destroy()
        return cluster_count
    
    def get_vms_by_power_state(self):
        """Get VMs grouped by power state
        
        Returns:
            dict: Dictionary with power states as keys and counts as values
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        power_states = {
            'poweredOn': 0,
            'poweredOff': 0,
            'suspended': 0
        }
        
        for vm in container.view:
            power_state = vm.runtime.powerState
            if power_state in power_states:
                power_states[power_state] += 1
        
        container.Destroy()
        return power_states
    
    def get_outdated_tools_count(self):
        """Get count of VMs with outdated VMware Tools
        
        Returns:
            int: Number of VMs with outdated VMware Tools
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        outdated_count = 0
        for vm in container.view:
            # Check if VMware Tools is installed and needs upgrade
            if vm.guest.toolsStatus in [
                vim.vm.GuestInfo.ToolsStatus.toolsOld,
                vim.vm.GuestInfo.ToolsStatus.toolsNotInstalled
            ]:
                outdated_count += 1
        
        container.Destroy()
        return outdated_count
    
    def get_snapshots_count(self):
        """Get total number of snapshots in the environment
        
        Returns:
            int: Total number of snapshots
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        snapshot_count = 0
        for vm in container.view:
            if vm.snapshot:
                snapshot_list = self._get_snapshots_recursively(vm.snapshot.rootSnapshotList)
                snapshot_count += len(snapshot_list)
        
        container.Destroy()
        return snapshot_count
    
    def _get_snapshots_recursively(self, snapshots):
        """Recursively get all snapshots from a snapshot list
        
        Args:
            snapshots (list): List of snapshot objects
            
        Returns:
            list: Flattened list of all snapshots
        """
        result = []
        for snapshot in snapshots:
            result.append(snapshot)
            if snapshot.childSnapshotList:
                result.extend(self._get_snapshots_recursively(snapshot.childSnapshotList))
        return result
    
    def get_orphaned_vmdks_count(self):
        """Get count of orphaned VMDK files
        
        Returns:
            int: Number of orphaned VMDK files
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        # This is a simplified implementation that needs proper detection logic
        # in a production environment. Currently returns a placeholder count.
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Datastore], True
        )
        
        orphaned_count = 0
        for datastore in container.view:
            try:
                browser = datastore.browser
                search_spec = vim.HostDatastoreBrowserSearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                
                # Get all VMDKs
                task = browser.SearchDatastore_Task(
                    datastorePath=f"[{datastore.name}]",
                    searchSpec=search_spec
                )
                
                # Wait for the task to complete
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    continue
                
                if task.info.state == vim.TaskInfo.State.success and task.info.result:
                    for file_info in task.info.result.file:
                        # Basic check: If file name contains "-flat" or "-delta", 
                        # these are typically dependent files and not orphaned
                        # This is a very simplified check and not reliable for production use
                        if (file_info.path.endswith(".vmdk") and 
                            "-flat.vmdk" not in file_info.path and 
                            "-delta.vmdk" not in file_info.path and 
                            self._is_potentially_orphaned(datastore, file_info.path)):
                            orphaned_count += 1
            except Exception as e:
                logger.warning(f"Error checking for orphaned VMDKs on datastore {datastore.name}: {str(e)}")
        
        container.Destroy()
        return orphaned_count
    
    def _is_potentially_orphaned(self, datastore, vmdk_path):
        """Very basic check if a VMDK might be orphaned
        
        This is a simplified implementation that would need significant enhancement
        for production use. It just checks if the VMDK is referenced by any VM.
        
        Args:
            datastore (vim.Datastore): Datastore object
            vmdk_path (str): Path of the VMDK file
            
        Returns:
            bool: True if potentially orphaned, False otherwise
        """
        # Get all VMs
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        # Check each VM's disks to see if they reference this VMDK
        for vm in container.view:
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualDisk):
                    if hasattr(device.backing, 'fileName'):
                        # Extract just the filename for comparison
                        if f"[{datastore.name}] {vmdk_path}" in device.backing.fileName:
                            container.Destroy()
                            return False
        
        container.Destroy()
        return True
    
    def get_vmware_tools_data(self):
        """Get detailed VMware Tools status information for all VMs
        
        Returns:
            list: List of dictionaries with VMware Tools information
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        tools_data = []
        for vm in container.view:
            # Skip templates
            if vm.config.template:
                continue
            
            # Get Tools status and version
            tools_status = "Unknown"
            tools_version = "Unknown"
            
            if vm.guest.toolsStatus == vim.vm.GuestInfo.ToolsStatus.toolsOld:
                tools_status = "Outdated"
            elif vm.guest.toolsStatus == vim.vm.GuestInfo.ToolsStatus.toolsNotInstalled:
                tools_status = "Not installed"
                tools_version = "Not installed"
            elif vm.guest.toolsStatus == vim.vm.GuestInfo.ToolsStatus.toolsOk:
                tools_status = "Up-to-date"
            
            if vm.guest.toolsVersion and tools_version == "Unknown":
                tools_version = vm.guest.toolsVersion
            
            # Get OS info
            os_name = vm.config.guestFullName if vm.config.guestFullName else "Unknown"
            
            # Power state
            power_state = vm.runtime.powerState
            
            tools_data.append({
                'vm_name': vm.name,
                'status': tools_status,
                'version': tools_version,
                'os': os_name,
                'power_state': power_state
            })
        
        container.Destroy()
        return tools_data
    
    def get_snapshots_data(self):
        """Get detailed snapshot information for all VMs
        
        Returns:
            list: List of dictionaries with snapshot information
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        snapshots_data = []
        for vm in container.view:
            if vm.snapshot:
                vm_snapshot_data = self._get_vm_snapshot_data(vm)
                snapshots_data.extend(vm_snapshot_data)
        
        container.Destroy()
        return snapshots_data
    
    def _get_vm_snapshot_data(self, vm):
        """Get snapshot data for a specific VM
        
        Args:
            vm (vim.VirtualMachine): VM object
            
        Returns:
            list: List of dictionaries with snapshot information
        """
        result = []
        
        def process_snapshot_tree(tree, parent_path=""):
            for snapshot in tree:
                path = parent_path + "/" + snapshot.name if parent_path else snapshot.name
                
                # Calculate snapshot size
                # Note: Getting accurate snapshot size is complex and may require additional calculations
                size_mb = 0
                if hasattr(snapshot, 'sizeBytes'):
                    size_mb = snapshot.sizeBytes / (1024 * 1024)
                
                # Get creation time
                creation_time = None
                if hasattr(snapshot, 'createTime'):
                    creation_time = snapshot.createTime
                
                result.append({
                    'vm_name': vm.name,
                    'name': snapshot.name,
                    'description': snapshot.description if hasattr(snapshot, 'description') else "",
                    'creation_time': creation_time,
                    'size_mb': size_mb,
                    'path': path,
                    'state': snapshot.state if hasattr(snapshot, 'state') else "unknown"
                })
                
                if snapshot.childSnapshotList:
                    process_snapshot_tree(snapshot.childSnapshotList, path)
        
        if vm.snapshot:
            process_snapshot_tree(vm.snapshot.rootSnapshotList)
        
        return result
    
    def get_orphaned_vmdks_data(self):
        """Get detailed information about orphaned VMDK files
        
        Returns:
            list: List of dictionaries with orphaned VMDK information
        """
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
            
        # For demo mode, return demo data
        if hasattr(self, 'demo_mode') and self.demo_mode:
            import demo_data
            return demo_data.get_orphaned_vmdks_data()
        
        orphaned_vmdks = []
        
        # First get all VMs and their disk files to optimize performance
        vm_container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        # Create a dictionary to track all VMDKs currently in use
        used_vmdks = {}
        for vm in vm_container.view:
            try:
                if vm.config and vm.config.hardware and vm.config.hardware.device:
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualDisk):
                            if hasattr(device.backing, 'fileName'):
                                used_vmdks[device.backing.fileName] = vm.name
            except Exception as e:
                logger.warning(f"Error checking VM disks for {vm.name}: {str(e)}")
        
        vm_container.Destroy()
        
        # Now check each datastore for VMDKs
        datastore_container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Datastore], True
        )
        
        for datastore in datastore_container.view:
            try:
                browser = datastore.browser
                search_spec = vim.HostDatastoreBrowserSearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                search_spec.details = vim.host.DatastoreBrowser.FileInfo.Details()
                search_spec.details.fileSize = True
                search_spec.details.fileType = True
                search_spec.details.modification = True
                
                # Get all VMDKs
                task = browser.SearchDatastore_Task(
                    datastorePath=f"[{datastore.name}]",
                    searchSpec=search_spec
                )
                
                # Wait for the task to complete
                while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                    continue
                
                if task.info.state == vim.TaskInfo.State.success and task.info.result:
                    for file_info in task.info.result.file:
                        # Skip descriptor files and dependent disks
                        if (file_info.path.endswith(".vmdk") and 
                            "-flat.vmdk" not in file_info.path and 
                            "-delta.vmdk" not in file_info.path and 
                            "-rdm.vmdk" not in file_info.path and 
                            "-ctk.vmdk" not in file_info.path):
                            
                            # Get full path
                            full_path = f"[{datastore.name}] {file_info.path}"
                            
                            # Check if this VMDK is being used by any VM
                            if full_path not in used_vmdks:
                                # It might be orphaned, but do additional checks
                                
                                # Check if there's a corresponding .vmx file in same directory
                                vmdk_dir = os.path.dirname(file_info.path)
                                vmx_search_spec = vim.HostDatastoreBrowserSearchSpec()
                                vmx_search_spec.matchPattern = ["*.vmx"]
                                
                                vmx_task = browser.SearchDatastore_Task(
                                    datastorePath=f"[{datastore.name}] {vmdk_dir}", 
                                    searchSpec=vmx_search_spec
                                )
                                
                                # Wait for VMX search to complete
                                while vmx_task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                                    continue
                                
                                # If there's a VMX file in the same directory, it's likely a template or unregistered VM
                                if (vmx_task.info.state == vim.TaskInfo.State.success and 
                                    vmx_task.info.result and 
                                    vmx_task.info.result.file):
                                    # Not truly orphaned - likely a template or unregistered VM
                                    continue
                                
                                # Get file size
                                size_bytes = file_info.fileSize if hasattr(file_info, 'fileSize') else 0
                                
                                # Get modification time
                                mod_time = file_info.modification if hasattr(file_info, 'modification') else None
                                
                                # This is truly an orphaned VMDK
                                orphaned_vmdks.append({
                                    'name': file_info.path,
                                    'datastore': datastore.name,
                                    'path': full_path,
                                    'size_bytes': size_bytes,
                                    'modification_time': mod_time,
                                    'recommended_action': "Manual inspection required before removal"
                                })
            except Exception as e:
                logger.warning(f"Error checking for orphaned VMDKs on datastore {datastore.name}: {str(e)}")
        
        datastore_container.Destroy()
        return orphaned_vmdks