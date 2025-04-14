#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere data collector module
"""

import datetime
import re
import logging
import sys
import os
from pyVmomi import vim
from contextlib import contextmanager

# Configure the logger
logger = logging.getLogger(__name__)

@contextmanager
def suppress_stdout_stderr():
    """
    Context manager to suppress stdout and stderr output
    
    This is useful for hiding error messages from pyVmomi that are not
    critical for the application's functioning. Output is redirected to
    the application log widget with DEBUG level instead of showing in 
    command windows.
    """
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    class LoggerWriter:
        def __init__(self, logger, level):
            self.logger = logger
            self.level = level
            self.buffer = ''
            
        def write(self, message):
            if message and message.strip():
                # Filter out known harmless PyVmomi errors
                if 'SSL:CERTIFICATE_VERIFY_FAILED' in message:
                    return
                if 'vim.fault' in message and 'vim.fault.NotFound' not in message:
                    self.logger.log(self.level, f"pyVmomi: {message.strip()}")
                    return
                # Allgemeine Fehler umleiten (nicht nur vim.fault)
                self.logger.log(self.level, f"pyVmomi: {message.strip()}")
                
        def flush(self):
            pass
    
    try:
        # Redirect stdout and stderr to logger with appropriate levels
        sys.stdout = LoggerWriter(logger, logging.DEBUG)
        sys.stderr = LoggerWriter(logger, logging.WARNING)
        yield
    finally:
        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

class DataCollector:
    """Collector for vSphere environment data"""
    
    def __init__(self, vsphere_client):
        """
        Initialize the data collector
        
        Args:
            vsphere_client (VSphereClient): Connected vSphere client
        """
        self.client = vsphere_client
        
    def collect_vm_info(self):
        """
        Collect information about virtual machines
        
        Returns:
            list: List of VM information dictionaries
        """
        logger.info("Collecting VM information")
        vms = self.client.get_virtual_machines()
        
        vm_info_list = []
        for vm in vms:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    # Get VM properties
                    summary = vm.summary
                    config = vm.config if vm.config else None
                    guest = vm.guest if vm.guest else None
                
                vm_info = {
                    'name': vm.name,
                    'power_state': summary.runtime.powerState,
                    'guest_full_name': summary.config.guestFullName if summary.config else "Unknown",
                    'vmware_tools_status': summary.guest.toolsStatus if summary.guest else "Unknown",
                    'vmware_tools_version': summary.guest.toolsVersionStatus if summary.guest else "Unknown",
                    'uuid': config.uuid if config else "Unknown",
                    'num_cpu': config.hardware.numCPU if config and config.hardware else 0,
                    'memory_mb': config.hardware.memoryMB if config and config.hardware else 0,
                    'ip_address': guest.ipAddress if guest else None,
                    'hostname': guest.hostName if guest else None,
                    'path': config.files.vmPathName if config and config.files else "Unknown",
                    'provisioned_space': summary.storage.committed + summary.storage.uncommitted if summary.storage else 0,
                    'used_space': summary.storage.committed if summary.storage else 0,
                }
                
                # Add disk information
                if config and config.hardware and config.hardware.device:
                    disks = []
                    for device in config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualDisk):
                            disk_info = {
                                'label': device.deviceInfo.label,
                                'capacity_kb': device.capacityInKB,
                                'thin_provisioned': device.backing.thinProvisioned if hasattr(device.backing, 'thinProvisioned') else False,
                                'datastore': device.backing.datastore.name if device.backing.datastore else "Unknown",
                                'file_name': device.backing.fileName
                            }
                            disks.append(disk_info)
                    vm_info['disks'] = disks
                    
                # Add network information
                if config and config.hardware and config.hardware.device:
                    networks = []
                    for device in config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualEthernetCard):
                            try:
                                if hasattr(device.backing, 'network'):
                                    network_name = device.backing.network.name
                                elif hasattr(device.backing, 'port') and hasattr(device.backing.port, 'portgroupKey'):
                                    network_name = device.backing.port.portgroupKey
                                else:
                                    network_name = "Unknown"
                                    
                                network_info = {
                                    'mac_address': device.macAddress if hasattr(device, 'macAddress') else "Unknown",
                                    'network_name': network_name,
                                    'adapter_type': type(device).__name__
                                }
                                networks.append(network_info)
                            except Exception as e:
                                logger.warning(f"Error getting network info for VM {vm.name}: {str(e)}")
                    vm_info['networks'] = networks
                    
                # Add snapshot information
                if vm.snapshot:
                    snapshots = self._get_vm_snapshots(vm)
                    vm_info['snapshots'] = snapshots
                else:
                    vm_info['snapshots'] = []
                
                vm_info_list.append(vm_info)
            
            except Exception as e:
                logger.error(f"Error collecting info for VM {vm.name}: {str(e)}")
                continue
                
        return vm_info_list

    def collect_vmware_tools_info(self):
        """
        Collect information about VMware Tools versions
        
        Returns:
            list: List of VM information dictionaries sorted by tools version (oldest first)
        """
        logger.info("Collecting VMware Tools information")
        vms = self.client.get_virtual_machines()
        
        tools_info_list = []
        for vm in vms:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    summary = vm.summary
                
                    # Skip if VM is a template
                    if summary.config.template:
                        continue
                    
                tools_info = {
                    'name': vm.name,
                    'power_state': summary.runtime.powerState,
                    'guest_full_name': summary.config.guestFullName if summary.config else "Unknown",
                    'vmware_tools_status': summary.guest.toolsStatus if summary.guest else "Unknown",
                    'vmware_tools_version': summary.guest.toolsVersionStatus if summary.guest else "Unknown",
                    'vmware_tools_running_status': summary.guest.toolsRunningStatus if summary.guest else "Unknown"
                }
                
                # Only include VMs that have Tools installed
                if tools_info['vmware_tools_status'] not in ['toolsNotInstalled', 'toolsNotRunning', None]:
                    tools_info_list.append(tools_info)
            
            except Exception as e:
                logger.error(f"Error collecting VMware Tools info for VM {vm.name}: {str(e)}")
                continue
                
        # Sort by tools version status (oldest first)
        # Order is: guestToolsNeedUpgrade, guestToolsCurrent
        def tools_version_sort_key(item):
            if item['vmware_tools_version'] == 'guestToolsNeedUpgrade':
                return 0
            elif item['vmware_tools_version'] == 'guestToolsCurrent':
                return 1
            else:
                return 2
                
        tools_info_list.sort(key=tools_version_sort_key)
        
        return tools_info_list
        
    def collect_snapshot_info(self):
        """
        Collect information about VM snapshots
        
        Returns:
            list: List of snapshot information dictionaries sorted by age (oldest first)
        """
        logger.info("Collecting snapshot information")
        vms = self.client.get_virtual_machines()
        
        snapshot_info_list = []
        for vm in vms:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    if vm.snapshot:
                        snapshots = self._get_vm_snapshots(vm)
                        for snapshot in snapshots:
                            snapshot['vm_name'] = vm.name
                            snapshot_info_list.append(snapshot)
            
            except Exception as e:
                logger.error(f"Error collecting snapshot info for VM {vm.name}: {str(e)}")
                continue
                
        # Sort by create time (oldest first)
        snapshot_info_list.sort(key=lambda x: x['create_time'])
        
        return snapshot_info_list
        
    def _get_vm_snapshots(self, vm):
        """
        Get snapshot information for a VM
        
        Args:
            vm (vim.VirtualMachine): Virtual machine object
            
        Returns:
            list: List of snapshot information dictionaries
        """
        snapshot_info = []
        
        if vm.snapshot:
            snapshot_list = self._get_snapshot_tree(vm.snapshot.rootSnapshotList)
            for snapshot in snapshot_list:
                # Calculate snapshot age
                create_time = snapshot['create_time']
                age = datetime.datetime.now() - create_time
                
                # Add age in days
                snapshot['age_days'] = age.days
                snapshot['age_hours'] = age.seconds // 3600
                
                snapshot_info.append(snapshot)
                
        return snapshot_info
        
    def _get_snapshot_tree(self, snapshots):
        """
        Recursively process snapshot tree
        
        Args:
            snapshots (list): List of snapshot objects
            
        Returns:
            list: Processed list of snapshot information dictionaries
        """
        snapshot_data = []
        for snapshot in snapshots:
            snap_info = {
                'name': snapshot.name,
                'description': snapshot.description,
                'create_time': snapshot.createTime,
                'state': snapshot.state,
                'snapshot_id': snapshot.id,
                'quiesced': snapshot.quiesced
            }
            snapshot_data.append(snap_info)
            
            # Process child snapshots
            if snapshot.childSnapshotList:
                snapshot_data.extend(self._get_snapshot_tree(snapshot.childSnapshotList))
                
        return snapshot_data
        
    def collect_orphaned_vmdks(self):
        """
        Collect information about orphaned VMDK files
        
        Returns:
            list: List of orphaned VMDK information dictionaries
        """
        logger.info("Collecting orphaned VMDK information")
        
        # Get all registered VMDKs
        registered_vmdks = set()
        vms = self.client.get_virtual_machines()
        
        for vm in vms:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    if vm.config and vm.config.hardware and vm.config.hardware.device:
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                # Get the datastore path
                                datastore_path = device.backing.fileName
                                registered_vmdks.add(datastore_path)
            except Exception as e:
                logger.error(f"Error getting VMDK info for VM {vm.name}: {str(e)}")
                continue
                
        # Get all datastores
        datastores = self.client.get_datastores()
        
        # Search for VMDK files in datastores
        orphaned_vmdks = []
        
        for datastore in datastores:
            try:
                # Skip if datastore browser is not available
                if not hasattr(datastore, 'browser'):
                    continue
                    
                # Create search spec for VMDK files
                search_spec = vim.host.DatastoreBrowser.SearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                search_spec.details = vim.host.DatastoreBrowser.FileInfo.Details()
                search_spec.details.fileSize = True
                search_spec.details.fileType = True
                search_spec.details.modification = True
                
                # Search the datastore
                browser = datastore.browser
                search_task = browser.SearchDatastoreSubFolders_Task(
                    datastorePath=f"[{datastore.name}]",
                    searchSpec=search_spec
                )
                
                # Wait for search to complete
                search_results = self.client.service_instance.content.taskManager.WaitForTask(search_task)
                
                # Process search results
                if hasattr(search_results, 'info') and hasattr(search_results.info, 'result'):
                    for result in search_results.info.result:
                        for file_info in result.file:
                            # Build datastore path
                            path = result.folderPath
                            if not path.endswith('/'):
                                path += '/'
                            path += file_info.path
                            
                            # Skip if this is not a VMDK file
                            if not path.lower().endswith('.vmdk'):
                                continue
                                
                            # Skip if this is a delta disk or descriptor file
                            if '-delta.vmdk' in path.lower() or '-flat.vmdk' in path.lower() or '-ctk.vmdk' in path.lower():
                                continue
                                
                            # Check if this VMDK is registered
                            if path not in registered_vmdks:
                                # Check whether this is a potential orphan
                                reason = "Unknown"
                                
                                # Check if in a known location for orphans
                                if '/forgotten/' in path.lower() or '/lost+found/' in path.lower():
                                    reason = "Located in a system recovery folder"
                                # Check if related VM files exist
                                elif self._is_vmdk_orphaned(result.folderPath, file_info.path):
                                    reason = "No associated VM configuration files found"
                                else:
                                    # Likely not an orphan, has VM files but not attached
                                    continue
                                
                                orphan_info = {
                                    'path': path,
                                    'datastore': datastore.name,
                                    'size': file_info.fileSize,
                                    'modification_time': file_info.modification,
                                    'reason': reason
                                }
                                orphaned_vmdks.append(orphan_info)
            
            except Exception as e:
                logger.error(f"Error scanning datastore {datastore.name} for orphaned VMDKs: {str(e)}")
                continue
                
        return orphaned_vmdks
        
    def _is_vmdk_orphaned(self, folder_path, vmdk_name):
        """
        Check if a VMDK file is orphaned by looking for associated VM files
        
        Args:
            folder_path (str): Datastore folder path
            vmdk_name (str): VMDK file name
            
        Returns:
            bool: True if the VMDK appears to be orphaned
        """
        # Extract VM name from VMDK file name (remove extension)
        vm_name = vmdk_name
        if vm_name.endswith('.vmdk'):
            vm_name = vm_name[:-5]
        
        # Check if there's a VMX file with the same name
        datastore_match = re.match(r'\[(.*?)\]', folder_path)
        if not datastore_match:
            logger.warning(f"Could not extract datastore name from path: {folder_path}")
            return False
            
        datastore = datastore_match.group(1)
        browser = None
        
        # Find the datastore browser
        datastores = self.client.get_datastores()
        for ds in datastores:
            if ds.name == datastore:
                browser = ds.browser
                break
                
        if browser is None:
            return False
            
        # Create search spec for VMX file
        search_spec = vim.host.DatastoreBrowser.SearchSpec()
        search_spec.matchPattern = [f"{vm_name}.vmx"]
        
        # Search the datastore folder
        search_task = browser.SearchDatastore_Task(
            datastorePath=folder_path,
            searchSpec=search_spec
        )
        
        # Wait for search to complete
        search_results = self.client.service_instance.content.taskManager.WaitForTask(search_task)
        
        # Check if VMX file was found
        if hasattr(search_results, 'info') and hasattr(search_results.info, 'result'):
            if len(search_results.info.result.file) == 0:
                # No VMX file found, likely orphaned
                return True
                
        return False
        
    def collect_host_info(self):
        """
        Collect information about ESXi hosts
        
        Returns:
            list: List of host information dictionaries
        """
        logger.info("Collecting ESXi host information")
        hosts = self.client.get_hosts()
        
        host_info_list = []
        for host in hosts:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    # Get host properties
                    summary = host.summary
                    hardware = host.hardware if hasattr(host, 'hardware') else None
                    config = host.config if hasattr(host, 'config') else None
                
                host_info = {
                    'name': host.name,
                    'connection_state': summary.runtime.connectionState,
                    'power_state': summary.runtime.powerState,
                    'in_maintenance_mode': summary.runtime.inMaintenanceMode,
                    'standalone': summary.runtime.inMaintenanceMode,
                    'cpu_model': hardware.cpuPkg[0].description if hardware and hardware.cpuPkg else "Unknown",
                    'cpu_cores': hardware.cpuInfo.numCpuCores if hardware and hardware.cpuInfo else 0,
                    'cpu_threads': hardware.cpuInfo.numCpuThreads if hardware and hardware.cpuInfo else 0,
                    'cpu_mhz': hardware.cpuInfo.hz / 1000000 if hardware and hardware.cpuInfo and hardware.cpuInfo.hz else 0,
                    'memory_size': hardware.memorySize / (1024 * 1024 * 1024) if hardware and hardware.memorySize else 0,
                    'model': hardware.systemInfo.model if hardware and hardware.systemInfo else "Unknown",
                    'vendor': hardware.systemInfo.vendor if hardware and hardware.systemInfo else "Unknown",
                    'version': config.product.fullName if config and config.product else "Unknown",
                    'build': config.product.build if config and config.product else "Unknown",
                }
                
                # Get cluster information if available
                if host.parent and hasattr(host.parent, 'name'):
                    host_info['cluster'] = host.parent.name
                else:
                    host_info['cluster'] = "Standalone"
                
                host_info_list.append(host_info)
            
            except Exception as e:
                logger.error(f"Error collecting info for host {host.name}: {str(e)}")
                continue
                
        return host_info_list
        
    def collect_datastore_info(self):
        """
        Collect information about datastores
        
        Returns:
            list: List of datastore information dictionaries
        """
        logger.info("Collecting datastore information")
        datastores = self.client.get_datastores()
        
        datastore_info_list = []
        for datastore in datastores:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    # Get datastore properties
                    summary = datastore.summary
                
                datastore_info = {
                    'name': datastore.name,
                    'type': summary.type,
                    'capacity': summary.capacity,
                    'free_space': summary.freeSpace,
                    'uncommitted': summary.uncommitted if hasattr(summary, 'uncommitted') else 0,
                    'accessible': summary.accessible,
                    'multipleHostAccess': summary.multipleHostAccess,
                    'url': summary.url,
                }
                
                # Calculate usage percentage
                if datastore_info['capacity'] > 0:
                    used_space = datastore_info['capacity'] - datastore_info['free_space']
                    datastore_info['usage_percent'] = (used_space / datastore_info['capacity']) * 100
                else:
                    datastore_info['usage_percent'] = 0
                
                datastore_info_list.append(datastore_info)
            
            except Exception as e:
                logger.error(f"Error collecting info for datastore {datastore.name}: {str(e)}")
                continue
                
        return datastore_info_list
        
    def collect_cluster_info(self):
        """
        Collect information about clusters
        
        Returns:
            list: List of cluster information dictionaries
        """
        logger.info("Collecting cluster information")
        clusters = self.client.get_clusters()
        
        cluster_info_list = []
        for cluster in clusters:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    # Get cluster properties
                    summary = cluster.summary
                
                cluster_info = {
                    'name': cluster.name,
                    'hosts': len(cluster.host) if hasattr(cluster, 'host') else 0,
                    'drs_enabled': summary.drsConfig.enabled if hasattr(summary, 'drsConfig') else False,
                    'drs_behavior': summary.drsConfig.defaultVmBehavior if hasattr(summary, 'drsConfig') else "Unknown",
                    'ha_enabled': summary.dasConfig.enabled if hasattr(summary, 'dasConfig') else False,
                    'total_cpu': summary.totalCpu if hasattr(summary, 'totalCpu') else 0,
                    'total_memory': summary.totalMemory if hasattr(summary, 'totalMemory') else 0,
                    'used_cpu': summary.usedCpu if hasattr(summary, 'usedCpu') else 0,
                    'used_memory': summary.usedMemory if hasattr(summary, 'usedMemory') else 0,
                }
                
                # Get list of hosts in cluster
                if hasattr(cluster, 'host'):
                    host_list = []
                    for host in cluster.host:
                        host_list.append(host.name)
                    cluster_info['host_list'] = host_list
                else:
                    cluster_info['host_list'] = []
                
                cluster_info_list.append(cluster_info)
            
            except Exception as e:
                logger.error(f"Error collecting info for cluster {cluster.name}: {str(e)}")
                continue
                
        return cluster_info_list
        
    def collect_resource_pool_info(self):
        """
        Collect information about resource pools
        
        Returns:
            list: List of resource pool information dictionaries
        """
        logger.info("Collecting resource pool information")
        resource_pools = self.client.get_resource_pools()
        
        resource_pool_info_list = []
        for pool in resource_pools:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    # Get resource pool properties
                    summary = pool.summary
                    config = pool.config if hasattr(pool, 'config') else None
                
                pool_info = {
                    'name': pool.name,
                    'cpu_shares': config.cpuAllocation.shares.shares if config and config.cpuAllocation and config.cpuAllocation.shares else 0,
                    'cpu_limit': config.cpuAllocation.limit if config and config.cpuAllocation else -1,
                    'cpu_reservation': config.cpuAllocation.reservation if config and config.cpuAllocation else 0,
                    'memory_shares': config.memoryAllocation.shares.shares if config and config.memoryAllocation and config.memoryAllocation.shares else 0,
                    'memory_limit': config.memoryAllocation.limit if config and config.memoryAllocation else -1,
                    'memory_reservation': config.memoryAllocation.reservation if config and config.memoryAllocation else 0,
                }
                
                # Get parent information
                if pool.parent:
                    if isinstance(pool.parent, vim.ClusterComputeResource):
                        pool_info['parent_type'] = 'Cluster'
                        pool_info['parent_name'] = pool.parent.name
                    elif isinstance(pool.parent, vim.ResourcePool):
                        pool_info['parent_type'] = 'Resource Pool'
                        pool_info['parent_name'] = pool.parent.name
                    else:
                        pool_info['parent_type'] = type(pool.parent).__name__
                        pool_info['parent_name'] = pool.parent.name if hasattr(pool.parent, 'name') else "Unknown"
                else:
                    pool_info['parent_type'] = "None"
                    pool_info['parent_name'] = "None"
                
                resource_pool_info_list.append(pool_info)
            
            except Exception as e:
                logger.error(f"Error collecting info for resource pool {pool.name}: {str(e)}")
                continue
                
        return resource_pool_info_list
        
    def collect_network_info(self):
        """
        Collect information about networks
        
        Returns:
            list: List of network information dictionaries
        """
        logger.info("Collecting network information")
        networks = self.client.get_networks()
        
        network_info_list = []
        for network in networks:
            try:
                # Suppress stdout/stderr to prevent PyVmomi error messages
                with suppress_stdout_stderr():
                    network_info = {
                        'name': network.name,
                        'accessible': network.summary.accessible if hasattr(network.summary, 'accessible') else False,
                        'type': type(network).__name__,  # Network type (DistributedVirtualPortgroup, Network, etc.)
                    }
                
                # Get additional properties based on network type
                if isinstance(network, vim.dvs.DistributedVirtualPortgroup):
                    # This is a DVS portgroup
                    config = network.config if hasattr(network, 'config') else None
                    
                    if config:
                        network_info['vlan_type'] = config.defaultPortConfig.vlan.__class__.__name__ if hasattr(config.defaultPortConfig, 'vlan') else "Unknown"
                        
                        # Get VLAN ID if it's a single VLAN
                        if isinstance(config.defaultPortConfig.vlan, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec) and hasattr(config.defaultPortConfig.vlan, 'vlanId'):
                            network_info['vlan_id'] = config.defaultPortConfig.vlan.vlanId
                        else:
                            network_info['vlan_id'] = "Multiple or None"
                            
                        # Get DVS name
                        if config.distributedVirtualSwitch:
                            network_info['dvs_name'] = config.distributedVirtualSwitch.name
                        else:
                            network_info['dvs_name'] = "Unknown"
                            
                # Add to list
                network_info_list.append(network_info)
            
            except Exception as e:
                logger.error(f"Error collecting info for network {network.name}: {str(e)}")
                continue
                
        return network_info_list
