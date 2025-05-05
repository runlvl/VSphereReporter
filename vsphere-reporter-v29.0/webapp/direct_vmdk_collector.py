#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter - Web Edition v29.0
Spezialisierter Sammler für verwaiste VMDK-Dateien

Verwendet einen verbesserten VM-zentrischen Ansatz zur Erkennung von VMDKs
"""

import logging
import re
from pyVmomi import vim

logger = logging.getLogger('vsphere_reporter')

class DirectVMDKCollector:
    """Spezialisierte Klasse für das Sammeln von potenziell verwaisten VMDK-Dateien"""
    
    def __init__(self, vsphere_client):
        """
        Initialisiert den Sammler mit einem verbundenen VSphereClient
        
        Args:
            vsphere_client: Ein verbundener VSphereClient
        """
        self.client = vsphere_client
        self.content = vsphere_client.content if vsphere_client else None
        self._all_vms = []                   # Liste aller VMs
        self._known_vmdk_paths = set()       # Set aller bekannten VMDK-Pfade
        self._datastore_browser_cache = {}   # Cache für DatastoreBrowser-Objekte
        self._datastore_path_cache = {}      # Cache für Datastore-Pfade
    
    def collect_orphaned_vmdks(self):
        """
        Sammelt potentiell verwaiste VMDK-Dateien
        
        Der Ansatz umfasst:
        1. Sammeln aller bekannten VMDKs, die zu VMs gehören
        2. Suchen nach allen VMDK-Dateien auf allen Datastores
        3. Identifizieren von VMDKs, die nicht zu bekannten VMs gehören
        
        Returns:
            list: Liste von Informationen über potentiell verwaiste VMDK-Dateien
        """
        logger.info("Suche nach verwaisten VMDK-Dateien...")
        
        # Schritt 1: Sammle alle VMs und ihre zugehörigen VMDKs
        self._all_vms = self.client.get_all_vms()
        self._collect_known_vmdks()
        
        # Schritt 2 & 3: Durchsuche alle Datastores nach VMDKs und identifiziere verwaiste
        datastores = self.client.get_all_datastores()
        orphaned_vmdks = []
        
        for ds in datastores:
            try:
                # Skip-Logik für unzugängliche Datastores
                if hasattr(ds, 'summary') and hasattr(ds.summary, 'accessible') and not ds.summary.accessible:
                    logger.warning(f"Überspringe nicht zugänglichen Datastore: {ds.name}")
                    continue
                
                # VMDKs auf dem Datastore suchen
                vmdks_on_datastore = self._search_vmdks_on_datastore(ds)
                
                # Verwaiste VMDKs identifizieren
                for vmdk in vmdks_on_datastore:
                    full_path = f"[{ds.name}] {vmdk['path']}"
                    
                    # Prüfen, ob die VMDK bereits einer VM zugeordnet ist
                    if full_path not in self._known_vmdk_paths:
                        # VMDK als potenziell verwaist markieren
                        vmdk['datastore'] = ds.name
                        vmdk['full_path'] = full_path
                        vmdk['status'] = "POTENTIALLY ORPHANED"
                        
                        # Weitere Analyse, ob die VMDK wirklich verwaist ist
                        vmdk['is_template'] = self._is_template_vmdk(vmdk['path'])
                        vmdk['has_vmx_file'] = self._has_associated_vmx(ds, vmdk['path'])
                        
                        # Verschiedene VMDK-Typen erkennen
                        if vmdk['is_template']:
                            vmdk['status'] = "TEMPLATE VMDK"
                        elif vmdk['has_vmx_file']:
                            vmdk['status'] = "HAS VMX ASSOCIATION"
                        elif self._is_in_templates_folder(vmdk['path']):
                            vmdk['status'] = "IN TEMPLATES FOLDER"
                        elif self._is_delta_disk(vmdk['path']):
                            vmdk['status'] = "DELTA DISK (SNAPSHOT)"
                        
                        # Nur potenziell verwaiste VMDKs hinzufügen
                        if vmdk['status'] == "POTENTIALLY ORPHANED":
                            orphaned_vmdks.append(vmdk)
                
            except Exception as e:
                logger.error(f"Fehler beim Durchsuchen des Datastores {ds.name}: {str(e)}")
        
        logger.info(f"{len(orphaned_vmdks)} potenziell verwaiste VMDK-Dateien gefunden")
        return orphaned_vmdks
    
    def _collect_known_vmdks(self):
        """Sammelt alle bekannten VMDK-Pfade von existierenden VMs"""
        logger.debug("Sammle bekannte VMDK-Pfade von existierenden VMs...")
        
        self._known_vmdk_paths = set()
        
        for vm in self._all_vms:
            try:
                # VMDKs der VM sammeln
                if vm.config and vm.config.hardware and vm.config.hardware.device:
                    for device in vm.config.hardware.device:
                        if isinstance(device, vim.vm.device.VirtualDisk):
                            if hasattr(device.backing, 'fileName'):
                                self._known_vmdk_paths.add(device.backing.fileName)
                
                # Snapshot-VMDKs sammeln
                if vm.snapshot:
                    self._collect_snapshot_vmdks(vm)
                    
            except Exception as e:
                logger.error(f"Fehler beim Sammeln von VMDK-Pfaden für VM {vm.name}: {str(e)}")
        
        logger.debug(f"{len(self._known_vmdk_paths)} bekannte VMDK-Pfade gesammelt")
    
    def _collect_snapshot_vmdks(self, vm):
        """
        Sammelt die VMDK-Pfade von Snapshots einer VM
        
        Args:
            vm: Virtual Machine-Objekt
        """
        def process_snapshot_tree(tree):
            """Verarbeitet den Snapshot-Baum rekursiv"""
            for snapshot in tree:
                try:
                    # Layout-Informationen auslesen, falls verfügbar
                    if hasattr(snapshot, 'layoutEx') and snapshot.layoutEx and snapshot.layoutEx.disk:
                        for disk in snapshot.layoutEx.disk:
                            for chain in disk.chain:
                                for file_key in chain.fileKey:
                                    for file_info in snapshot.layoutEx.file:
                                        if file_info.key == file_key and file_info.name.endswith('.vmdk'):
                                            self._known_vmdk_paths.add(file_info.name)
                    
                    # Mit Snapshot-VM-Objekten
                    snapshot_vm = snapshot.snapshot.vm if snapshot.snapshot and hasattr(snapshot.snapshot, 'vm') else None
                    if snapshot_vm and snapshot_vm.config and snapshot_vm.config.hardware:
                        for device in snapshot_vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk) and hasattr(device.backing, 'fileName'):
                                self._known_vmdk_paths.add(device.backing.fileName)
                    
                    # Rekursiv für Kind-Snapshots
                    if snapshot.childSnapshotList:
                        process_snapshot_tree(snapshot.childSnapshotList)
                        
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten von Snapshot für VM {vm.name}: {str(e)}")
        
        # Snapshot-Baum verarbeiten, falls vorhanden
        if vm.snapshot and vm.snapshot.rootSnapshotList:
            process_snapshot_tree(vm.snapshot.rootSnapshotList)
    
    def _search_vmdks_on_datastore(self, datastore):
        """
        Durchsucht einen Datastore nach VMDK-Dateien
        
        Args:
            datastore: Datastore-Objekt
            
        Returns:
            list: Liste von VMDK-Informationsdictionaries
        """
        vmdks = []
        search_stack = [('', '')]  # Tupel aus (Pfad, Elternpfad)
        
        while search_stack:
            folder_path, parent_path = search_stack.pop()
            ds_browser = self._get_datastore_browser(datastore)
            search_spec = vim.host.DatastoreBrowser.SearchSpec(
                details=vim.host.DatastoreBrowser.FileInfo.Details(fileType=True, fileSize=True, modification=True),
                query=[vim.host.DatastoreBrowser.FolderQuery(), vim.host.DatastoreBrowser.VmDiskQuery()]
            )
            
            task = ds_browser.SearchDatastoreSubFolders_Task(folderPath=folder_path, searchSpec=search_spec)
            search_results = self.client.wait_for_task(task)
            
            for result in search_results:
                for file_info in result.file:
                    if isinstance(file_info, vim.host.DatastoreBrowser.VmDiskInfo) and file_info.path.endswith('.vmdk'):
                        # Prüfen, ob es sich um eine Beschreibungsdatei oder eine Flat-Datei handelt
                        if not file_info.path.endswith('-flat.vmdk') and not file_info.path.endswith('-delta.vmdk'):
                            
                            # Vollständigen Dateipfad innerhalb des Datastores konstruieren
                            relative_path = result.folderPath
                            if not relative_path.endswith('/'):
                                relative_path += '/'
                            
                            file_path = relative_path + file_info.path
                            
                            # VMDK-Informationen sammeln
                            vmdk_info = {
                                'path': file_path,
                                'file_name': file_info.path,
                                'size_bytes': file_info.fileSize,
                                'modification_time': file_info.modification,
                                'parent_folder': parent_path
                            }
                            
                            vmdks.append(vmdk_info)
                    
                    # Verzeichnisse zur weiteren Durchsuchung zur Stack hinzufügen
                    elif isinstance(file_info, vim.host.DatastoreBrowser.FolderInfo):
                        new_folder_path = result.folderPath
                        if not new_folder_path.endswith('/'):
                            new_folder_path += '/'
                        new_folder_path += file_info.path
                        
                        search_stack.append((new_folder_path, result.folderPath))
        
        return vmdks
    
    def _get_datastore_browser(self, datastore):
        """
        Holt den DatastoreBrowser für einen Datastore (mit Cache)
        
        Args:
            datastore: Datastore-Objekt
            
        Returns:
            vim.host.DatastoreBrowser: DatastoreBrowser-Objekt
        """
        if datastore.name not in self._datastore_browser_cache:
            self._datastore_browser_cache[datastore.name] = datastore.browser
        
        return self._datastore_browser_cache[datastore.name]
    
    def _is_template_vmdk(self, path):
        """
        Prüft, ob eine VMDK-Datei zu einem Template gehört
        
        Args:
            path: Pfad der VMDK-Datei
            
        Returns:
            bool: True, wenn die VMDK zu einem Template gehört
        """
        # Wenn in einem Verzeichnis mit "template" oder "vorlage" im Namen
        if 'template' in path.lower() or 'vorlage' in path.lower():
            return True
        
        # Wenn das Verzeichnis einen der standardmäßigen Template-Pfade enthält
        template_paths = ['/templates/', '/Template/', '/vorlagen/']
        return any(template_path in path for template_path in template_paths)
    
    def _has_associated_vmx(self, datastore, vmdk_path):
        """
        Prüft, ob eine VMDK-Datei eine zugehörige VMX-Datei hat
        
        Args:
            datastore: Datastore-Objekt
            vmdk_path: Pfad der VMDK-Datei
            
        Returns:
            bool: True, wenn eine zugehörige VMX-Datei existiert
        """
        try:
            # Verzeichnispfad extrahieren
            folder_path = vmdk_path.rsplit('/', 1)[0] if '/' in vmdk_path else ''
            
            # Basisname der VM extrahieren (VMDK ohne Erweiterung)
            vmdk_file = vmdk_path.rsplit('/', 1)[1] if '/' in vmdk_path else vmdk_path
            vm_base_name = re.sub(r'(_[0-9]+)?\.vmdk$', '', vmdk_file)
            
            # Nach VMX-Dateien im selben Verzeichnis suchen
            ds_browser = self._get_datastore_browser(datastore)
            search_spec = vim.host.DatastoreBrowser.SearchSpec(
                details=vim.host.DatastoreBrowser.FileInfo.Details(fileType=True),
                query=[vim.host.DatastoreBrowser.VmConfigQuery()]
            )
            
            task = ds_browser.SearchDatastore_Task(datastorePath=f"[{datastore.name}] {folder_path}", searchSpec=search_spec)
            search_result = self.client.wait_for_task(task)
            
            for file_info in search_result.file:
                # Prüfen, ob die VMX dem Basisnamen der VMDK entspricht
                if file_info.path.endswith('.vmx') and file_info.path.startswith(vm_base_name):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Fehler beim Suchen nach zugehöriger VMX-Datei für {vmdk_path}: {str(e)}")
            return False
    
    def _is_in_templates_folder(self, path):
        """
        Prüft, ob sich eine VMDK-Datei in einem Templates-Verzeichnis befindet
        
        Args:
            path: Pfad der VMDK-Datei
            
        Returns:
            bool: True, wenn die VMDK in einem Templates-Verzeichnis liegt
        """
        template_indicators = ['template', 'vorlage', 'iso', 'images', 'installation']
        path_lower = path.lower()
        
        return any(indicator in path_lower for indicator in template_indicators)
    
    def _is_delta_disk(self, path):
        """
        Prüft, ob eine VMDK-Datei eine Delta-Disk (Snapshot) ist
        
        Args:
            path: Pfad der VMDK-Datei
            
        Returns:
            bool: True, wenn die VMDK eine Delta-Disk ist
        """
        # Typische Merkmale von Delta-Disks
        delta_patterns = [
            r'-\d{6}\.vmdk$',  # z.B. VM-000001.vmdk (Snapshot-Format)
            r'-delta\.vmdk$',   # Explizites Delta-Disk-Format
            r'_\d+\.vmdk$'      # z.B. VM_1.vmdk (alternatives Snapshot-Format)
        ]
        
        return any(re.search(pattern, path) for pattern in delta_patterns)