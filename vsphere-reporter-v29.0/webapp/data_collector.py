#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Datensammler für vSphere-Umgebungsinformationen
"""

import logging
import humanize
from datetime import datetime

import pyVmomi
from pyVmomi import vim

logger = logging.getLogger('vsphere_reporter')

class DataCollector:
    """Hauptklasse für das Sammeln von Daten aus der vSphere-Umgebung"""
    
    def __init__(self, vsphere_client):
        """
        Initialisiert den Datensammler
        
        Args:
            vsphere_client: Verbundener VSphereClient
        """
        self.client = vsphere_client
        self.content = vsphere_client.content if vsphere_client else None
    
    def collect_vms(self):
        """
        Sammelt Informationen über alle virtuellen Maschinen
        
        Returns:
            list: Liste von VM-Informationsdictionaries
        """
        logger.info("Sammle Informationen über virtuelle Maschinen...")
        
        vms = self.client.get_all_vms()
        vm_info_list = []
        
        for vm in vms:
            try:
                vm_info = {
                    'name': vm.name,
                    'power_state': str(vm.runtime.powerState),
                    'guest_full_name': vm.config.guestFullName if vm.config else 'Unbekannt',
                    'cpus': vm.config.hardware.numCPU if vm.config and vm.config.hardware else 0,
                    'memory_mb': vm.config.hardware.memoryMB if vm.config and vm.config.hardware else 0,
                    'vmware_tools_status': self._get_tools_status(vm),
                    'vmware_tools_version': self._get_tools_version(vm),
                    'vmdks': self._get_vm_disks(vm),
                    'ip_address': vm.guest.ipAddress if vm.guest else None,
                    'annotation': vm.config.annotation if vm.config else None,
                    'uuid': vm.config.uuid if vm.config else None,
                    'instance_uuid': vm.config.instanceUuid if vm.config else None,
                    'host': vm.runtime.host.name if vm.runtime and vm.runtime.host else None,
                    'datastore': self._get_vm_datastores(vm),
                    'create_date': self._get_vm_create_date(vm),
                    'has_snapshots': len(self._get_vm_snapshots(vm)) > 0,
                    'networks': self._get_vm_networks(vm)
                }
                vm_info_list.append(vm_info)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Informationen für VM {vm.name}: {str(e)}")
        
        logger.info(f"{len(vm_info_list)} VMs erfolgreich gesammelt")
        return vm_info_list
    
    def collect_hosts(self):
        """
        Sammelt Informationen über alle ESXi-Hosts
        
        Returns:
            list: Liste von Host-Informationsdictionaries
        """
        logger.info("Sammle Informationen über ESXi-Hosts...")
        
        hosts = self.client.get_all_hosts()
        host_info_list = []
        
        for host in hosts:
            try:
                # Grundlegende Informationen sammeln
                host_info = {
                    'name': host.name,
                    'connection_state': str(host.runtime.connectionState),
                    'power_state': str(host.runtime.powerState),
                    'maintenance_mode': host.runtime.inMaintenanceMode,
                    'vendor': host.hardware.systemInfo.vendor if host.hardware and host.hardware.systemInfo else 'Unbekannt',
                    'model': host.hardware.systemInfo.model if host.hardware and host.hardware.systemInfo else 'Unbekannt',
                    'cpu_model': host.hardware.cpuPkg[0].description if host.hardware and host.hardware.cpuPkg else 'Unbekannt',
                    'cpu_cores': host.hardware.cpuInfo.numCpuCores if host.hardware and host.hardware.cpuInfo else 0,
                    'cpu_threads': host.hardware.cpuInfo.numCpuThreads if host.hardware and host.hardware.cpuInfo else 0,
                    'memory_size': host.hardware.memorySize if host.hardware else 0,
                    'product_name': host.config.product.name if host.config and host.config.product else 'Unbekannt',
                    'version': host.config.product.version if host.config and host.config.product else 'Unbekannt',
                    'build': host.config.product.build if host.config and host.config.product else 'Unbekannt',
                    'uptime': self._format_uptime(host.runtime.bootTime) if host.runtime and host.runtime.bootTime else 'Unbekannt',
                    'datastores': [ds.name for ds in host.datastore] if host.datastore else [],
                    'networks': [network.name for network in host.network] if host.network else [],
                    'cluster': host.parent.name if host.parent and isinstance(host.parent, vim.ClusterComputeResource) else None
                }
                
                # CPU- und Arbeitsspeicherauslastung berechnen
                if host.summary and host.summary.quickStats:
                    cpu_usage = host.summary.quickStats.overallCpuUsage
                    memory_usage = host.summary.quickStats.overallMemoryUsage
                    
                    if host.hardware and host.hardware.cpuInfo:
                        cpu_total = host.hardware.cpuInfo.hz * host.hardware.cpuInfo.numCpuCores / 1000000  # In MHz
                        cpu_percent = (cpu_usage / cpu_total) * 100 if cpu_total > 0 else 0
                        host_info['cpu_usage_mhz'] = cpu_usage
                        host_info['cpu_total_mhz'] = cpu_total
                        host_info['cpu_usage_percent'] = cpu_percent
                    
                    if host.hardware and host.hardware.memorySize:
                        memory_total_mb = host.hardware.memorySize / (1024 * 1024)  # In MB
                        memory_percent = (memory_usage / memory_total_mb) * 100 if memory_total_mb > 0 else 0
                        host_info['memory_usage_mb'] = memory_usage
                        host_info['memory_total_mb'] = memory_total_mb
                        host_info['memory_usage_percent'] = memory_percent
                
                host_info_list.append(host_info)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Informationen für Host {host.name}: {str(e)}")
        
        logger.info(f"{len(host_info_list)} ESXi-Hosts erfolgreich gesammelt")
        return host_info_list
    
    def collect_datastores(self):
        """
        Sammelt Informationen über alle Datastores
        
        Returns:
            list: Liste von Datastore-Informationsdictionaries
        """
        logger.info("Sammle Informationen über Datastores...")
        
        datastores = self.client.get_all_datastores()
        datastore_info_list = []
        
        for ds in datastores:
            try:
                datastore_info = {
                    'name': ds.name,
                    'type': ds.summary.type if ds.summary else 'Unbekannt',
                    'url': ds.summary.url if ds.summary else None,
                    'capacity': ds.summary.capacity if ds.summary else 0,
                    'free_space': ds.summary.freeSpace if ds.summary else 0,
                    'uncommitted': ds.summary.uncommitted if ds.summary and hasattr(ds.summary, 'uncommitted') else 0,
                    'accessible': ds.summary.accessible if ds.summary else False,
                    'maintenance_mode': ds.summary.maintenanceMode if ds.summary and hasattr(ds.summary, 'maintenanceMode') else 'normal',
                    'hosts': [host.name for host in ds.host] if ds.host else [],
                    'vms': [vm.name for vm in ds.vm] if ds.vm else []
                }
                
                # Prozentsätze berechnen
                if datastore_info['capacity'] > 0:
                    datastore_info['used_space'] = datastore_info['capacity'] - datastore_info['free_space']
                    datastore_info['used_percent'] = (datastore_info['used_space'] / datastore_info['capacity']) * 100
                    datastore_info['free_percent'] = (datastore_info['free_space'] / datastore_info['capacity']) * 100
                    
                    # Human-readable Größen
                    datastore_info['capacity_human'] = humanize.naturalsize(datastore_info['capacity'], binary=True)
                    datastore_info['free_space_human'] = humanize.naturalsize(datastore_info['free_space'], binary=True)
                    datastore_info['used_space_human'] = humanize.naturalsize(datastore_info['used_space'], binary=True)
                
                datastore_info_list.append(datastore_info)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Informationen für Datastore {ds.name}: {str(e)}")
        
        logger.info(f"{len(datastore_info_list)} Datastores erfolgreich gesammelt")
        return datastore_info_list
    
    def collect_networks(self):
        """
        Sammelt Informationen über alle Netzwerke
        
        Returns:
            list: Liste von Netzwerk-Informationsdictionaries
        """
        logger.info("Sammle Informationen über Netzwerke...")
        
        networks = self.client.get_all_networks()
        network_info_list = []
        
        for network in networks:
            try:
                network_info = {
                    'name': network.name,
                    'accessible': network.summary.accessible if network.summary else False
                }
                
                # Unterschiedliche Netzwerktypen behandeln
                if isinstance(network, vim.Network):
                    network_info['type'] = 'Standard Network'
                    network_info['hosts'] = [host.name for host in network.host] if network.host else []
                    network_info['vms'] = [vm.name for vm in network.vm] if network.vm else []
                
                elif isinstance(network, vim.DistributedVirtualPortgroup):
                    network_info['type'] = 'Distributed Virtual Portgroup'
                    network_info['key'] = network.key
                    network_info['switch'] = network.config.distributedVirtualSwitch.name if network.config and network.config.distributedVirtualSwitch else None
                    network_info['vlan'] = network.config.defaultPortConfig.vlan.vlanId if (
                        network.config and 
                        network.config.defaultPortConfig and 
                        network.config.defaultPortConfig.vlan and
                        hasattr(network.config.defaultPortConfig.vlan, 'vlanId')
                    ) else None
                    network_info['vms'] = [vm.name for vm in network.vm] if network.vm else []
                
                network_info_list.append(network_info)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Informationen für Netzwerk {network.name}: {str(e)}")
        
        logger.info(f"{len(network_info_list)} Netzwerke erfolgreich gesammelt")
        return network_info_list
    
    def collect_clusters(self):
        """
        Sammelt Informationen über alle Cluster
        
        Returns:
            list: Liste von Cluster-Informationsdictionaries
        """
        logger.info("Sammle Informationen über Cluster...")
        
        clusters = self.client.get_all_clusters()
        cluster_info_list = []
        
        for cluster in clusters:
            try:
                cluster_info = {
                    'name': cluster.name,
                    'num_hosts': len(cluster.host) if cluster.host else 0,
                    'num_effective_hosts': cluster.summary.numEffectiveHosts if cluster.summary else 0,
                    'total_cpu': cluster.summary.totalCpu if cluster.summary else 0,
                    'total_memory': cluster.summary.totalMemory if cluster.summary else 0,
                    'num_cores_per_cpu': cluster.summary.numCpuCores / cluster.summary.numCpuThreads if (
                        cluster.summary and 
                        cluster.summary.numCpuThreads and 
                        cluster.summary.numCpuCores
                    ) else 0,
                    'drs_enabled': cluster.configuration.drsConfig.enabled if (
                        cluster.configuration and 
                        cluster.configuration.drsConfig
                    ) else False,
                    'drs_automation_level': str(cluster.configuration.drsConfig.defaultVmBehavior) if (
                        cluster.configuration and 
                        cluster.configuration.drsConfig
                    ) else 'Unbekannt',
                    'ha_enabled': cluster.configuration.dasConfig.enabled if (
                        cluster.configuration and 
                        cluster.configuration.dasConfig
                    ) else False,
                    'hosts': [host.name for host in cluster.host] if cluster.host else []
                }
                
                # Ressourcennutzung berechnen
                if cluster.summary:
                    if cluster.summary.totalCpu and cluster.summary.effectiveCpu:
                        cluster_info['cpu_usage_percent'] = (cluster.summary.effectiveCpu / cluster.summary.totalCpu) * 100
                    
                    if cluster.summary.totalMemory and cluster.summary.effectiveMemory:
                        total_memory_mb = cluster.summary.totalMemory / (1024 * 1024)
                        cluster_info['memory_usage_percent'] = (cluster.summary.effectiveMemory / total_memory_mb) * 100
                
                cluster_info_list.append(cluster_info)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Informationen für Cluster {cluster.name}: {str(e)}")
        
        logger.info(f"{len(cluster_info_list)} Cluster erfolgreich gesammelt")
        return cluster_info_list
    
    def collect_resource_pools(self):
        """
        Sammelt Informationen über alle Resource Pools
        
        Returns:
            list: Liste von Resource Pool-Informationsdictionaries
        """
        logger.info("Sammle Informationen über Resource Pools...")
        
        resource_pools = self.client.get_all_resource_pools()
        resource_pool_info_list = []
        
        for pool in resource_pools:
            try:
                resource_pool_info = {
                    'name': pool.name,
                    'cpu_limit': pool.config.cpuAllocation.limit if pool.config and pool.config.cpuAllocation else -1,
                    'cpu_reservation': pool.config.cpuAllocation.reservation if pool.config and pool.config.cpuAllocation else 0,
                    'cpu_expandable_reservation': pool.config.cpuAllocation.expandableReservation if pool.config and pool.config.cpuAllocation else True,
                    'cpu_shares': pool.config.cpuAllocation.shares.shares if pool.config and pool.config.cpuAllocation and pool.config.cpuAllocation.shares else 0,
                    'cpu_shares_level': str(pool.config.cpuAllocation.shares.level) if pool.config and pool.config.cpuAllocation and pool.config.cpuAllocation.shares else 'normal',
                    'memory_limit': pool.config.memoryAllocation.limit if pool.config and pool.config.memoryAllocation else -1,
                    'memory_reservation': pool.config.memoryAllocation.reservation if pool.config and pool.config.memoryAllocation else 0,
                    'memory_expandable_reservation': pool.config.memoryAllocation.expandableReservation if pool.config and pool.config.memoryAllocation else True,
                    'memory_shares': pool.config.memoryAllocation.shares.shares if pool.config and pool.config.memoryAllocation and pool.config.memoryAllocation.shares else 0,
                    'memory_shares_level': str(pool.config.memoryAllocation.shares.level) if pool.config and pool.config.memoryAllocation and pool.config.memoryAllocation.shares else 'normal',
                    'parent': pool.parent.name if pool.parent else None,
                    'vms': [vm.name for vm in pool.vm] if pool.vm else []
                }
                
                resource_pool_info_list.append(resource_pool_info)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Informationen für Resource Pool {pool.name}: {str(e)}")
        
        logger.info(f"{len(resource_pool_info_list)} Resource Pools erfolgreich gesammelt")
        return resource_pool_info_list
    
    def collect_vmware_tools_status(self):
        """
        Sammelt Informationen über den VMware Tools Status aller VMs
        
        Returns:
            list: Liste von VMware Tools-Informationsdictionaries, sortiert nach Alter
        """
        logger.info("Sammle Informationen über VMware Tools-Status...")
        
        vms = self.client.get_all_vms()
        vmware_tools_info_list = []
        
        for vm in vms:
            try:
                # Nur für eingeschaltete VMs relevant
                if vm.runtime.powerState != vim.VirtualMachine.PowerState.poweredOn:
                    continue
                
                tools_status = vm.guest.toolsStatus if vm.guest else 'toolsNotInstalled'
                tools_version = vm.config.tools.toolsVersion if vm.config and vm.config.tools else 0
                tools_version_status = vm.guest.toolsVersionStatus if vm.guest else None
                
                tools_info = {
                    'vm_name': vm.name,
                    'tools_status': str(tools_status) if tools_status else 'Unbekannt',
                    'tools_running_status': str(vm.guest.toolsRunningStatus) if vm.guest and vm.guest.toolsRunningStatus else 'Unbekannt',
                    'tools_version': tools_version,
                    'tools_version_status': str(tools_version_status) if tools_version_status else 'Unbekannt',
                    'guest_os': vm.config.guestFullName if vm.config else 'Unbekannt',
                    'last_boot_time': vm.runtime.bootTime if vm.runtime else None,
                    'host': vm.runtime.host.name if vm.runtime and vm.runtime.host else 'Unbekannt'
                }
                
                # Status für Benutzer lesbar machen
                if tools_status == 'toolsNotInstalled':
                    tools_info['status_description'] = 'Nicht installiert'
                    tools_info['status_severity'] = 'critical'
                elif tools_status == 'toolsNotRunning':
                    tools_info['status_description'] = 'Nicht aktiv'
                    tools_info['status_severity'] = 'warning'
                elif tools_status == 'toolsOld':
                    tools_info['status_description'] = 'Veraltet'
                    tools_info['status_severity'] = 'warning'
                elif tools_status == 'toolsOk':
                    tools_info['status_description'] = 'Aktuell'
                    tools_info['status_severity'] = 'ok'
                else:
                    tools_info['status_description'] = 'Unbekannt'
                    tools_info['status_severity'] = 'warning'
                
                vmware_tools_info_list.append(tools_info)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von VMware Tools-Informationen für VM {vm.name}: {str(e)}")
        
        # Nach letztem Neustart sortieren (älteste zuerst)
        vmware_tools_info_list.sort(key=lambda x: x['last_boot_time'] if x['last_boot_time'] else datetime.now())
        
        logger.info(f"VMware Tools-Status für {len(vmware_tools_info_list)} VMs erfolgreich gesammelt")
        return vmware_tools_info_list
    
    def collect_snapshots(self):
        """
        Sammelt Informationen über alle VM-Snapshots
        
        Returns:
            list: Liste von Snapshot-Informationsdictionaries, sortiert nach Alter (älteste zuerst)
        """
        logger.info("Sammle Informationen über VM-Snapshots...")
        
        vms = self.client.get_all_vms()
        snapshot_info_list = []
        
        for vm in vms:
            try:
                if not vm.snapshot:
                    continue
                
                # Snapshot-Informationen rekursiv sammeln
                snapshots = self._get_vm_snapshots(vm)
                for snapshot in snapshots:
                    snapshot_info_list.append(snapshot)
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von Snapshot-Informationen für VM {vm.name}: {str(e)}")
        
        # Nach Erstellungsdatum sortieren (älteste zuerst)
        snapshot_info_list.sort(key=lambda x: x['create_time'] if x['create_time'] else datetime.now())
        
        logger.info(f"{len(snapshot_info_list)} Snapshots erfolgreich gesammelt")
        return snapshot_info_list
    
    def _format_uptime(self, boot_time):
        """
        Formatiert die Uptime eines Hosts
        
        Args:
            boot_time: Der Zeitpunkt des letzten Bootens
            
        Returns:
            str: Formatierte Uptime (z.B. "10 Tage, 5 Stunden")
        """
        if not boot_time:
            return "Unbekannt"
        
        uptime_delta = datetime.now() - boot_time.replace(tzinfo=None)
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} Tage, {hours} Stunden"
        elif hours > 0:
            return f"{hours} Stunden, {minutes} Minuten"
        else:
            return f"{minutes} Minuten"
    
    def _get_tools_status(self, vm):
        """
        Gibt den VMware Tools Status einer VM zurück
        
        Args:
            vm: Das VM-Objekt
            
        Returns:
            str: Status der VMware Tools
        """
        if not vm.guest:
            return "Unbekannt"
        
        tools_status = vm.guest.toolsStatus
        if tools_status == "toolsNotInstalled":
            return "Nicht installiert"
        elif tools_status == "toolsNotRunning":
            return "Nicht aktiv"
        elif tools_status == "toolsOld":
            return "Veraltet"
        elif tools_status == "toolsOk":
            return "Aktuell"
        else:
            return "Unbekannt"
    
    def _get_tools_version(self, vm):
        """
        Gibt die VMware Tools Version einer VM zurück
        
        Args:
            vm: Das VM-Objekt
            
        Returns:
            str: Version der VMware Tools
        """
        if not vm.config or not vm.config.tools:
            return "Unbekannt"
        
        tools_version = vm.config.tools.toolsVersion
        if not tools_version or tools_version == 0:
            return "Nicht installiert"
        else:
            return str(tools_version)
    
    def _get_vm_disks(self, vm):
        """
        Gibt Informationen über die Festplatten einer VM zurück
        
        Args:
            vm: Das VM-Objekt
            
        Returns:
            list: Liste von Festplatteninformationen
        """
        if not vm.config or not vm.config.hardware or not vm.config.hardware.device:
            return []
        
        disks = []
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualDisk):
                disk_info = {
                    'label': device.deviceInfo.label,
                    'summary': device.deviceInfo.summary,
                    'capacity_bytes': device.capacityInBytes if hasattr(device, 'capacityInBytes') else device.capacityInKB * 1024,
                    'thin_provisioned': device.backing.thinProvisioned if hasattr(device.backing, 'thinProvisioned') else False,
                    'datastore': device.backing.datastore.name if device.backing and device.backing.datastore else "Unbekannt",
                    'filename': device.backing.fileName if device.backing else "Unbekannt"
                }
                disks.append(disk_info)
        
        return disks
    
    def _get_vm_datastores(self, vm):
        """
        Gibt Informationen über die Datastores einer VM zurück
        
        Args:
            vm: Das VM-Objekt
            
        Returns:
            list: Liste von Datastore-Namen
        """
        if not vm.datastore:
            return []
        
        return [ds.name for ds in vm.datastore]
    
    def _get_vm_create_date(self, vm):
        """
        Versucht, das Erstellungsdatum einer VM zu ermitteln
        
        Args:
            vm: Das VM-Objekt
            
        Returns:
            datetime: Erstellungsdatum der VM oder None
        """
        if not vm.config or not vm.config.createDate:
            return None
        
        return vm.config.createDate
    
    def _get_vm_networks(self, vm):
        """
        Gibt Informationen über die Netzwerke einer VM zurück
        
        Args:
            vm: Das VM-Objekt
            
        Returns:
            list: Liste von Netzwerkinformationen
        """
        if not vm.config or not vm.config.hardware or not vm.config.hardware.device:
            return []
        
        networks = []
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualEthernetCard):
                if hasattr(device.backing, 'network') and device.backing.network:
                    network_name = device.backing.network.name
                elif hasattr(device.backing, 'port') and device.backing.port:
                    network_name = device.backing.port.portgroupKey
                else:
                    network_name = "Unbekannt"
                
                network_info = {
                    'name': network_name,
                    'mac_address': device.macAddress if hasattr(device, 'macAddress') else "Unbekannt",
                    'connected': device.connectable.connected if device.connectable else False,
                    'type': type(device).__name__
                }
                networks.append(network_info)
        
        return networks
    
    def _get_vm_snapshots(self, vm):
        """
        Gibt Informationen über die Snapshots einer VM zurück
        
        Args:
            vm: Das VM-Objekt
            
        Returns:
            list: Liste von Snapshot-Informationen
        """
        if not vm.snapshot:
            return []
        
        snapshots = []
        
        def process_snapshot_tree(tree, parent_name=None):
            for snapshot in tree:
                # Größe des Snapshots berechnen (wenn verfügbar)
                size_on_disk = 0
                if hasattr(snapshot, 'layoutEx') and snapshot.layoutEx and snapshot.layoutEx.file:
                    for file in snapshot.layoutEx.file:
                        size_on_disk += file.size
                
                snapshot_info = {
                    'vm_name': vm.name,
                    'name': snapshot.name,
                    'description': snapshot.description if hasattr(snapshot, 'description') else "",
                    'create_time': snapshot.createTime if hasattr(snapshot, 'createTime') else None,
                    'state': str(snapshot.state) if hasattr(snapshot, 'state') else "Unbekannt",
                    'quiesced': snapshot.quiesced if hasattr(snapshot, 'quiesced') else False,
                    'size_on_disk': size_on_disk,
                    'parent': parent_name,
                    'host': vm.runtime.host.name if vm.runtime and vm.runtime.host else "Unbekannt",
                    'datastore': vm.datastore[0].name if vm.datastore else "Unbekannt"
                }
                
                # Alter berechnen
                if snapshot_info['create_time']:
                    age_delta = datetime.now() - snapshot_info['create_time'].replace(tzinfo=None)
                    snapshot_info['age_days'] = age_delta.days
                    
                    # Warnungsstufe basierend auf Alter
                    if age_delta.days > 30:
                        snapshot_info['age_status'] = 'critical'
                    elif age_delta.days > 14:
                        snapshot_info['age_status'] = 'warning'
                    else:
                        snapshot_info['age_status'] = 'ok'
                
                snapshots.append(snapshot_info)
                
                # Kinder rekursiv verarbeiten
                if snapshot.childSnapshotList:
                    process_snapshot_tree(snapshot.childSnapshotList, snapshot.name)
        
        # Snapshot-Baum rekursiv verarbeiten
        if vm.snapshot.rootSnapshotList:
            process_snapshot_tree(vm.snapshot.rootSnapshotList)
        
        return snapshots