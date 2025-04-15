#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Direkte VMDK-Erkennung
Speziell entwickelt, um verwaiste VMDKs zuverlässig zu identifizieren
"""

import os
import re
import logging
from pyVmomi import vim

# Configure logging
logger = logging.getLogger(__name__)

def collect_orphaned_vmdks(client):
    """
    Direkte, vereinfachte Methode zur zuverlässigen Erkennung von verwaisten VMDKs.
    
    Implementiert einen klaren, robusten Algorithmus ohne verschachtelte Logik:
    1. Sammelt alle in Verwendung befindlichen VMDK-Dateien von VMs
    2. Sammelt alle VMDK-Dateien von den Datastores
    3. Identifiziert VMDKs, die nicht in Verwendung sind (verwaist)
    
    Args:
        client: Der VSphereClient
        
    Returns:
        list: Liste von verwaisten VMDK-Informationen
    """
    # Debug-Modus aktivieren für detaillierte Logs
    debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
    if debug_mode:
        logger.warning("*** DIRECT ORPHANED VMDK COLLECTION - V24.3 ***")
    
    logger.info("Using direct VMDK collection method v24.3")
    
    # Zwei Listen aufbauen:
    # 1. Alle verwendeten VMDKs
    # 2. Alle VMDKs auf den Datastores
    used_vmdks = set()  # Verwendete VMDKs (von VMs)
    all_vmdks = []      # Alle VMDKs aus den Datastores
    
    try:
        # Zugriff auf vSphere-Content
        content = client.service_instance.content
        
        # SCHRITT 1: Sammle alle verwendeten VMDKs
        logger.info("Step 1: Collecting all VMDKs in use by virtual machines")
        
        # Container-View für VMs erstellen
        vm_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True)
        vms = vm_view.view
        
        if debug_mode:
            logger.warning(f"Found {len(vms)} VMs to analyze")
        
        # Für jede VM die VMDK-Dateien erfassen
        for vm in vms:
            try:
                # Überspringen von Templates
                if vm.config and vm.config.template:
                    continue
                    
                # Alle Festplatten der VM prüfen
                if vm.config and vm.config.hardware and vm.config.hardware.device:
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualDisk):
                            if hasattr(device.backing, 'fileName'):
                                # VMDK-Pfad von der VM
                                vmdk_path = device.backing.fileName
                                
                                # Verschiedene Formate des Pfads hinzufügen
                                used_vmdks.add(vmdk_path)
                                used_vmdks.add(vmdk_path.lower())
                                
                                # Auch ohne Datastore-Klammern hinzufügen (z.B. "[datastore1] vm/file.vmdk" -> "vm/file.vmdk")
                                match = re.match(r'^\[(.*?)\] (.*)', vmdk_path)
                                if match:
                                    path_without_ds = match.group(2)
                                    used_vmdks.add(path_without_ds)
                                    used_vmdks.add(path_without_ds.lower())
                                
                                # Nur Dateiname
                                vmdk_filename = os.path.basename(vmdk_path)
                                used_vmdks.add(vmdk_filename)
                                used_vmdks.add(vmdk_filename.lower())
                                
                                if debug_mode:
                                    logger.warning(f"VM {vm.name} uses VMDK: {vmdk_path}")
            except Exception as e:
                if debug_mode:
                    logger.error(f"Error processing VM {vm.name if hasattr(vm, 'name') else 'Unknown'}: {str(e)}")
                continue
        
        if debug_mode:
            logger.warning(f"Found {len(used_vmdks)} VMDKs in use by VMs")
                
        # SCHRITT 2: Alle VMDKs auf den Datastores sammeln
        logger.info("Step 2: Collecting all VMDKs from datastores")
        
        # Alle Datacenters durchsuchen
        datacenters = [entity for entity in content.rootFolder.childEntity 
                      if isinstance(entity, vim.Datacenter)]
        
        if debug_mode:
            logger.warning(f"Found {len(datacenters)} datacenters to scan")
            
        for datacenter in datacenters:
            try:
                datastores = datacenter.datastore
                if debug_mode:
                    logger.warning(f"Datacenter {datacenter.name} has {len(datastores)} datastores")
                
                # Alle Datastores durchsuchen
                for datastore in datastores:
                    try:
                        if debug_mode:
                            logger.warning(f"Scanning datastore: {datastore.name}")
                        
                        # Datastore-Browser verwenden
                        browser = datastore.browser
                        
                        # Nur nach VMDK-Dateien suchen
                        search_spec = vim.HostDatastoreBrowserSearchSpec()
                        search_spec.matchPattern = ["*.vmdk"]
                        
                        # Suche durchführen
                        try:
                            task = browser.SearchDatastoreSubFolders_Task("[" + datastore.name + "]", search_spec)
                            client.wait_for_task(task)
                            search_results = task.info.result
                            
                            if debug_mode:
                                logger.warning(f"Found {len(search_results)} folders in datastore {datastore.name}")
                                
                        except Exception as e:
                            if debug_mode:
                                logger.error(f"Error searching datastore {datastore.name}: {str(e)}")
                            continue
                        
                        # Verarbeite die Suchergebnisse
                        for result in search_results:
                            folder_path = result.folderPath
                            
                            if debug_mode:
                                logger.warning(f"Checking folder: {folder_path} with {len(result.file)} files")
                                
                            for file_info in result.file:
                                try:
                                    # Nur VMDK-Dateien berücksichtigen
                                    if not file_info.path.lower().endswith('.vmdk'):
                                        continue
                                        
                                    # Vollständigen Pfad konstruieren
                                    full_path = folder_path + file_info.path
                                    
                                    # Hilfsdateien überspringen
                                    if ("-flat.vmdk" in full_path.lower() or 
                                        "-delta.vmdk" in full_path.lower() or 
                                        "-ctk.vmdk" in full_path.lower() or
                                        "-rdm.vmdk" in full_path.lower() or
                                        "-sesparse.vmdk" in full_path.lower()):
                                        if debug_mode:
                                            logger.warning(f"Skipping auxiliary VMDK: {full_path}")
                                        continue
                                    
                                    # Information über die VMDK sammeln
                                    vmdk_info = {
                                        'path': full_path,
                                        'name': file_info.path,
                                        'datastore': datastore.name,
                                        'size_mb': file_info.fileSize / (1024 * 1024),
                                        'modification_time': file_info.modification,
                                        'in_use': False,  # Standardmäßig als nicht in Verwendung markieren
                                        'full_path_lower': full_path.lower(),
                                        'path_without_ds': None
                                    }
                                    
                                    # Pfad ohne Datastore-Klammern extrahieren
                                    match = re.match(r'^\[(.*?)\] (.*)', full_path)
                                    if match:
                                        vmdk_info['path_without_ds'] = match.group(2)
                                        
                                    # Zur Liste aller VMDKs hinzufügen
                                    all_vmdks.append(vmdk_info)
                                    
                                    if debug_mode:
                                        logger.warning(f"Found VMDK: {full_path}")
                                        
                                except Exception as e:
                                    if debug_mode:
                                        logger.error(f"Error processing file {file_info.path}: {str(e)}")
                                    continue
                    except Exception as e:
                        if debug_mode:
                            logger.error(f"Error processing datastore {datastore.name}: {str(e)}")
                        continue
            except Exception as e:
                if debug_mode:
                    logger.error(f"Error processing datacenter {datacenter.name}: {str(e)}")
                continue
        
        # SCHRITT 3: Verwaiste VMDKs identifizieren (nicht in Verwendung)
        logger.info("Step 3: Identifying orphaned VMDKs")
        
        if debug_mode:
            logger.warning(f"Found total of {len(all_vmdks)} VMDKs in all datastores")
            
        orphaned_vmdks = []
        
        for vmdk in all_vmdks:
            # Überprüfe, ob die VMDK verwendet wird
            is_orphaned = True
            
            # Vollständiger Pfad
            if vmdk['path'].lower() in used_vmdks or vmdk['path'] in used_vmdks:
                is_orphaned = False
                
            # Pfad ohne Datastore-Klammern
            elif vmdk['path_without_ds'] and (
                vmdk['path_without_ds'].lower() in used_vmdks or 
                vmdk['path_without_ds'] in used_vmdks):
                is_orphaned = False
                
            # Nur Dateiname
            elif vmdk['name'].lower() in used_vmdks or vmdk['name'] in used_vmdks:
                is_orphaned = False
                
            # Wenn die VMDK verwaist ist, zur Ergebnisliste hinzufügen
            if is_orphaned:
                if debug_mode:
                    logger.warning(f"FOUND ORPHANED VMDK: {vmdk['path']}")
                    
                # Formatiere das Ergebnis für den Report
                orphaned_info = {
                    'path': vmdk['path'],
                    'name': vmdk['name'],
                    'datastore': vmdk['datastore'],
                    'size_mb': vmdk['size_mb'],
                    'modification_time': vmdk['modification_time'],
                    'explanation': "Diese VMDK-Datei ist keiner virtuellen Maschine zugeordnet."
                }
                orphaned_vmdks.append(orphaned_info)
                
        # FERTIG: Ergebnisse zurückgeben
        logger.info(f"Direct method found {len(orphaned_vmdks)} orphaned VMDKs")
        
        # HACK: Stelle sicher, dass mindestens eine VMDK zurückgegeben wird, falls keine gefunden wurde
        if not orphaned_vmdks and debug_mode:
            logger.warning("No orphaned VMDKs found, adding demo entry to debug.")
            # Hier fügen wir keine Demo-VMDKs hinzu, da diese später nicht überprüft werden können
            
        return orphaned_vmdks
        
    except Exception as e:
        if debug_mode:
            import traceback
            logger.error(f"Error in direct VMDK collection: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.debug(f"Error in direct VMDK collection: {str(e)}")
        
        # Leere Liste bei Fehlern zurückgeben
        return []