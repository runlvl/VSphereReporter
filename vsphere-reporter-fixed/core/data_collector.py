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
from core.enhanced_collector import EnhancedDataCollector
from core.direct_vmdk_collector import collect_orphaned_vmdks as direct_collect_orphaned_vmdks

# Configure the logger
logger = logging.getLogger(__name__)

# Define a filter to suppress error messages during data collection
class SuppressErrorFilter(logging.Filter):
    def filter(self, record):
        # Überprüfen, ob wir im Debug-Modus sind
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        
        # Im Debug-Modus keine Fehler unterdrücken
        if debug_mode:
            return True
        
        # Filtert alle Fehler-Level-Logs und konvertiert sie in Debug-Level-Logs
        if record.levelno >= logging.WARNING:
            # Ändere den Level zu DEBUG
            record.levelno = logging.DEBUG
            record.levelname = 'DEBUG'
            record.msg = f"SUPPRESSED ERROR: {record.msg}"
            # Vollständige Unterdrückung möglich, indem False zurückgegeben wird
            # Wir unterdrücken aber nicht vollständig, damit Entwickler bei Bedarf Logs sehen können
        return True

# Filter nur hinzufügen, wenn nicht im Debug-Modus
if os.environ.get('VSPHERE_REPORTER_DEBUG', '0') != '1':
    logging.getLogger().addFilter(SuppressErrorFilter())
    logger.addFilter(SuppressErrorFilter())
else:
    logger.debug("*** DEBUG MODE ACTIVE - Errors will NOT be suppressed ***")

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
            self.debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
            
        def write(self, message):
            # Im Debug-Modus alles protokollieren, sonst unterdrücken
            if self.debug_mode and message.strip():
                self.logger.log(self.level, f"PyVmomi: {message.strip()}")
            # Im Nicht-Debug-Modus komplett stumm bleiben
            
        def flush(self):
            pass
    
    try:
        # Debug-Modus überprüfen
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        
        if debug_mode:
            # Im Debug-Modus Nachrichten protokollieren, aber Original-Streams beibehalten
            logger.warning("DEBUG MODE: pyVmomi errors will be logged, not suppressed")
            yield
        else:
            # Im Normalbetrieb Ausgaben umleiten und unterdrücken
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
        
    def collect_all_data(self, optional_sections=None):
        """
        Collect all data for reporting
        
        Args:
            optional_sections (dict): Dictionary with boolean flags for optional sections
            
        Returns:
            dict: Dictionary with all collected data
        """
        logger.info("Collecting all data for reporting")
        
        if optional_sections is None:
            optional_sections = {
                'vms': True,
                'hosts': True,
                'datastores': True,
                'clusters': True,
                'resource_pools': True,
                'networks': True
            }
            
        # Pflichtdaten sammeln mit verbesserten V24.3-Methoden
        data = {
            'vmware_tools': self.collect_vmware_tools_info(),
            'snapshots': EnhancedDataCollector.collect_snapshots(self.client),
            'orphaned_vmdks': direct_collect_orphaned_vmdks(self.client)  # Zeigt jetzt ALLE VMDKs an, nicht nur verwaiste
        }
        
        # Optionale Daten je nach Konfiguration sammeln
        if optional_sections.get('vms', False):
            data['vms'] = self.collect_vm_info()
            
        if optional_sections.get('hosts', False):
            data['hosts'] = self.collect_host_info()
            
        if optional_sections.get('datastores', False):
            data['datastores'] = self.collect_datastore_info()
            
        if optional_sections.get('clusters', False):
            data['clusters'] = self.collect_cluster_info()
            
        if optional_sections.get('resource_pools', False):
            data['resource_pools'] = self.collect_resource_pool_info()
            
        if optional_sections.get('networks', False):
            data['networks'] = self.collect_network_info()
            
        logger.info("Data collection completed")
        return data
        
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
                                logger.debug(f"Error getting network info for VM {vm.name}: {str(e)}")
                    vm_info['networks'] = networks
                    
                # Add snapshot information
                if vm.snapshot:
                    snapshots = self._get_vm_snapshots(vm)
                    vm_info['snapshots'] = snapshots
                else:
                    vm_info['snapshots'] = []
                
                vm_info_list.append(vm_info)
            
            except Exception as e:
                # Keine Fehlermeldungen anzeigen - leise im Hintergrund weitermachen
                logger.debug(f"VM collection info silent error: {vm.name}")
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
                # Keine Fehlermeldungen anzeigen - leise im Hintergrund weitermachen
                logger.debug(f"VMware Tools info silent error: {vm.name}")
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
        # Debug-Modus-Check für verbesserte Protokollierung
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        if debug_mode:
            logger.warning("*** SNAPSHOTS COLLECTION - DEBUG MODE ACTIVE ***")
        
        logger.info("Collecting snapshot information")
        
        # In V24.0 - Verbesserte Snapshot-Erkennung mit direktem Content-Browse
        # Anstatt die PropertyCollector zu verwenden, greifen wir direkt auf VMs zu
        # Dies verbessert die Zuverlässigkeit erheblich
        try:
            content = self.client.service_instance.content
            vm_view = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True)
            vms = vm_view.view
            
            if debug_mode:
                logger.warning(f"Found {len(vms)} VMs to check for snapshots")
            
            snapshot_info_list = []
            vm_with_snapshot_count = 0
            
            for vm in vms:
                try:
                    # Ignore templates
                    if vm.config.template:
                        continue
                        
                    # Check if VM has snapshots
                    if vm.snapshot:
                        snapshots = self._get_vm_snapshots(vm)
                        if snapshots:
                            vm_with_snapshot_count += 1
                            snapshot_info_list.extend(snapshots)
                            
                            if debug_mode:
                                logger.warning(f"VM {vm.name} has {len(snapshots)} snapshots")
                except Exception as e:
                    if debug_mode:
                        logger.error(f"Error processing VM {vm.name} for snapshots: {str(e)}")
                    else:
                        logger.debug(f"Error processing VM {vm.name} for snapshots: {str(e)}")
            
            # Sort by create time (oldest first)
            snapshot_info_list.sort(key=lambda x: x['create_time'])
            
            logger.info(f"Found {len(snapshot_info_list)} snapshots across {vm_with_snapshot_count} VMs")
            return snapshot_info_list
            
        except Exception as e:
            if debug_mode:
                import traceback
                logger.error(f"Error accessing VMs for snapshots: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            else:
                logger.debug(f"Error accessing VMs for snapshots: {str(e)}")
            
            # Fallback auf die traditionelle Methode
            logger.warning("Direct VM access failed, using fallback method for snapshots")
            return self._collect_snapshot_info_fallback()
        
        snapshot_info_list = []
        vm_with_snapshot_count = 0
        
        # Ergebnisse verarbeiten
        for obj in result:
            try:
                if not hasattr(obj, 'obj') or not hasattr(obj, 'propSet'):
                    if debug_mode:
                        logger.warning("Found VM result without obj or propSet attributes")
                    continue
                
                vm = obj.obj
                props = {prop.name: prop.val for prop in obj.propSet}
                
                # Templates überspringen
                if 'config.template' in props and props['config.template']:
                    if debug_mode:
                        logger.warning(f"Skipping template VM: {props.get('name', 'Unknown')}")
                    continue
                
                # VM-Name abrufen
                vm_name = props.get('name', 'Unknown VM')
                
                if debug_mode:
                    logger.warning(f"Processing VM: {vm_name}, Properties: {list(props.keys())}")
                    logger.warning(f"Has snapshot property: {'snapshot' in props}")
                    if 'snapshot' in props:
                        logger.warning(f"Snapshot property is None: {props['snapshot'] is None}")
                
                # Snapshots verarbeiten, wenn vorhanden
                if 'snapshot' in props and props['snapshot'] is not None:
                    try:
                        # Auf snapshot-Property und rootSnapshotList zugreifen
                        snapshot_obj = props['snapshot']
                        
                        if debug_mode:
                            logger.warning(f"Snapshot object type: {type(snapshot_obj)}")
                            logger.warning(f"Has rootSnapshotList: {hasattr(snapshot_obj, 'rootSnapshotList')}")
                            if hasattr(snapshot_obj, 'rootSnapshotList'):
                                logger.warning(f"rootSnapshotList length: {len(snapshot_obj.rootSnapshotList)}")
                        
                        if hasattr(snapshot_obj, 'rootSnapshotList') and snapshot_obj.rootSnapshotList:
                            vm_with_snapshot_count += 1
                            snapshots = self._get_snapshot_tree(snapshot_obj.rootSnapshotList)
                            
                            if debug_mode:
                                logger.warning(f"_get_snapshot_tree returned {len(snapshots)} snapshots for VM {vm_name}")
                            
                            for snapshot in snapshots:
                                # VM-Name hinzufügen
                                snapshot['vm_name'] = vm_name
                                # Snapshot-Alter berechnen
                                create_time = snapshot['create_time']
                                age = datetime.datetime.now() - create_time
                                snapshot['age_days'] = age.days
                                snapshot['age_hours'] = age.seconds // 3600
                                # Zusammenfassung für bessere Darstellung
                                snapshot['summary'] = f"{vm_name}: {snapshot['name']} ({age.days} days old)"
                                
                                if debug_mode:
                                    logger.warning(f"Adding snapshot: {snapshot['name']} for VM {vm_name}, created {age.days} days ago")
                                
                                snapshot_info_list.append(snapshot)
                    except Exception as e:
                        if debug_mode:
                            import traceback
                            logger.error(f"Error processing snapshot for VM {vm_name}: {str(e)}")
                            logger.error(f"Traceback: {traceback.format_exc()}")
                        else:
                            logger.debug(f"Error processing snapshot for VM {vm_name}: {str(e)}")
            except Exception as e:
                if debug_mode:
                    import traceback
                    logger.error(f"Error processing VM object: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                else:
                    logger.debug(f"Error processing VM object: {str(e)}")
                continue
        
        # Informiere über die Ergebnisse
        logger.info(f"Found {vm_with_snapshot_count} VMs with snapshots")
        logger.info(f"Found {len(snapshot_info_list)} total snapshots")
        
        if debug_mode:
            logger.warning(f"DEBUG: Found {vm_with_snapshot_count} VMs with snapshots")
            logger.warning(f"DEBUG: Found {len(snapshot_info_list)} total snapshots")
        
        # KRITISCHE ÄNDERUNG: Fallback IMMER ausführen, wenn keine Snapshots gefunden wurden
        if not snapshot_info_list:
            logger.warning("No snapshots found using PropertyCollector, trying fallback method")
            fallback_snapshots = self._collect_snapshot_info_fallback()
            
            if debug_mode:
                logger.warning(f"Fallback method returned {len(fallback_snapshots)} snapshots")
                
            return fallback_snapshots
        
        # Nach Erstellzeit sortieren (älteste zuerst)
        try:
            snapshot_info_list.sort(key=lambda x: x['create_time'], reverse=False)
        except Exception as sort_err:
            if debug_mode:
                logger.error(f"Error sorting snapshots: {str(sort_err)}")
            else:
                logger.warning(f"Error sorting snapshots: {str(sort_err)}")
        
        return snapshot_info_list
        
    def _collect_snapshot_info_fallback(self):
        """
        Fallback-Methode zur Snapshot-Sammlung, verwendet den alten Ansatz
        """
        logger.info("Using fallback method for snapshot collection")
        vms = self.client.get_virtual_machines()
        
        snapshot_info_list = []
        for vm in vms:
            try:
                # Fehlermeldungen unterdrücken
                with suppress_stdout_stderr():
                    # Direkt alle verfügbaren Daten abfragen
                    if hasattr(vm, 'snapshot') and vm.snapshot:
                        logger.debug(f"Found VM with snapshots: {vm.name}")
                        if hasattr(vm.snapshot, 'rootSnapshotList'):
                            snapshots = self._get_snapshot_tree(vm.snapshot.rootSnapshotList)
                            for snapshot in snapshots:
                                # Zusätzliche Informationen hinzufügen
                                snapshot['vm_name'] = vm.name
                                # Snapshot-Alter berechnen
                                create_time = snapshot['create_time']
                                age = datetime.datetime.now() - create_time
                                snapshot['age_days'] = age.days
                                snapshot['age_hours'] = age.seconds // 3600
                                
                                snapshot_info_list.append(snapshot)
            except Exception as e:
                logger.debug(f"Snapshot fallback collection error for VM {vm.name}: {str(e)}")
                continue
                
        snapshot_info_list.sort(key=lambda x: x['create_time'], reverse=False)
        logger.info(f"Fallback method found {len(snapshot_info_list)} snapshots")
        
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
        
        # Verbesserte Snapshot-Erkennung mit Fehlerbehandlung
        try:
            if vm.snapshot and hasattr(vm.snapshot, 'rootSnapshotList') and vm.snapshot.rootSnapshotList:
                # Direkter Zugriff auf alle Snapshots, auch wenn sie in Hierarchien verschachtelt sind
                snapshot_list = self._get_snapshot_tree(vm.snapshot.rootSnapshotList)
                for snapshot in snapshot_list:
                    try:
                        # Calculate snapshot age
                        create_time = snapshot['create_time']
                        age = datetime.datetime.now() - create_time
                        
                        # Add age in days
                        snapshot['age_days'] = age.days
                        snapshot['age_hours'] = age.seconds // 3600
                        
                        # Mehr Details hinzufügen
                        snapshot['vm_summary'] = f"{vm.name}: {snapshot['name']} ({snapshot['age_days']} days old)"
                        
                        snapshot_info.append(snapshot)
                    except Exception as e:
                        logger.debug(f"Error processing individual snapshot: {str(e)}")
                        continue
        except Exception as e:
            logger.debug(f"Error accessing snapshots from VM {vm.name}: {str(e)}")
            # Versuchen, über die Property-Collector API zu gehen als Fallback
            try:
                # Alternativer Ansatz über MoRef-basierte Suche
                if hasattr(vm, '_moId'):
                    logger.debug(f"Trying alternative snapshot retrieval for VM {vm.name}")
                    # Dieser Ansatz über die PropertyCollector API könnte Ergebnisse liefern, 
                    # wenn der direkte Zugriff fehlschlägt
            except Exception:
                pass
                
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
        # Debug-Modus-Check für verbesserte Protokollierung
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        if debug_mode:
            logger.warning("*** ORPHANED VMDKs COLLECTION - DEBUG MODE ACTIVE ***")
        
        logger.info("Collecting orphaned VMDK information")
        
        # Erste direkte Abfrage von VM-Daten über Property Collector für bessere Zuverlässigkeit
        # Get all registered VMDKs using PropertyCollector
        content = self.client.service_instance.content
        registered_vmdks = set()
        
        # PropertyCollector Setup
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True)
            
        property_spec = vim.PropertySpec()
        property_spec.type = vim.VirtualMachine
        property_spec.pathSet = [
            'name',
            'config.hardware.device',
            'config.template'
        ]
        
        traversal_spec = vim.TraversalSpec()
        traversal_spec.name = 'traverseEntities'
        traversal_spec.path = 'view'
        traversal_spec.skip = False
        traversal_spec.type = type(container)
        
        obj_spec = vim.ObjectSpec()
        obj_spec.obj = container
        obj_spec.skip = True
        obj_spec.selectSet = [traversal_spec]
        
        filter_spec = vim.PropertyFilterSpec()
        filter_spec.objectSet = [obj_spec]
        filter_spec.propSet = [property_spec]
        
        # Abrufen der VM-Properties mit einer direkten Anfrage
        try:
            logger.info("Retrieving VM disk information using PropertyCollector")
            vm_properties = content.propertyCollector.RetrieveContents([filter_spec])
            
            if debug_mode:
                logger.warning(f"PropertyCollector returned {len(vm_properties)} VM properties")
            
            # Properties verarbeiten und registrierte VMDKs sammeln
            for vm_property in vm_properties:
                if not hasattr(vm_property, 'obj') or not hasattr(vm_property, 'propSet'):
                    if debug_mode:
                        logger.warning("Found VM property without obj or propSet attributes")
                    continue
                    
                props = {prop.name: prop.val for prop in vm_property.propSet}
                
                # Überspringe Templates
                if 'config.template' in props and props['config.template']:
                    if debug_mode:
                        logger.warning(f"Skipping template VM: {props.get('name', 'Unknown')}")
                    continue
                    
                # VM-Name für Logging
                vm_name = props.get('name', 'Unknown VM')
                
                if debug_mode:
                    logger.warning(f"Processing VM: {vm_name}, Properties: {list(props.keys())}")
                
                # Hardware-Devices durchgehen
                if 'config.hardware.device' in props:
                    devices = props['config.hardware.device']
                    disk_count = 0
                    for device in devices:
                        try:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                disk_count += 1
                                if hasattr(device, 'backing') and hasattr(device.backing, 'fileName'):
                                    # Datastore-Pfad abrufen
                                    datastore_path = device.backing.fileName
                                    registered_vmdks.add(datastore_path)
                                    
                                    # Normalisierte Pfade für besseren Vergleich
                                    normalized_path = datastore_path.lower().strip()
                                    registered_vmdks.add(normalized_path)
                                    
                                    # Pfade ohne Datastore-Klammern
                                    if normalized_path.startswith('['):
                                        parts = normalized_path.split('] ', 1)
                                        if len(parts) > 1:
                                            registered_vmdks.add(parts[1])
                                    
                                    if debug_mode:
                                        logger.warning(f"Registered VMDK: {datastore_path}")
                        except Exception as e:
                            if debug_mode:
                                logger.error(f"Error processing virtual disk for VM {vm_name}: {str(e)}")
                            else:
                                logger.debug(f"Error processing virtual disk for VM {vm_name}: {str(e)}")
                    
                    if debug_mode:
                        logger.warning(f"VM {vm_name} has {disk_count} disk(s)")
                            
        except Exception as e:
            if debug_mode:
                import traceback
                logger.error(f"Error using PropertyCollector for disk info: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            else:
                logger.debug(f"Error using PropertyCollector for disk info: {str(e)}")
            
            # Fallback auf den alten Ansatz
            return self._collect_orphaned_vmdks_fallback()
            
        # Wenn keine VMDKs über PropertyCollector gefunden wurden, Fallback verwenden
        if not registered_vmdks:
            logger.warning("No registered VMDKs found with PropertyCollector, using fallback")
            return self._collect_orphaned_vmdks_fallback()
            
        if debug_mode:
            logger.warning(f"Found {len(registered_vmdks)} registered VMDKs")
            
        logger.info(f"Found {len(registered_vmdks)} registered VMDKs")
        
        # Ergebnis-Liste für orphaned VMDKs
        orphaned_vmdks = []
        
        try:
            # Alle Datastores für die Suche nach VMDKs abrufen
            datastores = self.client.get_datastores()
            
            for datastore in datastores:
                try:
                    # Überspringe Datastores ohne Browser
                    if not hasattr(datastore, 'browser'):
                        continue
                        
                    # Such-Spezifikation für VMDK-Dateien erstellen
                    search_spec = vim.host.DatastoreBrowser.SearchSpec()
                    search_spec.matchPattern = ["*.vmdk"]  # Alle VMDKs suchen
                    search_spec.details = vim.host.DatastoreBrowser.FileInfo.Details()
                    search_spec.details.fileSize = True
                    search_spec.details.fileType = True
                    search_spec.details.modification = True
                    
                    # Datastore durchsuchen
                    browser = datastore.browser
                    search_task = browser.SearchDatastoreSubFolders_Task(
                        datastorePath=f"[{datastore.name}]",
                        searchSpec=search_spec
                    )
                    
                    # Warten auf Abschluss der Suche
                    search_results = self.client.service_instance.content.taskManager.WaitForTask(search_task)
                    
                    # Suchergebnisse verarbeiten
                    if hasattr(search_results, 'info') and hasattr(search_results.info, 'result'):
                        for result in search_results.info.result:
                            # Jeden gefundenen Ordner verarbeiten
                            folder_path = result.folderPath
                            
                            for file_info in result.file:
                                # Nur VMDK-Dateien berücksichtigen
                                if not file_info.path.lower().endswith('.vmdk'):
                                    continue
                                    
                                # Vollständigen Pfad erstellen
                                full_path = folder_path
                                if not full_path.endswith('/'):
                                    full_path += '/'
                                full_path += file_info.path
                                
                                # Normalisierter Pfad für Vergleiche
                                normalized_path = full_path.lower().strip()
                                
                                # Prüfen, ob die VMDK registriert ist
                                if (full_path in registered_vmdks or 
                                    normalized_path in registered_vmdks):
                                    continue
                                    
                                # Ohne Datastore-Klammern prüfen
                                if normalized_path.startswith('['):
                                    parts = normalized_path.split('] ', 1)
                                    if len(parts) > 1 and parts[1] in registered_vmdks:
                                        continue
                                
                                # Diese VMDK ist nicht registriert, potenziell orphaned
                                # Überprüfen, ob es eine Hilfs-VMDK ist (delta, flat, ctk)
                                is_helper_vmdk = False
                                for suffix in ['-ctk.vmdk']:
                                    if normalized_path.endswith(suffix):
                                        is_helper_vmdk = True
                                        break
                                        
                                if is_helper_vmdk:
                                    continue
                                    
                                # Diese VMDK ist nicht registriert und kein Hilfs-VMDK,
                                # also ist sie wahrscheinlich orphaned
                                reason = "Not registered to any VM"
                                
                                # Weitere Überprüfungen für eine genauere Begründung
                                if '/forgotten/' in normalized_path or '/lost+found/' in normalized_path:
                                    reason = "Located in a system recovery folder"
                                elif self._is_vmdk_orphaned(folder_path, file_info.path):
                                    reason = "No associated VM configuration files found"
                                elif '-flat.vmdk' in normalized_path or '-delta.vmdk' in normalized_path:
                                    # Rekonstruiere Basis-VMDK-Namen
                                    base_path = normalized_path
                                    if '-flat.vmdk' in base_path:
                                        base_path = base_path.replace('-flat.vmdk', '.vmdk')
                                    elif '-delta.vmdk' in base_path:
                                        base_path = base_path.replace('-delta.vmdk', '.vmdk')
                                        
                                    if base_path not in registered_vmdks:
                                        reason = "Base disk is not associated with any VM"
                                    else:
                                        # Wenn Basis registriert ist, ist dies keine orphaned VMDK
                                        continue
                                
                                # Diese VMDK ist orphaned, füge sie zur Ergebnisliste hinzu
                                orphan_info = {
                                    'path': full_path,
                                    'datastore': datastore.name,
                                    'size': file_info.fileSize,
                                    'modification_time': file_info.modification,
                                    'reason': reason
                                }
                                orphaned_vmdks.append(orphan_info)
                                
                except Exception as e:
                    logger.debug(f"Error scanning datastore {datastore.name} for orphaned VMDKs: {str(e)}")
                    continue
                    
            logger.info(f"Found {len(orphaned_vmdks)} orphaned VMDKs")
            
            # Wenn keine orphaned VMDKs gefunden wurden, obwohl genügend registrierte VMDKs vorhanden sind,
            # versuche es mit dem Fallback-Ansatz (für Konsistenz und um sicherzustellen, dass nichts übersehen wurde)
            if not orphaned_vmdks and len(registered_vmdks) > 5:
                logger.debug("No orphaned VMDKs found with PropertyCollector approach, trying fallback")
                fallback_orphans = self._collect_orphaned_vmdks_fallback()
                if fallback_orphans:
                    logger.info(f"Fallback found {len(fallback_orphans)} orphaned VMDKs")
                    return fallback_orphans
                    
            return orphaned_vmdks
            
        except Exception as e:
            logger.debug(f"Error in orphaned VMDK collection: {str(e)}")
            # Fallback verwenden, wenn ein schwerwiegender Fehler auftritt
            return self._collect_orphaned_vmdks_fallback()
            
    def _collect_orphaned_vmdks_fallback(self):
        """
        Fallback-Methode zur Sammlung von orphaned VMDKs, verwendet den alten Ansatz
        """
        logger.info("Using fallback method for orphaned VMDK collection")
        
        # Registrierte VMDKs mit traditionellem Ansatz sammeln
        registered_vmdks = set()
        vms = self.client.get_virtual_machines()
        
        # Überspringe die Fehlerfilterung und protokolliere aggressiver, um Probleme zu erkennen
        for vm in vms:
            try:
                if vm.config and vm.config.hardware and vm.config.hardware.device:
                    logger.debug(f"Processing VM: {vm.name}")
                    # Überspringe Templates
                    if vm.config.template:
                        logger.debug(f"Skipping template VM: {vm.name}")
                        continue
                        
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualDisk):
                            try:
                                datastore_path = device.backing.fileName
                                registered_vmdks.add(datastore_path)
                                # Auch normalisierte Version hinzufügen
                                registered_vmdks.add(datastore_path.lower().strip())
                                logger.debug(f"Registered VMDK: {datastore_path}")
                            except Exception as device_e:
                                logger.debug(f"Error processing device for VM {vm.name}: {str(device_e)}")
            except Exception as vm_e:
                logger.debug(f"Error processing VM {vm.name if hasattr(vm, 'name') else 'unknown'}: {str(vm_e)}")
                
        orphaned_vmdks = []
        datastores = self.client.get_datastores()
        
        # Alle Datastores nach VMDKs durchsuchen
        for datastore in datastores:
            try:
                if not hasattr(datastore, 'browser'):
                    continue
                    
                search_spec = vim.host.DatastoreBrowser.SearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                search_spec.details = vim.host.DatastoreBrowser.FileInfo.Details()
                search_spec.details.fileSize = True
                search_spec.details.fileType = True
                search_spec.details.modification = True
                
                logger.debug(f"Searching datastore: {datastore.name}")
                search_task = datastore.browser.SearchDatastoreSubFolders_Task(
                    datastorePath=f"[{datastore.name}]",
                    searchSpec=search_spec
                )
                
                search_results = self.client.service_instance.content.taskManager.WaitForTask(search_task)
                
                if hasattr(search_results, 'info') and hasattr(search_results.info, 'result'):
                    for result in search_results.info.result:
                        for file_info in result.file:
                            try:
                                # Vollständigen Pfad erstellen
                                path = result.folderPath
                                if not path.endswith('/'):
                                    path += '/'
                                path += file_info.path
                                
                                # Nicht-VMDK-Dateien überspringen
                                if not path.lower().endswith('.vmdk'):
                                    continue
                                    
                                # Nur CTK-Dateien überspringen, andere beibehalten
                                if '-ctk.vmdk' in path.lower():
                                    continue
                                    
                                # Prüfen, ob die VMDK registriert ist
                                if path in registered_vmdks or path.lower().strip() in registered_vmdks:
                                    continue
                                    
                                # Nicht registrierte VMDK gefunden - überprüfen, ob orphaned
                                logger.debug(f"Found non-registered VMDK: {path}")
                                
                                # Zusätzliche Checks für orphaned Status
                                reason = "Not associated with any VM"
                                
                                # Check 1: In Recovery-Verzeichnis?
                                if '/forgotten/' in path.lower() or '/lost+found/' in path.lower():
                                    reason = "Located in a system recovery folder"
                                # Check 2: Keine VMX-Datei vorhanden?
                                elif self._is_vmdk_orphaned(result.folderPath, file_info.path):
                                    reason = "No associated VM configuration files found"
                                # Check 3: Flat/Delta-Dateien ohne registrierte Basis?
                                elif '-flat.vmdk' in path.lower() or '-delta.vmdk' in path.lower():
                                    base_path = path.lower()
                                    if '-flat.vmdk' in base_path:
                                        base_path = base_path.replace('-flat.vmdk', '.vmdk')
                                    elif '-delta.vmdk' in base_path:
                                        base_path = base_path.replace('-delta.vmdk', '.vmdk')
                                        
                                    if base_path not in registered_vmdks:
                                        reason = "Base disk not registered to any VM"
                                    else:
                                        # Wenn Basis registriert ist, ist dies keine orphaned VMDK
                                        continue
                                
                                # Diese VMDK ist definitiv orphaned
                                logger.debug(f"Found orphaned VMDK: {path}, reason: {reason}")
                                orphan_info = {
                                    'path': path,
                                    'datastore': datastore.name,
                                    'size': file_info.fileSize,
                                    'modification_time': file_info.modification,
                                    'reason': reason
                                }
                                orphaned_vmdks.append(orphan_info)
                            except Exception as file_e:
                                logger.debug(f"Error processing file {file_info.path}: {str(file_e)}")
            except Exception as ds_e:
                logger.debug(f"Error scanning datastore {datastore.name}: {str(ds_e)}")
                
        logger.info(f"Fallback method found {len(orphaned_vmdks)} orphaned VMDKs")
        return orphaned_vmdks
        
    def _is_vmdk_orphaned(self, folder_path, vmdk_name):
        """
        Check if a VMDK file is orphaned by looking for associated VM files
        
        Definition: Eine VMDK ist orphaned, wenn sie keiner VM zugeordnet ist UND kein Template ist.
        
        Args:
            folder_path (str): Datastore folder path
            vmdk_name (str): VMDK file name
            
        Returns:
            bool: True if the VMDK appears to be orphaned
        """
        try:
            # Extrahiere VM-Namen aus dem VMDK-Dateinamen (entferne Erweiterung)
            # Berücksichtige verschiedene Namensmuster
            vm_name = vmdk_name
            if vm_name.endswith('.vmdk'):
                vm_name = vm_name[:-5]
                
            # Spezielle Behandlung für -delta und -flat VMDKs
            for pattern in ['-delta', '-flat', '-ctk', '-000']:
                if pattern in vm_name:
                    # Entferne das Suffix um den Basis-VM-Namen zu erhalten
                    parts = vm_name.split(pattern, 1)
                    if parts:
                        vm_name = parts[0]
                        break
            
            # Prüfe, ob ein Datastore im Pfad angegeben ist
            datastore_match = re.match(r'\[(.*?)\]', folder_path)
            if not datastore_match:
                logger.debug(f"Could not extract datastore name from path: {folder_path}")
                return True  # Im Zweifelsfall als orphaned betrachten
                
            datastore = datastore_match.group(1)
            browser = None
            
            # Finde den Datastore-Browser
            datastores = self.client.get_datastores()
            for ds in datastores:
                if ds.name == datastore:
                    browser = ds.browser
                    break
                    
            if browser is None:
                logger.debug(f"Could not find browser for datastore: {datastore}")
                return True  # Im Zweifelsfall als orphaned betrachten
            
            # 1. Prüfen, ob VMX-Datei existiert (zur Erkennung vorhandener VMs)
            vmx_search_spec = vim.host.DatastoreBrowser.SearchSpec()
            
            # Erweitere die Suche auf mögliche Varianten des VMX-Namens
            vmx_patterns = [f"{vm_name}.vmx"]
            # Wenn der Name Sonderzeichen enthält, versuche es ohne sie
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', vm_name)
            if clean_name != vm_name:
                vmx_patterns.append(f"{clean_name}.vmx")
            
            # Wenn der Name mit Nummern oder speziellen Markierungen endet, versuche es ohne sie
            base_name = re.sub(r'[0-9_-]+$', '', vm_name)
            if base_name != vm_name and len(base_name) > 3:  # Mindestens 3 Zeichen, um sinnvolle Namen zu haben
                vmx_patterns.append(f"{base_name}.vmx")
                
            vmx_search_spec.matchPattern = vmx_patterns
            
            # Suche nach VMX-Dateien im gleichen Ordner
            vmx_search_task = browser.SearchDatastore_Task(
                datastorePath=folder_path,
                searchSpec=vmx_search_spec
            )
            
            vmx_results = self.client.service_instance.content.taskManager.WaitForTask(vmx_search_task)
            vmx_exists = False
            
            if hasattr(vmx_results, 'info') and hasattr(vmx_results.info, 'result'):
                if len(vmx_results.info.result.file) > 0:
                    vmx_exists = True
            
            # Falls keine VMX im gleichen Ordner gefunden wurde, suche im übergeordneten Ordner
            if not vmx_exists:
                # Bestimme übergeordneten Ordner
                parent_folder = folder_path
                if parent_folder.endswith('/'):
                    parent_folder = parent_folder[:-1]
                    
                # Entferne letzten Pfadteil, um zum übergeordneten Ordner zu gelangen
                if '/' in parent_folder:
                    parent_folder = parent_folder.rsplit('/', 1)[0]
                    
                    # Suche nach VMX-Dateien im übergeordneten Ordner
                    parent_vmx_search_task = browser.SearchDatastore_Task(
                        datastorePath=parent_folder,
                        searchSpec=vmx_search_spec
                    )
                    
                    parent_vmx_results = self.client.service_instance.content.taskManager.WaitForTask(parent_vmx_search_task)
                    
                    if hasattr(parent_vmx_results, 'info') and hasattr(parent_vmx_results.info, 'result'):
                        if len(parent_vmx_results.info.result.file) > 0:
                            vmx_exists = True
            
            # 2. Prüfen, ob es ein Template ist (zur Erkennung von Templates)
            is_template = False
            is_registered = False
            
            # 2a. Erweiterte Prüfung auch auf VM-Registrierung (nicht nur Templates)
            vms = self.client.get_virtual_machines()
            for vm in vms:
                with suppress_stdout_stderr():
                    try:
                        # Vergleiche den Dateinamen auf verschiedene Arten mit VM-Namen
                        # Dieser Vergleich ist robuster gegenüber Formatierungsunterschieden
                        vm_base_name = vm.name.lower()
                        vmdk_base_name = vm_name.lower()
                        
                        # Direkter Namensvergleich
                        if vm_base_name == vmdk_base_name:
                            is_registered = True
                            # Prüfe, ob es sich um ein Template handelt
                            if vm.config and vm.config.template:
                                is_template = True
                            break
                        
                        # Teilweiser Namensvergleich (wenn VMDK Teil eines VM-Namens ist)
                        if vmdk_base_name in vm_base_name or vm_base_name in vmdk_base_name:
                            # Prüfe auch, ob die VM diese VMDK tatsächlich enthält
                            if hasattr(vm, 'config') and vm.config and vm.config.hardware:
                                for device in vm.config.hardware.device:
                                    if isinstance(device, vim.vm.device.VirtualDisk) and hasattr(device.backing, 'fileName'):
                                        if vmdk_name.lower() in device.backing.fileName.lower():
                                            is_registered = True
                                            if vm.config.template:
                                                is_template = True
                                            break
                    except:
                        continue
            
            # Eine VMDK ist orphaned, wenn:
            # 1. Keine VMX-Datei existiert, ODER
            # 2. Sie keiner VM zugeordnet und kein Template ist
            if not vmx_exists:
                logger.debug(f"No VMX file found for {vmdk_name}, marking as orphaned")
                return True  # Keine VMX-Datei gefunden, eindeutig orphaned
            elif not is_registered:
                logger.debug(f"VMX exists for {vmdk_name} but no matching registered VM found, marking as orphaned")
                return True  # VMX existiert, aber keine registrierte VM gefunden
            elif not is_template:
                # Es existiert eine registrierte VM, aber es ist kein Template
                # Hier können wir konservativer sein und die VMDK nur als orphaned betrachten, 
                # wenn weitere Bedingungen erfüllt sind
                
                # In diesem Fall: Wenn es eine registrierte VM gibt, die nicht als Template markiert ist,
                # ist die Disk wahrscheinlich in Benutzung
                return False
                
            return False

        except Exception as e:
            logger.debug(f"Error checking orphaned status for {vmdk_name}: {str(e)}")
            # Im Fehlerfall konservativ sein und nicht als orphaned markieren
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
                logger.debug(f"Error collecting info for host {host.name}: {str(e)}")
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
                logger.debug(f"Error collecting info for datastore {datastore.name}: {str(e)}")
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
                logger.debug(f"Error collecting info for cluster {cluster.name}: {str(e)}")
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
                logger.debug(f"Error collecting info for resource pool {pool.name}: {str(e)}")
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
                logger.debug(f"Error collecting info for network {network.name}: {str(e)}")
                continue
                
        return network_info_list
