#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VSphere Debug Collector - Spezialwerkzeug zur Diagnose von Problemen mit Snapshots und verwaisten VMDKs
Version 24.0 - April 2025
"""

import argparse
import datetime
import logging
import re
import sys
import os
import json
import time
import getpass
import ssl
from contextlib import contextmanager
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

# Konfiguration des Loggers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"vsphere_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@contextmanager
def suppress_stdout_stderr():
    """
    Kontext-Manager zum Unterdrücken von stdout und stderr Ausgaben
    Im Debug-Modus werden Ausgaben nicht unterdrückt
    """
    class DummyContext:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False
            
    if os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1':
        yield DummyContext()
    else:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        class NullDevice:
            def write(self, s):
                pass
                
            def flush(self):
                pass
                
        try:
            sys.stdout = NullDevice()
            sys.stderr = NullDevice()
            yield
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

class VSphereClient:
    """Einfacher vSphere-Client für CLI-Diagnose"""
    
    def __init__(self, host, user, password, ignore_ssl=False):
        """Initialisiere den Client mit Verbindungsparametern"""
        self.host = host
        self.user = user
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.service_instance = None
        
    def connect(self):
        """Verbindung zum vCenter herstellen"""
        logger.info(f"Verbinde mit vCenter: {self.host}")
        
        if self.ignore_ssl:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.verify_mode = ssl.CERT_NONE
        else:
            context = None
            
        try:
            self.service_instance = SmartConnect(
                host=self.host,
                user=self.user,
                pwd=self.password,
                sslContext=context
            )
            
            if not self.service_instance:
                raise Exception("Verbindung zum vCenter konnte nicht hergestellt werden.")
                
            logger.info("Verbindung zum vCenter hergestellt.")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Verbinden mit vCenter: {str(e)}")
            return False
            
    def disconnect(self):
        """Trennen vom vCenter"""
        if self.service_instance:
            Disconnect(self.service_instance)
            logger.info("Verbindung zum vCenter getrennt.")
            
    def wait_for_task(self, task):
        """
        Warten auf den Abschluss einer vCenter-Aufgabe
        
        Args:
            task: Die Aufgabe, auf die gewartet werden soll
            
        Returns:
            Task-Ergebnis
        """
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(1)
            
        if task.info.state == vim.TaskInfo.State.success:
            return task.info.result
        else:
            raise Exception(task.info.error.msg)
            
    def get_virtual_machines(self):
        """
        Gibt eine Liste aller virtuellen Maschinen zurück
        
        Returns:
            list: Liste von VM-Objekten
        """
        if not self.service_instance:
            raise Exception("Nicht mit vCenter verbunden.")
            
        content = self.service_instance.content
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True)
        vms = container.view
        container.Destroy()
        return vms

class DataCollector:
    """Collector für vSphere-Umgebungsdaten mit Fokus auf Snapshots und verwaiste VMDKs"""
    
    def __init__(self, vsphere_client):
        """
        Initialisiere den Datensammler
        
        Args:
            vsphere_client: Verbundener vSphere-Client
        """
        self.client = vsphere_client
        
    def collect_snapshot_info(self):
        """
        Sammle Informationen über VM-Snapshots
        
        Returns:
            list: Liste von Snapshot-Informationsdictionaries, sortiert nach Alter (älteste zuerst)
        """
        logger.info("Sammle Informationen über VM-Snapshots (Standard-Methode)")
        os.environ['VSPHERE_REPORTER_DEBUG'] = '1'  # Debug-Modus für detaillierte Logs aktivieren
        
        try:
            # Direkter Zugriff auf alle VMs und rekursive Abfrage
            content = self.client.service_instance.content
            container = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True)
            vms = container.view
            
            logger.info(f"{len(vms)} VMs gefunden zum Prüfen auf Snapshots")
            
            snapshot_info_list = []
            vm_with_snapshot_count = 0
            
            for vm in vms:
                try:
                    logger.info(f"Verarbeite VM: {vm.name}")
                    
                    # Überspringe Templates
                    if vm.config.template:
                        logger.info(f"  → Überspringe Template: {vm.name}")
                        continue
                        
                    # Überprüfe, ob VM Snapshots hat
                    if vm.snapshot:
                        logger.info(f"  → VM hat snapshot-Eigenschaft")
                        if hasattr(vm.snapshot, 'rootSnapshotList'):
                            logger.info(f"  → VM hat rootSnapshotList-Eigenschaft")
                            logger.info(f"  → Anzahl Root-Snapshots: {len(vm.snapshot.rootSnapshotList)}")
                            
                            snapshots = self._get_snapshot_tree(vm, vm.snapshot.rootSnapshotList)
                            
                            if snapshots:
                                vm_with_snapshot_count += 1
                                logger.info(f"  → {len(snapshots)} Snapshots gefunden für VM {vm.name}")
                                
                                for snapshot in snapshots:
                                    snapshot_info_list.append(snapshot)
                        else:
                            logger.warning(f"  → VM hat keine rootSnapshotList-Eigenschaft: {vm.name}")
                    else:
                        logger.info(f"  → VM hat keine snapshot-Eigenschaft: {vm.name}")
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten der VM {vm.name}: {str(e)}")
                    
            # Sortiere nach Erstellungszeit (älteste zuerst)
            try:
                snapshot_info_list.sort(key=lambda x: x['create_time'])
            except Exception as e:
                logger.error(f"Fehler beim Sortieren der Snapshots: {str(e)}")
                
            logger.info(f"Insgesamt {len(snapshot_info_list)} Snapshots über {vm_with_snapshot_count} VMs gefunden")
            
            # Detaillierte Diagnoseausgabe
            if snapshot_info_list:
                logger.info("\nSnapshot-Details:")
                for i, snap in enumerate(snapshot_info_list):
                    logger.info(f"Snapshot {i+1}:")
                    for key, value in snap.items():
                        logger.info(f"  {key}: {value}")
            else:
                logger.warning("KEINE SNAPSHOTS GEFUNDEN!")
                
            return snapshot_info_list
            
        except Exception as e:
            logger.error(f"Schwerwiegender Fehler bei der Snapshot-Erfassung: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return self._collect_snapshot_info_fallback()
            
    def _collect_snapshot_info_fallback(self):
        """
        Fallback-Methode zur Snapshot-Sammlung, verwendet den alten Ansatz
        """
        logger.info("Sammle Informationen über VM-Snapshots (Fallback-Methode)")
        
        try:
            # Direkter Zugriff über die Content-Eigenschaft
            content = self.client.service_instance.content
            
            # Property Collector verwenden für effizientere Abfrage
            property_spec = vim.PropertySpec()
            property_spec.type = vim.VirtualMachine
            property_spec.pathSet = ['name', 'snapshot', 'config.template']
            
            # Traversal Spec für den Container
            traversal_spec = vim.TraversalSpec()
            traversal_spec.name = 'traverseEntities'
            traversal_spec.path = 'view'
            traversal_spec.skip = False
            traversal_spec.type = vim.view.ContainerView
            
            # Container View für alle VMs
            container = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True)
                
            # Object Spec für die Abfrage
            obj_spec = vim.ObjectSpec()
            obj_spec.obj = container
            obj_spec.skip = True
            obj_spec.selectSet = [traversal_spec]
            
            # Filter Spec für die Abfrage
            filter_spec = vim.PropertyFilterSpec()
            filter_spec.objectSet = [obj_spec]
            filter_spec.propSet = [property_spec]
            
            # Eigenschaften abrufen
            result = content.propertyCollector.RetrieveContents([filter_spec])
            logger.info(f"PropertyCollector ergab {len(result)} VM-Ergebnisse")
            
            snapshot_info_list = []
            vm_with_snapshot_count = 0
            
            # Ergebnisse verarbeiten
            for obj in result:
                try:
                    props = {prop.name: prop.val for prop in obj.propSet}
                    
                    # Templates überspringen
                    if 'config.template' in props and props['config.template']:
                        continue
                        
                    vm_name = props.get('name', 'Unbekannte VM')
                    
                    # Snapshots verarbeiten
                    if 'snapshot' in props and props['snapshot'] is not None:
                        snapshot_obj = props['snapshot']
                        
                        if hasattr(snapshot_obj, 'rootSnapshotList') and snapshot_obj.rootSnapshotList:
                            vm_with_snapshot_count += 1
                            snapshots = self._get_snapshot_tree(None, snapshot_obj.rootSnapshotList)
                            
                            for snapshot in snapshots:
                                snapshot['vm_name'] = vm_name
                                create_time = snapshot['create_time']
                                age = datetime.datetime.now() - create_time
                                snapshot['age_days'] = age.days
                                snapshot['age_hours'] = age.seconds // 3600
                                snapshot['summary'] = f"{vm_name}: {snapshot['name']} ({age.days} Tage alt)"
                                
                                snapshot_info_list.append(snapshot)
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten des VM-Objekts: {str(e)}")
                    
            logger.info(f"Fallback-Methode fand {len(snapshot_info_list)} Snapshots über {vm_with_snapshot_count} VMs")
            
            # Sortiere nach Erstellungszeit (älteste zuerst)
            snapshot_info_list.sort(key=lambda x: x['create_time'])
            
            return snapshot_info_list
            
        except Exception as e:
            logger.error(f"Schwerwiegender Fehler in der Snapshot-Fallback-Methode: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return []
            
    def _get_snapshot_tree(self, vm, snapshot_list):
        """
        Verarbeite den Snapshot-Baum rekursiv
        
        Args:
            vm: Virtual Machine-Objekt
            snapshot_list: Liste von Snapshot-Objekten
            
        Returns:
            list: Verarbeitete Liste von Snapshot-Informationsdictionaries
        """
        snapshots = []
        
        for snapshot in snapshot_list:
            try:
                # Grundlegende Snapshot-Informationen
                snap_info = {
                    'name': snapshot.name,
                    'description': snapshot.description,
                    'create_time': snapshot.createTime,
                    'state': snapshot.state,
                    'snapshot_id': snapshot.id,
                    'quiesced': snapshot.quiesced
                }
                
                # VM-Name hinzufügen, wenn verfügbar
                if vm:
                    snap_info['vm_name'] = vm.name
                    
                # Alter berechnen
                create_time = snapshot.createTime
                age = datetime.datetime.now() - create_time
                snap_info['age_days'] = age.days
                snap_info['age_hours'] = age.seconds // 3600
                
                # Zusammenfassung erstellen
                if vm:
                    snap_info['summary'] = f"{vm.name}: {snapshot.name} ({age.days} Tage alt)"
                else:
                    snap_info['summary'] = f"{snapshot.name} ({age.days} Tage alt)"
                    
                snapshots.append(snap_info)
                
                # Untergeordnete Snapshots verarbeiten
                if snapshot.childSnapshotList:
                    snapshots.extend(self._get_snapshot_tree(vm, snapshot.childSnapshotList))
            except Exception as e:
                logger.error(f"Fehler beim Verarbeiten eines Snapshots: {str(e)}")
                
        return snapshots
        
    def collect_orphaned_vmdks(self):
        """
        Sammle Informationen über verwaiste VMDK-Dateien
        
        Returns:
            list: Liste von verwaisten VMDK-Informationsdictionaries
        """
        logger.info("Sammle Informationen über verwaiste VMDK-Dateien (Standard-Methode)")
        os.environ['VSPHERE_REPORTER_DEBUG'] = '1'  # Debug-Modus für detaillierte Logs aktivieren
        
        try:
            # Erst alle registrierten VMDKs sammeln
            registered_vmdks = set()
            vms = self.client.get_virtual_machines()
            
            logger.info(f"{len(vms)} VMs gefunden zum Prüfen auf registrierte VMDKs")
            
            # Alle registrierten VMDKs sammeln
            for vm in vms:
                try:
                    # Überspringe Templates
                    if vm.config.template:
                        continue
                        
                    if vm.config and vm.config.hardware and vm.config.hardware.device:
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                if hasattr(device.backing, 'fileName'):
                                    # Vollständiger Pfad
                                    full_path = device.backing.fileName
                                    registered_vmdks.add(full_path)
                                    
                                    # Normalisierte Form (Kleinschreibung)
                                    registered_vmdks.add(full_path.lower())
                                    
                                    # Pfad ohne Datastore-Teil
                                    if full_path.startswith('['):
                                        match = re.match(r'^\[(.*?)\] (.*)', full_path)
                                        if match:
                                            registered_vmdks.add(match.group(2))
                                            registered_vmdks.add(match.group(2).lower())
                                            
                                    logger.info(f"Registrierte VMDK: {full_path}")
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten der VM {vm.name if hasattr(vm, 'name') else 'Unbekannt'} für VMDKs: {str(e)}")
                    
            logger.info(f"Insgesamt {len(registered_vmdks)} registrierte VMDKs gefunden")
            
            # Alle Datacenters durchsuchen
            content = self.client.service_instance.content
            datacenters = [entity for entity in content.rootFolder.childEntity 
                          if isinstance(entity, vim.Datacenter)]
                          
            logger.info(f"{len(datacenters)} Datacenters zum Scannen gefunden")
            
            orphaned_vmdks = []
            
            # Alle Datastores durchsuchen
            for datacenter in datacenters:
                try:
                    datastores = datacenter.datastore
                    logger.info(f"Datacenter {datacenter.name} hat {len(datastores)} Datastores")
                    
                    for datastore in datastores:
                        try:
                            logger.info(f"Scanne Datastore: {datastore.name}")
                            
                            # Datastore Browser abrufen
                            browser = datastore.browser
                            
                            # Suchspezifikation für VMDK-Dateien
                            search_spec = vim.HostDatastoreBrowserSearchSpec()
                            search_spec.matchPattern = ["*.vmdk"]
                            
                            # Suche nach VMDKs im Datastore
                            task = browser.SearchDatastoreSubFolders_Task("[" + datastore.name + "]", search_spec)
                            self.client.wait_for_task(task)
                            search_results = task.info.result
                            
                            logger.info(f"{len(search_results)} Ordner im Datastore {datastore.name} gefunden")
                            
                            # Verarbeite die Suchergebnisse
                            for result in search_results:
                                folder_path = result.folderPath
                                logger.info(f"Prüfe Ordner: {folder_path} mit {len(result.file)} Dateien")
                                
                                for file_info in result.file:
                                    try:
                                        if not file_info.path.lower().endswith('.vmdk'):
                                            continue
                                            
                                        # Vollständigen Pfad konstruieren
                                        full_path = folder_path + file_info.path
                                        normalized_path = full_path.lower()
                                        
                                        # Prüfe auf Hilfs-VMDK-Dateien
                                        if ("-flat.vmdk" in normalized_path or 
                                            "-delta.vmdk" in normalized_path or 
                                            "-ctk.vmdk" in normalized_path or
                                            "-rdm.vmdk" in normalized_path or
                                            "-sesparse.vmdk" in normalized_path):
                                            logger.info(f"Überspringe Hilfs-VMDK: {full_path}")
                                            continue
                                            
                                        # Prüfe, ob VMDK in Verwendung ist
                                        if (full_path in registered_vmdks or 
                                            full_path.lower() in registered_vmdks):
                                            logger.info(f"VMDK in Verwendung (direkter Treffer): {full_path}")
                                            continue
                                            
                                        # Extrahiere Pfad ohne Datastore-Klammern
                                        match = re.match(r'^\[(.*?)\] (.*)', full_path)
                                        if match:
                                            path_without_ds = match.group(2)
                                            if (path_without_ds in registered_vmdks or 
                                                path_without_ds.lower() in registered_vmdks):
                                                logger.info(f"VMDK in Verwendung (Pfad-Treffer): {full_path}")
                                                continue
                                                
                                        # Weitere Validierung
                                        if not self._is_vmdk_orphaned(folder_path, file_info.path):
                                            logger.info(f"VMDK nicht verwaist (Funktionscheck): {full_path}")
                                            continue
                                            
                                        # An diesem Punkt ist die VMDK verwaist
                                        logger.info(f"VERWAISTE VMDK GEFUNDEN: {full_path}")
                                        
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
                                        logger.error(f"Fehler bei der Verarbeitung der Datei {file_info.path}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Fehler bei der Verarbeitung des Datastores {datastore.name}: {str(e)}")
                except Exception as e:
                    logger.error(f"Fehler bei der Verarbeitung des Datacenters {datacenter.name}: {str(e)}")
                    
            logger.info(f"Insgesamt {len(orphaned_vmdks)} verwaiste VMDKs gefunden")
            
            # Detaillierte Diagnoseausgabe
            if orphaned_vmdks:
                logger.info("\nVerwaiste VMDK-Details:")
                for i, vmdk in enumerate(orphaned_vmdks):
                    logger.info(f"Verwaiste VMDK {i+1}:")
                    for key, value in vmdk.items():
                        logger.info(f"  {key}: {value}")
            else:
                logger.warning("KEINE VERWAISTEN VMDKs GEFUNDEN!")
                
            return orphaned_vmdks
            
        except Exception as e:
            logger.error(f"Schwerwiegender Fehler bei der Erfassung verwaister VMDKs: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return self._collect_orphaned_vmdks_fallback()
            
    def _collect_orphaned_vmdks_fallback(self):
        """
        Fallback-Methode zur Sammlung von verwaisten VMDKs, verwendet den alten Ansatz
        """
        logger.info("Sammle Informationen über verwaiste VMDK-Dateien (Fallback-Methode)")
        
        try:
            # Sammle registrierte VMDKs mit traditionellem Ansatz
            registered_vmdks = set()
            vms = self.client.get_virtual_machines()
            
            for vm in vms:
                try:
                    # Überspringe Templates
                    if vm.config.template:
                        continue
                        
                    if vm.config and vm.config.hardware and vm.config.hardware.device:
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                if hasattr(device.backing, 'fileName'):
                                    registered_vmdks.add(device.backing.fileName)
                                    
                                    # Normalisierte Pfade für besseren Vergleich
                                    normalized_path = device.backing.fileName.lower().strip()
                                    registered_vmdks.add(normalized_path)
                                    
                                    # Pfade ohne Datastore-Klammern
                                    if normalized_path.startswith('['):
                                        parts = normalized_path.split('] ', 1)
                                        if len(parts) > 1:
                                            registered_vmdks.add(parts[1])
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten der VM {vm.name} für VMDKs: {str(e)}")
                    
            # Suche nach VMDKs in allen Datastores
            content = self.client.service_instance.content
            datacenters = [entity for entity in content.rootFolder.childEntity 
                          if isinstance(entity, vim.Datacenter)]
                          
            orphaned_vmdks = []
            
            for datacenter in datacenters:
                datastores = datacenter.datastore
                
                for datastore in datastores:
                    try:
                        # Datastore Browser abrufen
                        browser = datastore.browser
                        
                        # Suchspezifikation für VMDK-Dateien
                        search_spec = vim.HostDatastoreBrowserSearchSpec()
                        search_spec.matchPattern = ["*.vmdk"]
                        
                        # Suche nach VMDKs im Datastore
                        task = browser.SearchDatastoreSubFolders_Task("[" + datastore.name + "]", search_spec)
                        self.client.wait_for_task(task)
                        search_results = task.info.result
                        
                        # Verarbeite die Suchergebnisse
                        for result in search_results:
                            folder_path = result.folderPath
                            
                            for file_info in result.file:
                                try:
                                    if not file_info.path.lower().endswith('.vmdk'):
                                        continue
                                        
                                    # Vollständigen Pfad konstruieren
                                    full_path = folder_path + file_info.path
                                    
                                    # Prüfe, ob die VMDK verwaist ist
                                    if (full_path not in registered_vmdks and 
                                        full_path.lower() not in registered_vmdks):
                                        # Überspringe Hilfs-VMDK-Dateien
                                        if ("-flat.vmdk" in full_path.lower() or 
                                            "-delta.vmdk" in full_path.lower() or 
                                            "-ctk.vmdk" in full_path.lower() or
                                            "-rdm.vmdk" in full_path.lower() or
                                            "-sesparse.vmdk" in full_path.lower()):
                                            continue
                                            
                                        # Prüfe, ob die VMDK wirklich verwaist ist
                                        if self._is_vmdk_orphaned(folder_path, file_info.path):
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
                                    logger.error(f"Fehler bei der Verarbeitung der Datei: {str(e)}")
                    except Exception as e:
                        logger.error(f"Fehler bei der Verarbeitung des Datastores {datastore.name}: {str(e)}")
                        
            logger.info(f"Fallback-Methode fand {len(orphaned_vmdks)} verwaiste VMDKs")
            return orphaned_vmdks
            
        except Exception as e:
            logger.error(f"Schwerwiegender Fehler in der Fallback-Methode für verwaiste VMDKs: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return []
            
    def _is_vmdk_orphaned(self, folder_path, vmdk_name):
        """
        Prüfe, ob eine VMDK-Datei verwaist ist, indem nach zugehörigen VM-Dateien gesucht wird
        
        Definition: Eine VMDK ist verwaist, wenn sie keiner VM zugeordnet ist UND kein Template ist.
        
        Args:
            folder_path: Datastore-Verzeichnispfad
            vmdk_name: VMDK-Dateiname
            
        Returns:
            bool: True, wenn die VMDK verwaist zu sein scheint
        """
        try:
            # 1. Prüfe auf Hilfs-VMDKs, die automatisch ausgeschlossen werden sollten
            if ("-flat.vmdk" in vmdk_name.lower() or 
                "-delta.vmdk" in vmdk_name.lower() or 
                "-ctk.vmdk" in vmdk_name.lower() or
                "-rdm.vmdk" in vmdk_name.lower() or
                "-sesparse.vmdk" in vmdk_name.lower()):
                return False
                
            # 2. Extrahiere den Basisnamen (ohne Erweiterung)
            base_name = os.path.splitext(vmdk_name)[0]
            
            # 3. Suche nach zugehörigen VMX-Dateien im selben Verzeichnis
            content = self.client.service_instance.content
            
            # Datastore und Pfad extrahieren
            match = re.match(r'^\[(.*?)\] (.*?)$', folder_path)
            if not match:
                logger.error(f"Ungültiges Datastore-Pfadformat: {folder_path}")
                return True  # Im Zweifelsfall als verwaist markieren
                
            datastore_name = match.group(1)
            folder_relative_path = match.group(2)
            
            # Finde den Datastore
            datastores = [ds for dc in content.rootFolder.childEntity 
                         if isinstance(dc, vim.Datacenter) 
                         for ds in dc.datastore 
                         if ds.name == datastore_name]
                         
            if not datastores:
                logger.error(f"Datastore nicht gefunden: {datastore_name}")
                return True  # Im Zweifelsfall als verwaist markieren
                
            datastore = datastores[0]
            
            # Suche nach VMX-Dateien im selben Verzeichnis
            search_spec = vim.HostDatastoreBrowserSearchSpec()
            search_spec.matchPattern = ["*.vmx"]
            
            # Stelle sicher, dass der Pfad korrekt formatiert ist (ohne abschließenden Schrägstrich)
            search_path = folder_path
            if search_path.endswith('/'):
                search_path = search_path[:-1]
                
            # Führe die Suche durch
            try:
                task = datastore.browser.SearchDatastore_Task(search_path, search_spec)
                self.client.wait_for_task(task)
                search_result = task.info.result
                
                # Wenn VMX-Dateien gefunden wurden, prüfe, ob sie mit der VMDK zusammenhängen
                if search_result and search_result.file:
                    for vmx_file in search_result.file:
                        vmx_base_name = os.path.splitext(vmx_file.path)[0]
                        
                        # Wenn der VMDK-Name mit dem VMX-Namen übereinstimmt oder ähnlich ist,
                        # ist die VMDK wahrscheinlich nicht verwaist
                        if (base_name == vmx_base_name or 
                            base_name.startswith(vmx_base_name) or 
                            vmx_base_name.startswith(base_name)):
                            logger.info(f"VMDK {vmdk_name} gehört zu VMX {vmx_file.path}")
                            return False
            except Exception as e:
                logger.error(f"Fehler bei der Suche nach VMX-Dateien: {str(e)}")
                
            # Wenn keine passende VMX gefunden wurde, ist die VMDK wahrscheinlich verwaist
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Prüfung, ob VMDK verwaist ist: {str(e)}")
            return True  # Im Zweifelsfall als verwaist markieren

def export_to_json(data, filename):
    """Exportiere Daten in eine JSON-Datei"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, cls=CustomJSONEncoder, fp=f, indent=2, ensure_ascii=False)
        logger.info(f"Daten wurden erfolgreich in {filename} exportiert")
    except Exception as e:
        logger.error(f"Fehler beim Exportieren der Daten: {str(e)}")

class CustomJSONEncoder(json.JSONEncoder):
    """Benutzerdefinierter JSON-Encoder für Datetime-Objekte"""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

def run_diagnostics(args):
    """Führe Diagnose-Tools aus"""
    # Client initialisieren
    client = VSphereClient(args.server, args.username, args.password, args.ignore_ssl)
    
    # Mit vCenter verbinden
    if not client.connect():
        logger.error("Verbindung zum vCenter fehlgeschlagen. Diagnose-Tool wird beendet.")
        return 1
        
    try:
        # Datensammler initialisieren
        collector = DataCollector(client)
        
        # Daten sammeln je nach gewähltem Diagnose-Typ
        if args.diagnostic_type == 'snapshots' or args.diagnostic_type == 'all':
            logger.info("\n=== SNAPSHOT-DIAGNOSE ===")
            snapshots = collector.collect_snapshot_info()
            if snapshots:
                export_to_json(snapshots, f"snapshots_diagnosis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            else:
                logger.warning("Keine Snapshots gefunden!")
                
        if args.diagnostic_type == 'orphaned-vmdks' or args.diagnostic_type == 'all':
            logger.info("\n=== VERWAISTE VMDK-DIAGNOSE ===")
            orphaned_vmdks = collector.collect_orphaned_vmdks()
            if orphaned_vmdks:
                export_to_json(orphaned_vmdks, f"orphaned_vmdks_diagnosis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            else:
                logger.warning("Keine verwaisten VMDKs gefunden!")
                
        logger.info("\nDiagnose-Tool abgeschlossen. Siehe Log-Datei für Details.")
        return 0
        
    except Exception as e:
        logger.error(f"Unerwarteter Fehler im Diagnose-Tool: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1
        
    finally:
        # Verbindung trennen
        client.disconnect()

def main():
    """Haupteinstiegspunkt für das Diagnose-Tool"""
    parser = argparse.ArgumentParser(description="VMware vSphere Reporter - Diagnose-Tool für Snapshots und verwaiste VMDKs")
    
    parser.add_argument("--server", "-s", required=True, help="vCenter-Server-Adresse")
    parser.add_argument("--username", "-u", required=True, help="vCenter-Benutzername")
    parser.add_argument("--password", "-p", help="vCenter-Passwort (weglassen für sichere Eingabeaufforderung)")
    parser.add_argument("--ignore-ssl", "-k", action="store_true", help="SSL-Zertifikatvalidierung ignorieren")
    parser.add_argument("--diagnostic-type", "-t", choices=["snapshots", "orphaned-vmdks", "all"], 
                      default="all", help="Art der Diagnose (snapshots, orphaned-vmdks, oder all)")
    
    args = parser.parse_args()
    
    # Passwort sicher abfragen, wenn nicht angegeben
    if not args.password:
        args.password = getpass.getpass("vCenter-Passwort: ")
        
    # Debug-Modus für detaillierte Protokollierung aktivieren
    os.environ['VSPHERE_REPORTER_DEBUG'] = '1'
        
    # Diagnose-Tool ausführen
    return run_diagnostics(args)

if __name__ == "__main__":
    sys.exit(main())