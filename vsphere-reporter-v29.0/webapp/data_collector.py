#!/usr/bin/env python3
"""
Data Collector Module for VMware vSphere Reporter Web Edition
Collects and processes data from vSphere environments
"""

import logging
import humanize
from datetime import datetime, timedelta
from pyVmomi import vim

# Configure logger
logger = logging.getLogger(__name__)

class DataCollector:
    """Collector for vSphere environment data"""
    
    def __init__(self, vsphere_client):
        """
        Initialize the data collector
        
        Args:
            vsphere_client: Connected VSphereClient instance
        """
        self.client = vsphere_client
        self.logger = logging.getLogger(__name__)
    
    def collect_vmware_tools_info(self):
        """
        Collect VMware Tools information for all VMs
        
        Returns:
            list: List of VM information dictionaries, sorted by tools status and version
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting VMware Tools information")
        vms = self.client.get_all_vms()
        
        result = []
        for vm in vms:
            # Skip templates
            if vm.config.template:
                continue
            
            # Extract basic VM information
            vm_info = {
                'name': vm.name,
                'power_state': vm.runtime.powerState,
                'tools_version': vm.guest.toolsVersion if hasattr(vm.guest, 'toolsVersion') else 'N/A',
                'tools_status': vm.guest.toolsStatus if hasattr(vm.guest, 'toolsStatus') else 'N/A',
                'tools_running_status': vm.guest.toolsRunningStatus if hasattr(vm.guest, 'toolsRunningStatus') else 'N/A',
            }
            
            # Convert version to numeric for sorting
            version_parts = vm_info['tools_version'].split('.')
            vm_info['version_numeric'] = int(''.join(version_parts)) if vm_info['tools_version'] != 'N/A' and version_parts[0].isdigit() else 0
            
            result.append(vm_info)
        
        # Sort by version (oldest first) and then by status
        result.sort(key=lambda x: (x['version_numeric'], x['tools_status']))
        
        self.logger.info(f"Collected VMware Tools information for {len(result)} VMs")
        return result
    
    def collect_snapshot_info(self):
        """
        Collect snapshot information for all VMs
        
        Returns:
            list: List of snapshot information dictionaries, sorted by age (oldest first)
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting snapshot information")
        vms = self.client.get_all_vms()
        
        result = []
        for vm in vms:
            # Skip VMs without snapshots
            if not vm.snapshot:
                continue
            
            snapshot_list = []
            self._get_snapshot_tree(vm, vm.snapshot.rootSnapshotList, snapshot_list)
            
            for snapshot in snapshot_list:
                # Calculate age in days
                age_days = (datetime.now() - snapshot['create_time']).days
                
                # Add VM information
                snapshot['vm_name'] = vm.name
                snapshot['age_days'] = age_days
                snapshot['age_text'] = humanize.naturaldelta(timedelta(days=age_days))
                
                result.append(snapshot)
        
        # Sort by creation time (oldest first)
        result.sort(key=lambda x: x['create_time'])
        
        self.logger.info(f"Collected information for {len(result)} snapshots")
        return result
    
    def _get_snapshot_tree(self, vm, snapshot_list, result):
        """
        Process the snapshot tree recursively
        
        Args:
            vm: Virtual Machine object
            snapshot_list: List of snapshot objects to process
            result: List to store the processed snapshot information
        """
        for snapshot in snapshot_list:
            # Extract snapshot information
            snapshot_info = {
                'name': snapshot.name,
                'description': snapshot.description,
                'create_time': snapshot.createTime,
                'id': snapshot.id,
                'state': snapshot.state,
                'quiesced': snapshot.quiesced,
                'size_mb': 0  # Will be filled later
            }
            
            # Get snapshot size if available
            try:
                snapshot_size = 0
                for file in vm.layoutEx.file:
                    if file.type == 'snapshotData' and file.key.startswith(f'snapshot-{snapshot.id}'):
                        snapshot_size += file.size
                snapshot_info['size_mb'] = snapshot_size / (1024 * 1024)
            except Exception as e:
                self.logger.warning(f"Failed to get snapshot size for {snapshot.name}: {str(e)}")
            
            result.append(snapshot_info)
            
            # Process child snapshots recursively
            if hasattr(snapshot, 'childSnapshotList') and snapshot.childSnapshotList:
                self._get_snapshot_tree(vm, snapshot.childSnapshotList, result)
    
    def collect_vm_hardware_info(self):
        """
        Collect hardware information for all VMs
        
        Returns:
            list: List of VM hardware information dictionaries
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting VM hardware information")
        vms = self.client.get_all_vms()
        
        result = []
        for vm in vms:
            # Extract hardware information
            vm_info = {
                'name': vm.name,
                'power_state': vm.runtime.powerState,
                'cpu_count': vm.config.hardware.numCPU,
                'memory_mb': vm.config.hardware.memoryMB,
                'guest_os': vm.config.guestFullName,
                'guest_os_id': vm.config.guestId,
                'hardware_version': vm.config.version,
                'template': vm.config.template,
                'uuid': vm.config.uuid,
                'instance_uuid': vm.config.instanceUuid,
                'path': vm.config.files.vmPathName if hasattr(vm.config.files, 'vmPathName') else 'N/A',
            }
            
            # Add network interfaces
            vm_info['network_adapters'] = []
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualEthernetCard):
                    network_name = 'N/A'
                    try:
                        if hasattr(device.backing, 'network') and device.backing.network:
                            network_name = device.backing.network.name
                        elif hasattr(device.backing, 'port') and device.backing.port:
                            network_name = device.backing.port.portgroupKey
                    except Exception:
                        pass
                    
                    vm_info['network_adapters'].append({
                        'type': type(device).__name__,
                        'mac_address': device.macAddress if hasattr(device, 'macAddress') else 'N/A',
                        'network': network_name,
                        'connected': device.connectable.connected if hasattr(device, 'connectable') else False,
                    })
            
            # Add disks
            vm_info['disks'] = []
            for device in vm.config.hardware.device:
                if isinstance(device, vim.vm.device.VirtualDisk):
                    vm_info['disks'].append({
                        'label': device.deviceInfo.label,
                        'capacity_gb': device.capacityInKB / (1024 * 1024),
                        'thin_provisioned': device.backing.thinProvisioned if hasattr(device.backing, 'thinProvisioned') else False,
                        'path': device.backing.fileName if hasattr(device.backing, 'fileName') else 'N/A',
                    })
            
            result.append(vm_info)
        
        self.logger.info(f"Collected hardware information for {len(result)} VMs")
        return result
    
    def collect_datastore_info(self):
        """
        Collect information about datastores
        
        Returns:
            list: List of datastore information dictionaries
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting datastore information")
        datastores = self.client.get_all_datastores()
        
        result = []
        for ds in datastores:
            # Calculate capacity and usage
            capacity = ds.summary.capacity
            free_space = ds.summary.freeSpace
            used_space = capacity - free_space
            used_percentage = (used_space / capacity * 100) if capacity > 0 else 0
            
            datastore_info = {
                'name': ds.name,
                'type': ds.summary.type,
                'url': ds.summary.url,
                'capacity': humanize.naturalsize(capacity),
                'free_space': humanize.naturalsize(free_space),
                'used_space': humanize.naturalsize(used_space),
                'used_percentage': used_percentage,
                'maintenance_mode': ds.summary.maintenanceMode,
                'accessible': ds.summary.accessible,
                'capacity_bytes': capacity,
                'free_space_bytes': free_space,
                'used_space_bytes': used_space,
            }
            
            # Add hosts that can access this datastore
            datastore_info['hosts'] = []
            if hasattr(ds, 'host') and ds.host:
                for host_mount in ds.host:
                    datastore_info['hosts'].append({
                        'name': host_mount.key.name,
                        'state': host_mount.mountInfo.mounted,
                        'path': host_mount.mountInfo.path,
                    })
            
            result.append(datastore_info)
        
        # Sort by used percentage (highest first)
        result.sort(key=lambda x: x['used_percentage'], reverse=True)
        
        self.logger.info(f"Collected information for {len(result)} datastores")
        return result
    
    def collect_cluster_info(self):
        """
        Collect information about clusters
        
        Returns:
            list: List of cluster information dictionaries
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting cluster information")
        clusters = self.client.get_all_clusters()
        
        result = []
        for cluster in clusters:
            # Extract cluster configuration
            drs_config = {
                'enabled': cluster.configuration.drsConfig.enabled,
                'default_vm_behavior': str(cluster.configuration.drsConfig.defaultVmBehavior),
                'automation_level': str(cluster.configuration.drsConfig.defaultVmBehavior),
            }
            
            ha_config = {
                'enabled': cluster.configuration.dasConfig.enabled,
                'admission_control_enabled': cluster.configuration.dasConfig.admissionControlEnabled,
                'host_monitoring': cluster.configuration.dasConfig.hostMonitoring,
            }
            
            # Extract resources and status
            total_cpu_mhz = 0
            total_memory_mb = 0
            if hasattr(cluster, 'summary') and hasattr(cluster.summary, 'totalCpu'):
                total_cpu_mhz = cluster.summary.totalCpu
                total_memory_mb = cluster.summary.totalMemory / (1024 * 1024)
            
            cluster_info = {
                'name': cluster.name,
                'num_hosts': len(cluster.host) if hasattr(cluster, 'host') else 0,
                'num_effective_hosts': len(cluster.host) if hasattr(cluster, 'host') else 0,
                'total_cpu_mhz': total_cpu_mhz,
                'total_memory_mb': total_memory_mb,
                'drs_config': drs_config,
                'ha_config': ha_config,
            }
            
            # Add hosts in this cluster
            cluster_info['hosts'] = []
            if hasattr(cluster, 'host') and cluster.host:
                for host in cluster.host:
                    cluster_info['hosts'].append({
                        'name': host.name,
                        'state': str(host.runtime.connectionState),
                    })
            
            result.append(cluster_info)
        
        self.logger.info(f"Collected information for {len(result)} clusters")
        return result
    
    def collect_host_info(self):
        """
        Collect information about ESXi hosts
        
        Returns:
            list: List of host information dictionaries
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting ESXi host information")
        hosts = self.client.get_all_hosts()
        
        result = []
        for host in hosts:
            # Extract hardware information
            hardware_info = {
                'vendor': host.hardware.systemInfo.vendor,
                'model': host.hardware.systemInfo.model,
                'cpu_model': host.hardware.cpuPkg[0].description if host.hardware.cpuPkg else 'N/A',
                'cpu_cores': host.hardware.cpuInfo.numCpuCores,
                'cpu_threads': host.hardware.cpuInfo.numCpuThreads,
                'memory_mb': host.hardware.memorySize / (1024 * 1024),
            }
            
            # Extract software information
            software_info = {
                'version': host.config.product.version,
                'build': host.config.product.build,
                'full_name': host.config.product.fullName,
            }
            
            # Calculate uptime
            uptime_seconds = host.summary.quickStats.uptime if hasattr(host.summary.quickStats, 'uptime') else 0
            uptime_text = humanize.naturaltime(datetime.now() - timedelta(seconds=uptime_seconds))
            
            host_info = {
                'name': host.name,
                'connection_state': str(host.runtime.connectionState),
                'power_state': str(host.runtime.powerState),
                'maintenance_mode': host.runtime.inMaintenanceMode,
                'uptime_seconds': uptime_seconds,
                'uptime_text': uptime_text,
                'hardware': hardware_info,
                'software': software_info,
            }
            
            # Add VMs running on this host
            host_info['vms'] = []
            if hasattr(host, 'vm') and host.vm:
                for vm in host.vm:
                    host_info['vms'].append({
                        'name': vm.name,
                        'power_state': str(vm.runtime.powerState),
                    })
            
            result.append(host_info)
        
        self.logger.info(f"Collected information for {len(result)} ESXi hosts")
        return result
    
    def collect_resource_pool_info(self):
        """
        Collect information about resource pools
        
        Returns:
            list: List of resource pool information dictionaries
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting resource pool information")
        resource_pools = self.client.get_all_resource_pools()
        
        result = []
        for rp in resource_pools:
            # Skip default or hidden resource pools
            if rp.parent and isinstance(rp.parent, vim.ResourcePool):
                if rp.name == 'Resources' and rp.parent.name == 'Resources':
                    continue
            
            # Extract resource pool configuration
            cpu_config = {
                'reservation': rp.config.cpuAllocation.reservation,
                'limit': rp.config.cpuAllocation.limit,
                'expandable_reservation': rp.config.cpuAllocation.expandableReservation,
                'shares': rp.config.cpuAllocation.shares.shares,
                'shares_level': str(rp.config.cpuAllocation.shares.level),
            }
            
            memory_config = {
                'reservation': rp.config.memoryAllocation.reservation,
                'limit': rp.config.memoryAllocation.limit,
                'expandable_reservation': rp.config.memoryAllocation.expandableReservation,
                'shares': rp.config.memoryAllocation.shares.shares,
                'shares_level': str(rp.config.memoryAllocation.shares.level),
            }
            
            # Get parent name
            parent_name = 'N/A'
            parent_type = 'N/A'
            if rp.parent:
                parent_name = rp.parent.name
                parent_type = type(rp.parent).__name__
            
            resource_pool_info = {
                'name': rp.name,
                'parent_name': parent_name,
                'parent_type': parent_type,
                'cpu_config': cpu_config,
                'memory_config': memory_config,
            }
            
            # Add VMs in this resource pool
            resource_pool_info['vms'] = []
            if hasattr(rp, 'vm') and rp.vm:
                for vm in rp.vm:
                    resource_pool_info['vms'].append({
                        'name': vm.name,
                        'power_state': str(vm.runtime.powerState),
                    })
            
            result.append(resource_pool_info)
        
        self.logger.info(f"Collected information for {len(result)} resource pools")
        return result
    
    def collect_network_info(self):
        """
        Collect information about networks
        
        Returns:
            list: List of network information dictionaries
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting network information")
        networks = self.client.get_all_networks()
        
        result = []
        for network in networks:
            # Determine network type
            network_type = 'Standard Network'
            if isinstance(network, vim.dvs.DistributedVirtualPortgroup):
                network_type = 'Distributed Port Group'
            
            network_info = {
                'name': network.name,
                'type': network_type,
                'host_count': len(network.host) if hasattr(network, 'host') else 0,
                'vm_count': len(network.vm) if hasattr(network, 'vm') else 0,
            }
            
            # Add additional information for distributed port groups
            if isinstance(network, vim.dvs.DistributedVirtualPortgroup):
                network_info['vlan_id'] = network.config.defaultPortConfig.vlan.vlanId if hasattr(network.config.defaultPortConfig, 'vlan') else 'N/A'
                network_info['switch_name'] = network.config.distributedVirtualSwitch.name if hasattr(network.config, 'distributedVirtualSwitch') else 'N/A'
            
            # Add VMs connected to this network
            network_info['vms'] = []
            if hasattr(network, 'vm') and network.vm:
                for vm in network.vm:
                    network_info['vms'].append({
                        'name': vm.name,
                        'power_state': str(vm.runtime.powerState),
                    })
            
            result.append(network_info)
        
        self.logger.info(f"Collected information for {len(result)} networks")
        return result