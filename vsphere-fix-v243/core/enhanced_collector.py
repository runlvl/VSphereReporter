#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced data collection methods for VMware vSphere Reporter v24.3
"""

import os
import re
import logging
import datetime
from pyVmomi import vim

# Logger konfigurieren
logger = logging.getLogger(__name__)

class EnhancedDataCollector:
    """
    Verbesserte Datensammelmethoden für v24.3 zur Behebung von Problemen mit
    fehlenden Snapshots und verwaisten VMDK-Dateien
    """
    
    @staticmethod
    def collect_snapshots(client):
        """
        Verbesserte Methode zur Sammlung von VM-Snapshots
        
        Args:
            client: Der VSphereClient
            
        Returns:
            list: Liste von Snapshot-Informationen, sortiert nach Alter (älteste zuerst)
        """
        # Debug-Modus-Check für verbesserte Protokollierung
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        if debug_mode:
            logger.warning("*** ENHANCED SNAPSHOTS COLLECTION - V24.3 ***")
        
        logger.info("Using enhanced v24.3 snapshot collection")
        
        try:
            # Direkter Zugriff auf alle VMs über Content Browser
            content = client.service_instance.content
            vm_view = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True)
            vms = vm_view.view
            
            if debug_mode:
                logger.warning(f"Found {len(vms)} VMs to check for snapshots")
            
            snapshot_info_list = []
            vm_with_snapshot_count = 0
            
            for vm in vms:
                try:
                    # Templates überspringen
                    if vm.config.template:
                        continue
                        
                    # Prüfen, ob VM Snapshots hat
                    if vm.snapshot:
                        # Zuverlässige Methode zur Snapshot-Traversierung
                        if hasattr(vm.snapshot, 'rootSnapshotList'):
                            snapshots = EnhancedDataCollector._get_snapshot_tree(vm, vm.snapshot.rootSnapshotList)
                            if snapshots:
                                vm_with_snapshot_count += 1
                                snapshot_info_list.extend(snapshots)
                                
                                if debug_mode:
                                    logger.warning(f"VM {vm.name} has {len(snapshots)} snapshots")
                except Exception as e:
                    if debug_mode:
                        logger.error(f"Error processing VM {vm.name if hasattr(vm, 'name') else 'Unknown'} for snapshots: {str(e)}")
                    continue
            
            # Nach Erstellzeit sortieren (älteste zuerst)
            snapshot_info_list.sort(key=lambda x: x['create_time'])
            
            logger.info(f"Enhanced method found {len(snapshot_info_list)} snapshots across {vm_with_snapshot_count} VMs")
            return snapshot_info_list
            
        except Exception as e:
            if debug_mode:
                import traceback
                logger.error(f"Error in enhanced snapshot collection: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            else:
                logger.debug(f"Error in enhanced snapshot collection: {str(e)}")
            
            # Leere Liste zurückgeben bei Fehlern
            return []
    
    @staticmethod
    def _get_snapshot_tree(vm, snapshots):
        """
        Rekursive Verarbeitung des Snapshot-Baums
        
        Args:
            vm: Die VM
            snapshots: Liste von Snapshot-Objekten
            
        Returns:
            list: Verarbeitete Liste von Snapshot-Informationen
        """
        snapshot_data = []
        for snapshot in snapshots:
            try:
                # Basisdaten sammeln
                snap_info = {
                    'name': snapshot.name,
                    'description': snapshot.description,
                    'create_time': snapshot.createTime,
                    'state': snapshot.state,
                    'snapshot_id': snapshot.id,
                    'quiesced': snapshot.quiesced,
                    'vm_name': vm.name
                }
                
                # Alter berechnen
                create_time = snapshot.createTime
                
                # BUGFIX v24.1: Verbesserte Lösung für "can't subtract offset-naive and offset-aware datetimes"
                # Stelle sicher, dass beide Datumswerte entweder mit oder ohne Zeitzoneninformationen sind
                # Immer UTC für konsistente Berechnungen verwenden
                now = datetime.datetime.now(datetime.timezone.utc)
                
                # Prüfen, ob create_time Zeitzoneninformation enthält
                if create_time.tzinfo is not None:
                    # create_time hat bereits Zeitzone
                    # Für zuverlässige Berechnung zur UTC konvertieren
                    try:
                        # Versuch die Zeit in UTC zu konvertieren
                        create_time = create_time.astimezone(datetime.timezone.utc)
                    except Exception as e:
                        logger.debug(f"Zeitzonenkonvertierung fehlgeschlagen: {str(e)}")
                        # Falls Konvertierung fehlschlägt, behalte die Zeit und verwende die gleiche Zeitzone für now
                        now = now.astimezone(create_time.tzinfo)
                else:
                    # create_time hat keine Zeitzone, füge UTC hinzu für korrekte Berechnung
                    # Dies ist besser als die Zeitzone zu entfernen, da die Berechnung präziser ist
                    create_time = create_time.replace(tzinfo=datetime.timezone.utc)
                
                # Jetzt ist es sicher, die Subtraktion durchzuführen
                age = now - create_time
                snap_info['age_days'] = age.days
                snap_info['age_hours'] = age.seconds // 3600
                
                # Zusammenfassung für bessere Darstellung
                snap_info['summary'] = f"{vm.name}: {snapshot.name} ({age.days} days old)"
                
                snapshot_data.append(snap_info)
                
                # Verarbeite untergeordnete Snapshots
                if snapshot.childSnapshotList:
                    snapshot_data.extend(EnhancedDataCollector._get_snapshot_tree(vm, snapshot.childSnapshotList))
            except Exception as e:
                logger.debug(f"Error processing individual snapshot: {str(e)}")
                continue
                
        return snapshot_data
    
    @staticmethod
    def collect_orphaned_vmdks(client):
        """
        Verbesserte Methode zur Sammlung von verwaisten VMDK-Dateien (v24.3)
        
        Args:
            client: Der VSphereClient
            
        Returns:
            list: Liste von verwaisten VMDK-Informationen
        """
        # Debug-Modus-Check für verbesserte Protokollierung
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        if debug_mode:
            logger.warning("*** ENHANCED ORPHANED VMDK COLLECTION - V24.3 ***")
        
        logger.info("Using enhanced v24.3 orphaned VMDK collection")
        
        orphaned_vmdks = []
        
        try:
            # Service-Instanz und Content abrufen
            content = client.service_instance.content
            
            # ------ SCHRITT 1: Alle registrierten VMDKs sammeln ------
            registered_vmdks = set()
            
            try:
                # Container-View für VMs erstellen
                vm_view = content.viewManager.CreateContainerView(
                    content.rootFolder, [vim.VirtualMachine], True)
                vms = vm_view.view
                
                # Jede VM durchlaufen
                for vm in vms:
                    try:
                        # Templates überspringen
                        if vm.config.template:
                            continue
                            
                        # Alle virtuellen Disks der VM sammeln
                        if vm.config and vm.config.hardware and vm.config.hardware.device:
                            for device in vm.config.hardware.device:
                                if isinstance(device, vim.vm.device.VirtualDisk):
                                    if hasattr(device.backing, 'fileName'):
                                        # VMDK-Pfad zur Liste hinzufügen
                                        disk_path = device.backing.fileName
                                        registered_vmdks.add(disk_path)
                                        registered_vmdks.add(disk_path.lower())
                                        
                                        # Pfad ohne Datastore-Klammern
                                        match = re.match(r'^\[(.*?)\] (.*)', disk_path)
                                        if match:
                                            path_without_ds = match.group(2)
                                            registered_vmdks.add(path_without_ds)
                                            registered_vmdks.add(path_without_ds.lower())
                                        
                                        if debug_mode:
                                            logger.warning(f"Registered VMDK: {disk_path}")
                    except Exception as vm_ex:
                        if debug_mode:
                            logger.error(f"Error processing VM {vm.name if hasattr(vm, 'name') else 'Unknown'}: {str(vm_ex)}")
                        continue
                
                if debug_mode:
                    logger.warning(f"Total registered VMDKs: {len(registered_vmdks)}")
                    
            except Exception as vm_list_ex:
                if debug_mode:
                    logger.error(f"Error collecting registered VMDKs: {str(vm_list_ex)}")
                    
            # ------ SCHRITT 2: Datacenters und Datastores durchsuchen ------
            try:
                # Alle Datacenters abrufen
                datacenters = [entity for entity in content.rootFolder.childEntity 
                            if isinstance(entity, vim.Datacenter)]
                
                if debug_mode:
                    logger.warning(f"Found {len(datacenters)} datacenters to scan")
                
                # Jedes Datacenter durchlaufen
                for datacenter in datacenters:
                    try:
                        # Alle Datastores im Datacenter abrufen
                        datastores = datacenter.datastore
                        
                        if debug_mode:
                            logger.warning(f"Datacenter '{datacenter.name}' has {len(datastores)} datastores")
                        
                        # Jeden Datastore durchlaufen
                        for datastore in datastores:
                            try:
                                if debug_mode:
                                    logger.warning(f"Scanning datastore: {datastore.name}")
                                
                                # Datastore-Browser für Dateioperationen abrufen
                                browser = datastore.browser
                                
                                # Suchspezifikation für VMDK-Dateien erstellen
                                search_spec = vim.HostDatastoreBrowserSearchSpec()
                                search_spec.matchPattern = ["*.vmdk"]
                                
                                # Suche nach VMDKs im gesamten Datastore
                                try:
                                    task = browser.SearchDatastoreSubFolders_Task("[" + datastore.name + "]", search_spec)
                                    client.wait_for_task(task)
                                    search_results = task.info.result
                                    
                                    if debug_mode:
                                        logger.warning(f"Found {len(search_results)} folders in datastore {datastore.name}")
                                    
                                    # Jeden Ordner im Suchergebnis durchlaufen
                                    for result in search_results:
                                        try:
                                            folder_path = result.folderPath
                                            
                                            # Sicherstellen, dass der Ordner Dateien enthält
                                            if not hasattr(result, 'file') or not result.file:
                                                continue
                                            
                                            if debug_mode:
                                                logger.warning(f"Folder '{folder_path}' has {len(result.file)} files")
                                            
                                            # Jede VMDK-Datei im Ordner prüfen
                                            for file_info in result.file:
                                                try:
                                                    # Nur VMDK-Dateien verarbeiten
                                                    if not file_info.path.lower().endswith('.vmdk'):
                                                        continue
                                                    
                                                    # Vollständigen Pfad konstruieren
                                                    full_path = folder_path + file_info.path
                                                    normalized_path = full_path.lower()
                                                    
                                                    if debug_mode:
                                                        logger.warning(f"Found VMDK: {full_path}")
                                                    
                                                    # Nur die primäre VMDK-Datei prüfen (keine -flat, -delta, etc.)
                                                    auxiliary_patterns = [
                                                        "-flat.vmdk", "-delta.vmdk", "-ctk.vmdk", 
                                                        "-rdm.vmdk", "-sesparse.vmdk", "~"
                                                    ]
                                                    
                                                    is_auxiliary = False
                                                    for pattern in auxiliary_patterns:
                                                        if pattern in normalized_path:
                                                            is_auxiliary = True
                                                            break
                                                            
                                                    if is_auxiliary:
                                                        if debug_mode:
                                                            logger.warning(f"Skipping auxiliary VMDK: {full_path}")
                                                        continue
                                                    
                                                    # ------ SCHRITT 3: Prüfen, ob die VMDK verwendet wird ------
                                                    
                                                    # Direkte Übereinstimmung mit registrierten VMDKs
                                                    if (full_path in registered_vmdks or 
                                                        normalized_path in registered_vmdks):
                                                        if debug_mode:
                                                            logger.warning(f"VMDK in use (direct match): {full_path}")
                                                        continue
                                                    
                                                    # Pfad ohne Datastore-Klammern extrahieren und prüfen
                                                    is_orphaned = True
                                                    match = re.match(r'^\[(.*?)\] (.*)', full_path)
                                                    if match:
                                                        path_without_ds = match.group(2)
                                                        if (path_without_ds in registered_vmdks or 
                                                            path_without_ds.lower() in registered_vmdks):
                                                            if debug_mode:
                                                                logger.warning(f"VMDK in use (path match): {full_path}")
                                                            is_orphaned = False
                                                    
                                                    # Wenn die VMDK nicht als verwendet gefunden wurde, 
                                                    # zusätzliche Prüfung nach VMX-Dateien im gleichen Ordner
                                                    if is_orphaned:
                                                        try:
                                                            # Nach VMX-Dateien im selben Ordner suchen
                                                            vmx_spec = vim.HostDatastoreBrowserSearchSpec()
                                                            vmx_spec.matchPattern = ["*.vmx"]
                                                            
                                                            # Pfad für die Suche vorbereiten
                                                            search_path = folder_path
                                                            if search_path.endswith('/'):
                                                                search_path = search_path[:-1]
                                                                
                                                            # VMX-Dateien suchen
                                                            vmx_task = browser.SearchDatastore_Task(search_path, vmx_spec)
                                                            client.wait_for_task(vmx_task)
                                                            vmx_result = vmx_task.info.result
                                                            
                                                            # Wenn VMX-Dateien vorhanden sind, prüfen ob eine davon
                                                            # zur VMDK gehören könnte
                                                            if vmx_result and vmx_result.file:
                                                                if debug_mode:
                                                                    logger.warning(f"Found {len(vmx_result.file)} VMX files in folder {folder_path}")
                                                                
                                                                # VMDK-Name ohne Erweiterung
                                                                vmdk_base = os.path.splitext(file_info.path)[0]
                                                                
                                                                # VMX-Dateien durchlaufen
                                                                for vmx_file in vmx_result.file:
                                                                    # VMX-Name ohne Erweiterung
                                                                    vmx_base = os.path.splitext(vmx_file.path)[0]
                                                                    
                                                                    # Prüfen, ob VMX und VMDK zusammen gehören könnten
                                                                    if (vmdk_base == vmx_base or 
                                                                        vmdk_base.startswith(vmx_base) or 
                                                                        vmx_base.startswith(vmdk_base)):
                                                                        
                                                                        if debug_mode:
                                                                            logger.warning(f"VMDK '{vmdk_base}' might belong to VMX '{vmx_base}'")
                                                                        
                                                                        is_orphaned = False
                                                                        break
                                                        except Exception as vmx_ex:
                                                            if debug_mode:
                                                                logger.error(f"Error checking VMX files: {str(vmx_ex)}")
                                                            # Falls fehler beim VMX-Check, trotzdem fortfahren
                                                    
                                                    # ------ SCHRITT 4: Verwaiste VMDK zur Liste hinzufügen ------
                                                    if is_orphaned:
                                                        if debug_mode:
                                                            logger.warning(f"FOUND ORPHANED VMDK: {full_path}")
                                                            
                                                        # Informationen über die verwaiste VMDK sammeln
                                                        orphaned_info = {
                                                            'path': full_path,
                                                            'name': file_info.path,
                                                            'datastore': datastore.name,
                                                            'size_mb': file_info.fileSize / (1024 * 1024),
                                                            'modification_time': file_info.modification,
                                                            'explanation': "Diese VMDK-Datei ist keiner virtuellen Maschine zugeordnet."
                                                        }
                                                        
                                                        # Zur Liste hinzufügen
                                                        orphaned_vmdks.append(orphaned_info)
                                                
                                                except Exception as file_ex:
                                                    if debug_mode:
                                                        logger.error(f"Error processing file {file_info.path if hasattr(file_info, 'path') else 'Unknown'}: {str(file_ex)}")
                                                    continue
                                                    
                                        except Exception as folder_ex:
                                            if debug_mode:
                                                logger.error(f"Error processing folder {folder_path if 'folder_path' in locals() else 'Unknown'}: {str(folder_ex)}")
                                            continue
                                            
                                except Exception as search_ex:
                                    if debug_mode:
                                        logger.error(f"Error searching datastore {datastore.name}: {str(search_ex)}")
                                    continue
                                    
                            except Exception as ds_ex:
                                if debug_mode:
                                    logger.error(f"Error processing datastore {datastore.name if hasattr(datastore, 'name') else 'Unknown'}: {str(ds_ex)}")
                                continue
                                
                    except Exception as dc_ex:
                        if debug_mode:
                            logger.error(f"Error processing datacenter {datacenter.name if hasattr(datacenter, 'name') else 'Unknown'}: {str(dc_ex)}")
                        continue
                        
            except Exception as scan_ex:
                if debug_mode:
                    logger.error(f"Error scanning for orphaned VMDKs: {str(scan_ex)}")
            
            # Ergebnis zurückgeben
            logger.info(f"Enhanced v24.3 method found {len(orphaned_vmdks)} orphaned VMDKs")
            return orphaned_vmdks
            
        except Exception as e:
            if debug_mode:
                import traceback
                logger.error(f"Error in enhanced orphaned VMDK collection: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            else:
                logger.debug(f"Error in enhanced orphaned VMDK collection: {str(e)}")
            
            # Leere Liste zurückgeben bei Fehlern
            return []