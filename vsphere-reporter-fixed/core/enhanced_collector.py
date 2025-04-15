#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced data collection methods for VMware vSphere Reporter v24.0
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
    Verbesserte Datensammelmethoden für v24.0 zur Behebung von Problemen mit
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
            logger.warning("*** ENHANCED SNAPSHOTS COLLECTION - V24.0 ***")
        
        logger.info("Using enhanced v24.0 snapshot collection")
        
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
        Verbesserte Methode zur Sammlung von verwaisten VMDK-Dateien
        
        Args:
            client: Der VSphereClient
            
        Returns:
            list: Liste von verwaisten VMDK-Informationen
        """
        # Debug-Modus-Check für verbesserte Protokollierung
        debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
        if debug_mode:
            logger.warning("*** ENHANCED ORPHANED VMDK COLLECTION - V24.1 ***")
        
        logger.info("Using enhanced v24.1 orphaned VMDK collection")
        
        # Globaler Exception-Handler - Tool darf nicht abstürzen, auch bei unerwarteten Fehlern
        try:
            # Registrierte VMDKs mit verbessertem Ansatz sammeln
            registered_vmdks = set()
            
            try:
                # Direkter Zugriff auf alle VMs
                content = client.service_instance.content
                vm_view = content.viewManager.CreateContainerView(
                    content.rootFolder, [vim.VirtualMachine], True)
                vms = vm_view.view
            except Exception as e:
                if debug_mode:
                    logger.error(f"Fehler beim Zugriff auf VMs: {str(e)}")
                else:
                    logger.debug(f"Fehler beim Zugriff auf VMs: {str(e)}")
                vms = []
            
            # Erfasse alle registrierten VMDKs
            for vm in vms:
                try:
                    # Templates überspringen
                    if vm.config.template:
                        continue
                        
                    if vm.config and vm.config.hardware and vm.config.hardware.device:
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                if hasattr(device.backing, 'fileName'):
                                    # Vollständiger Pfad wie vom vSphere API zurückgegeben
                                    full_path = device.backing.fileName
                                    registered_vmdks.add(full_path)
                                    
                                    # Normalisierte Form (Kleinschreibung)
                                    registered_vmdks.add(full_path.lower())
                                    
                                    # Pfad ohne Datastore-Name-Bracket (z.B. ohne [datastore1])
                                    if full_path.startswith('['):
                                        match = re.match(r'^\[(.*?)\] (.*)', full_path)
                                        if match:
                                            registered_vmdks.add(match.group(2))
                                            registered_vmdks.add(match.group(2).lower())
                                    
                                    if debug_mode:
                                        logger.warning(f"Registered VMDK: {full_path}")
                except Exception as e:
                    if debug_mode:
                        logger.error(f"Error processing VM {vm.name if hasattr(vm, 'name') else 'Unknown'}: {str(e)}")
                    continue
                    
            if debug_mode:
                logger.warning(f"Total registered VMDKs: {len(registered_vmdks)}")
                    
            # Suche nach VMDKs in allen Datastores
            datacenters = [entity for entity in content.rootFolder.childEntity 
                        if isinstance(entity, vim.Datacenter)]
            
            orphaned_vmdks = []
            
            if debug_mode:
                logger.warning(f"Found {len(datacenters)} datacenters to scan")
                
            for datacenter in datacenters:
                try:
                    datastores = datacenter.datastore
                    if debug_mode:
                        logger.warning(f"Datacenter {datacenter.name} has {len(datastores)} datastores")
                    
                    for datastore in datastores:
                        try:
                            if debug_mode:
                                logger.warning(f"Scanning datastore: {datastore.name}")
                            
                            # Datastore-Browser abrufen
                            browser = datastore.browser
                            
                            # Suchspezifikation nur für VMDK-Dateien
                            search_spec = vim.HostDatastoreBrowserSearchSpec()
                            search_spec.matchPattern = ["*.vmdk"]
                            
                            # Suche nach VMDKs im Datastore durchführen
                            # Fehlerbehandlung verbessert, um Abstürze zu vermeiden
                            try:
                                task = browser.SearchDatastoreSubFolders_Task("[" + datastore.name + "]", search_spec)
                                client.wait_for_task(task)
                                search_results = task.info.result
                                
                                if debug_mode:
                                    logger.warning(f"Found {len(search_results)} folders in datastore {datastore.name}")
                                    
                            except Exception as e:
                                if debug_mode:
                                    logger.error(f"Error searching datastore {datastore.name}: {str(e)}")
                                else:
                                    logger.debug(f"Error searching datastore {datastore.name}: {str(e)}")
                                continue
                            
                            # Verarbeite die Suchergebnisse mit verbesserter Fehlerbehandlung
                            for result in search_results:
                                try:
                                    folder_path = result.folderPath
                                    
                                    # Überprüfe, ob die Dateien-Eigenschaft existiert und nicht leer ist
                                    if not hasattr(result, 'file') or not result.file:
                                        if debug_mode:
                                            logger.warning(f"Folder {folder_path} has no files or file property")
                                        continue
                                    
                                    # Verbessertes Logging für Nachverfolgung
                                    if debug_mode:
                                        logger.warning(f"Checking folder: {folder_path} with {len(result.file)} files")
                                    
                                    for file_info in result.file:
                                        try:
                                            if not file_info.path.lower().endswith('.vmdk'):
                                                continue
                                                
                                            # Vollständigen Pfad konstruieren
                                            full_path = folder_path + file_info.path
                                            normalized_path = full_path.lower()
                                            
                                            # Prüfe auf Hilfs-VMDK-Dateien (delta, flat)
                                            if ("-flat.vmdk" in normalized_path or 
                                                "-delta.vmdk" in normalized_path or 
                                                "-ctk.vmdk" in normalized_path or
                                                "-rdm.vmdk" in normalized_path or
                                                "-sesparse.vmdk" in normalized_path or
                                                "~" in normalized_path):
                                                if debug_mode:
                                                    logger.warning(f"Skipping auxiliary VMDK: {full_path}")
                                                continue
                                            
                                            # Zuverlässige Prüfung, ob VMDK in Verwendung ist
                                            if (full_path in registered_vmdks or 
                                                full_path.lower() in registered_vmdks):
                                                if debug_mode:
                                                    logger.warning(f"VMDK in use (direct match): {full_path}")
                                                continue
                                            
                                            # Extrahiere Pfad ohne Datastore-Klammern
                                            match = re.match(r'^\[(.*?)\] (.*)', full_path)
                                            if match:
                                                path_without_ds = match.group(2)
                                                if (path_without_ds in registered_vmdks or 
                                                    path_without_ds.lower() in registered_vmdks):
                                                    if debug_mode:
                                                        logger.warning(f"VMDK in use (path match): {full_path}")
                                                    continue
                                            
                                            # Weitere Validierung für verwaiste VMDKs
                                            # Prüfe, ob in demselben Verzeichnis eine VM-Konfiguration existiert
                                            is_orphaned = True
                                            folder_content = None
                                            
                                            # VMX-Dateien im selben Verzeichnis suchen
                                            try:
                                                vmx_spec = vim.HostDatastoreBrowserSearchSpec()
                                                vmx_spec.matchPattern = ["*.vmx"]
                                                
                                                folder_without_brackets = folder_path
                                                if folder_path.endswith('/'):
                                                    folder_without_brackets = folder_path[:-1]
                                                    
                                                # Führe eine Suche nach VMX-Dateien durch
                                                task = browser.SearchDatastore_Task(folder_without_brackets, vmx_spec)
                                                client.wait_for_task(task)
                                                folder_content = task.info.result
                                                
                                                # Wenn VMX-Dateien gefunden wurden, ist die VMDK möglicherweise nicht verwaist
                                                if folder_content and folder_content.file:
                                                    if debug_mode:
                                                        logger.warning(f"Found {len(folder_content.file)} VMX files in the same folder")
                                                    
                                                    # VMDK-Basisname ohne Erweiterung
                                                    vmdk_base = os.path.splitext(file_info.path)[0]
                                                    
                                                    # Prüfe, ob eine VMX mit ähnlichem Namen existiert
                                                    for vmx_file in folder_content.file:
                                                        vmx_base = os.path.splitext(vmx_file.path)[0]
                                                        
                                                        # Wenn VMX- und VMDK-Namen ähnlich sind, ist die VMDK wahrscheinlich nicht verwaist
                                                        if vmdk_base == vmx_base or vmdk_base.startswith(vmx_base) or vmx_base.startswith(vmdk_base):
                                                            is_orphaned = False
                                                            if debug_mode:
                                                                logger.warning(f"VMDK might belong to VMX: {vmx_file.path}")
                                                            break
                                            except Exception as e:
                                                if debug_mode:
                                                    logger.error(f"Error checking for VMX files: {str(e)}")
                                                # Im Zweifelsfall weiter prüfen
                                            
                                            # Nur wirklich verwaiste VMDKs zur Liste hinzufügen
                                            if is_orphaned:
                                                if debug_mode:
                                                    logger.warning(f"FOUND ORPHANED VMDK: {full_path}")
                                                    
                                                orphaned_info = {
                                                    'path': full_path,
                                                    'name': file_info.path,
                                                    'datastore': datastore.name,
                                                    'size_mb': file_info.fileSize / (1024 * 1024),
                                                    'modification_time': file_info.modification,
                                                    'explanation': "Diese VMDK-Datei ist keiner virtuellen Maschine zugeordnet."
                                                }
                                                orphaned_vmdks.append(orphaned_info)
                                        except Exception as e:
                                            if debug_mode:
                                                logger.error(f"Error processing file {file_info.path}: {str(e)}")
                                            else:
                                                logger.debug(f"Error processing file: {str(e)}")
                                            continue
                        except Exception as e:
                            if debug_mode:
                                logger.error(f"Error processing datastore {datastore.name}: {str(e)}")
                            else:
                                logger.debug(f"Error processing datastore: {str(e)}")
                            continue
                except Exception as e:
                    if debug_mode:
                        logger.error(f"Error processing datacenter {datacenter.name}: {str(e)}")
                    else:
                        logger.debug(f"Error processing datacenter: {str(e)}")
                    continue
                        
            logger.info(f"Enhanced v24.1 method found {len(orphaned_vmdks)} orphaned VMDKs")
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