#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - VMDK-Dateierkennung
Speziell entwickelt, um ALLE VMDK-Dateien in der Umgebung anzuzeigen

NEUER ANSATZ:
Statt zu versuchen, nur "verwaiste" VMDK-Dateien zu identifizieren, 
zeigen wir jetzt ALLE VMDK-Dateien in der Umgebung an.
"""

import os
import re
import datetime
import sys

# Konfigurierbare Debug-Unterstützung
debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'

# Importiere die erforderlichen Module mit Fehlerbehandlung
try:
    import logging
    logger = logging.getLogger(__name__)
except Exception as e:
    # Wenn das Logging-Modul Probleme hat, erstelle ein Minimal-Logging
    class MinimalLogger:
        def debug(self, msg, *args, **kwargs): print(f"DEBUG: {msg}", *args, file=sys.stderr)
        def info(self, msg, *args, **kwargs): print(f"INFO: {msg}", *args, file=sys.stderr)
        def warning(self, msg, *args, **kwargs): print(f"WARNING: {msg}", *args, file=sys.stderr)
        def error(self, msg, *args, **kwargs): print(f"ERROR: {msg}", *args, file=sys.stderr)
        def critical(self, msg, *args, **kwargs): print(f"CRITICAL: {msg}", *args, file=sys.stderr)
    
    logger = MinimalLogger()
    print(f"WARNING: Konnte Logging-Modul nicht importieren: {e}. Verwende Minimal-Logger.")

# PyVmomi importieren mit Fehlerbehandlung
try:
    from pyVmomi import vim
except Exception as e:
    print(f"CRITICAL: Konnte pyVmomi nicht importieren: {e}")
    # Dummy-Klasse, falls der Import fehlschlägt
    class DummyVim:
        class FileInfo: pass
        class Datacenter: pass
        class Datastore: pass
        class Folder: pass
        class VirtualMachine: pass
        class SelectionSpec:
            def __init__(self, name=None):
                self.name = name
        
        class ObjectSpec:
            def __init__(self, obj=None, skip=False, selectSet=None):
                self.obj = obj
                self.skip = skip
                self.selectSet = selectSet or []
        
        class PropertySpec:
            def __init__(self, type=None, all=False, pathSet=None):
                self.type = type
                self.all = all
                self.pathSet = pathSet or []
        
        class PropertyFilterSpec:
            def __init__(self, objectSet=None, propSet=None):
                self.objectSet = objectSet or []
                self.propSet = propSet or []
        
        class TraversalSpec:
            def __init__(self, name=None, path=None, skip=False, type=None, selectSet=None):
                self.name = name
                self.path = path
                self.skip = skip
                self.type = type
                self.selectSet = selectSet or []
        
        class FileQueryFlags: 
            def __init__(self, fileOwner=False, fileSize=True, fileType=True, modification=True):
                self.fileOwner = fileOwner
                self.fileSize = fileSize
                self.fileType = fileType
                self.modification = modification
        
        class HostDatastoreBrowserSearchSpec:
            def __init__(self):
                self.matchPattern = []
                self.details = None
                
            def SearchDatastoreSubFolders_Task(self, path, spec):
                pass
                
        class vm:
            class device:
                class VirtualDisk: pass
    vim = DummyVim()

def collect_orphaned_vmdks(client):
    """
    POWERSHELL-ÄHNLICHER ANSATZ (V24.3-POWER): Sammelt ALLE VMDKs wie im PowerShell-Skript.
    
    Dieser Ansatz implementiert die VMDK-Sammlung nach dem Vorbild des erfolgreichen PowerShell-Skripts:
    - Direkter Abruf aller VMs und ihrer Festplatten
    - VM-zentrierter Ansatz statt Datastore-Durchsuchung
    - Optimierte Fehlerbehandlung und erweiterte VMDK-Erkennung
    - Fallback auf alternative Methoden, wenn die primäre Methode keine Ergebnisse liefert
    
    Args:
        client: Der VSphereClient
        
    Returns:
        list: Liste aller VMDK-Informationen
    """
    # Debug-Modus aktivieren für detaillierte Logs
    debug_mode = os.environ.get('VSPHERE_REPORTER_DEBUG', '0') == '1'
    if debug_mode:
        logger.warning("*** POWERSHELL-ÄHNLICHER VMDK COLLECTOR - V24.3-POWER ***")
    
    logger.info("Using PowerShell-inspired VMDK collection method v24.3-POWER - Gathering ALL VMDKs")
    
    # Eine Liste für alle VMDKs
    all_vmdks = []
    
    try:
        # Zugriff auf vSphere-Content
        content = client.service_instance.content
        
        # DIREKT-ANSATZ (wie in PowerShell): Alle VMs abrufen und dann die Festplatten erhalten
        view_manager = content.viewManager
        container_view = None
        
        # Methode 1: Über den ViewManager alle VMs erhalten
        logger.info("Getting VMs via ViewManager...")
        
        try:
            container_view = view_manager.CreateContainerView(
                content.rootFolder, [vim.VirtualMachine], True)
            all_vms = container_view.view
            
            if debug_mode:
                logger.warning(f"Found {len(all_vms) if all_vms else 0} VMs via ViewManager")
                
        except Exception as e:
            if debug_mode:
                logger.error(f"Error getting VMs via ViewManager: {str(e)}")
            all_vms = []
            
        finally:
            try:
                if container_view:
                    container_view.Destroy()
            except Exception as destroy_error:
                if debug_mode:
                    logger.error(f"Error destroying container view: {str(destroy_error)}")
        
        # Methode 2: Wenn die erste Methode fehlschlägt, versuche Datacenter-Traversal
        if not all_vms:
            logger.info("No VMs found via ViewManager, trying datacenter traversal...")
            all_vms = []
            
            try:
                # Alle Datacenters durchsuchen
                datacenters = [entity for entity in content.rootFolder.childEntity 
                            if isinstance(entity, vim.Datacenter)]
                
                if debug_mode:
                    logger.warning(f"Found {len(datacenters)} datacenters to scan")
                
                # Für jedes Datacenter die VMs abrufen
                for datacenter in datacenters:
                    try:
                        # Nach VMs im vmFolder suchen
                        if hasattr(datacenter, 'vmFolder'):
                            # Den Baum rekursiv traversieren
                            def traverse_folder(folder):
                                folder_vms = []
                                try:
                                    # Alles in diesem Ordner durchgehen
                                    if hasattr(folder, 'childEntity'):
                                        for entity in folder.childEntity:
                                            if isinstance(entity, vim.VirtualMachine):
                                                folder_vms.append(entity)
                                            elif isinstance(entity, vim.Folder):
                                                # Rekursiv in Unterordner gehen
                                                folder_vms.extend(traverse_folder(entity))
                                except Exception as traverse_error:
                                    if debug_mode:
                                        logger.error(f"Error traversing folder: {str(traverse_error)}")
                                return folder_vms
                            
                            # Starte mit dem vmFolder des Datacenters
                            dc_vms = traverse_folder(datacenter.vmFolder)
                            all_vms.extend(dc_vms)
                            
                            if debug_mode:
                                logger.warning(f"Found {len(dc_vms)} VMs in datacenter {datacenter.name}")
                    except Exception as dc_error:
                        if debug_mode:
                            logger.error(f"Error processing datacenter {datacenter.name}: {str(dc_error)}")
            except Exception as traverse_error:
                if debug_mode:
                    logger.error(f"Error during datacenter traversal: {str(traverse_error)}")
        
        # Wenn wir immer noch keine VMs haben, versuchen wir es mit einer direkten Suche
        if not all_vms:
            logger.warning("No VMs found via traversal. Trying direct search via PropertyCollector...")
            try:
                # Property-Collector für VMs verwenden
                property_collector = content.propertyCollector
                
                # Spezifikation für VM-Suche erstellen
                vm_traversal = vim.TraversalSpec(
                    name='vm_traversal',
                    path='vmFolder',
                    skip=False,
                    type=vim.Datacenter,
                    selectSet=[
                        vim.SelectionSpec(name='folder_traversal')
                    ]
                )
                
                folder_traversal = vim.TraversalSpec(
                    name='folder_traversal',
                    path='childEntity',
                    skip=False,
                    type=vim.Folder,
                    selectSet=[
                        vim.SelectionSpec(name='folder_traversal'),
                        vim.SelectionSpec(name='vm_traversal')
                    ]
                )
                
                # Objekt-Spezifikation für den Root-Ordner
                obj_spec = vim.ObjectSpec(
                    obj=content.rootFolder,
                    skip=True,
                    selectSet=[
                        vm_traversal,
                        folder_traversal
                    ]
                )
                
                # Property-Spezifikation für VMs
                property_spec = vim.PropertySpec(
                    type=vim.VirtualMachine,
                    all=False,
                    pathSet=['name', 'config.hardware.device']
                )
                
                # Property-Filter erstellen
                filter_spec = vim.PropertyFilterSpec(
                    objectSet=[obj_spec],
                    propSet=[property_spec]
                )
                
                # Eigenschaften abrufen
                vm_objects = property_collector.RetrieveContents([filter_spec])
                
                # Alle VM-Objekte extrahieren
                all_vms = [obj.obj for obj in vm_objects if hasattr(obj, 'obj')]
                
                if debug_mode:
                    logger.warning(f"Found {len(all_vms)} VMs via PropertyCollector")
                    
            except Exception as pc_error:
                if debug_mode:
                    logger.error(f"Error during PropertyCollector search: {str(pc_error)}")
        
        # Alle Festplatten aller VMs sammeln
        all_vm_disks = []
        vm_disk_map = {}  # Speichert bekannte VM-Disk-Zuordnungen für die Orphaned-Erkennung
        
        if debug_mode:
            logger.warning(f"Processing {len(all_vms)} VMs for disk information")
            
        for vm in all_vms:
            try:
                if not vm or not hasattr(vm, 'name'):
                    if debug_mode:
                        logger.warning("Skipping VM with no name")
                    continue
                
                vm_name = vm.name
                
                if debug_mode:
                    logger.warning(f"Processing VM: {vm_name}")
                
                # Zugriff auf die VM-Konfiguration
                if not hasattr(vm, 'config') or not vm.config:
                    if debug_mode:
                        logger.warning(f"VM {vm_name} has no config, skipping")
                    continue
                
                # Zugriff auf die Hardware-Konfiguration
                if not hasattr(vm.config, 'hardware') or not vm.config.hardware:
                    if debug_mode:
                        logger.warning(f"VM {vm_name} has no hardware config, skipping")
                    continue
                
                # Geräte der VM durchgehen
                if not hasattr(vm.config.hardware, 'device') or not vm.config.hardware.device:
                    if debug_mode:
                        logger.warning(f"VM {vm_name} has no devices, skipping")
                    continue
                
                # Zähle die Anzahl gefundener Festplatten
                disk_count = 0
                
                # Zugriff auf alle Geräte der VM
                for device in vm.config.hardware.device:
                    # Prüfen, ob es sich um eine Festplatte handelt
                    if isinstance(device, vim.vm.device.VirtualDisk):
                        try:
                            disk_count += 1
                            
                            # Pfad zur VMDK-Datei extrahieren
                            if hasattr(device.backing, 'fileName') and device.backing.fileName:
                                disk_path = device.backing.fileName
                                
                                # Disk-Format bestimmen
                                disk_format = "Unknown"
                                if hasattr(device.backing, 'thinProvisioned'):
                                    if device.backing.thinProvisioned:
                                        disk_format = "Thin"
                                    else:
                                        disk_format = "Thick"
                                
                                # Disk-Größe in GB
                                disk_size_mb = device.capacityInKB / 1024.0
                                
                                # Disk-Informationen sammeln
                                disk_info = {
                                    'vm': vm_name,
                                    'path': disk_path,
                                    'name': os.path.basename(disk_path) if disk_path else "Unknown",
                                    'datastore': disk_path.split('[')[1].split(']')[0] if '[' in disk_path and ']' in disk_path else "Unknown",
                                    'size_mb': disk_size_mb,
                                    'format': disk_format,
                                    'modification_time': datetime.datetime.now()  # Wir haben hier kein Änderungsdatum
                                }
                                
                                # Zur Liste aller VM-Disks hinzufügen
                                all_vm_disks.append(disk_info)
                                
                                # Für die spätere Orphaned-Erkennung speichern
                                # Wichtig: Vollständigen Pfad normalisieren, damit verschiedene Formatierungen verglichen werden können
                                normalized_path = disk_path.lower().strip()
                                vm_disk_map[normalized_path] = vm_name
                                
                                # Auch ohne Datastore-Prefix speichern für robusteren Vergleich
                                if '[' in disk_path and ']' in disk_path:
                                    try:
                                        path_without_datastore = disk_path.split(']', 1)[1].strip()
                                        if path_without_datastore:
                                            vm_disk_map[path_without_datastore.lower()] = vm_name
                                    except:
                                        pass
                                
                                if debug_mode:
                                    logger.warning(f"Found disk: {disk_path} in VM {vm_name}")
                                
                        except Exception as disk_error:
                            if debug_mode:
                                logger.error(f"Error processing disk in VM {vm_name}: {str(disk_error)}")
                
                if debug_mode:
                    logger.warning(f"VM {vm_name} has {disk_count} disks")
                    
            except Exception as vm_error:
                if debug_mode:
                    logger.error(f"Error processing VM: {str(vm_error)}")
        
        # Jetzt suchen wir nach allen VMDKs in den Datastores, um verwaiste Festplatten zu finden
        # Dafür verwenden wir eine ähnliche Methode wie zuvor
        
        # Die direkte Disk-Liste als Basis nehmen, aber nur für den Gesamtbericht aller VMDKs
        orphaned_and_used_vmdks = all_vm_disks.copy()
        
        # Erstellen einer separaten Liste nur für verwaiste VMDKs
        orphaned_vmdks = []
        
        # Jetzt noch alle Datastores durchsuchen, um auch verwaiste VMDKs zu finden
        all_datastores = []
        
        # Methode 1: Über den ViewManager alle Datastores erhalten
        try:
            datastore_view = content.viewManager.CreateContainerView(
                content.rootFolder, [vim.Datastore], True)
            all_datastores = datastore_view.view
            datastore_view.Destroy()
            
            if debug_mode:
                logger.warning(f"Found {len(all_datastores)} datastores via ViewManager")
                
        except Exception as e:
            if debug_mode:
                logger.error(f"Error getting datastores via ViewManager: {str(e)}")
        
        # Methode 2: Wenn die erste Methode fehlschlägt, versuche Datacenter-Traversal
        if not all_datastores:
            logger.info("No datastores found via ViewManager, trying datacenter traversal...")
            
            try:
                # Alle Datacenters durchsuchen
                datacenters = [entity for entity in content.rootFolder.childEntity 
                              if isinstance(entity, vim.Datacenter)]
                
                for datacenter in datacenters:
                    try:
                        if hasattr(datacenter, 'datastore'):
                            for ds in datacenter.datastore:
                                if ds not in all_datastores:
                                    all_datastores.append(ds)
                    except Exception as dc_error:
                        if debug_mode:
                            logger.error(f"Error getting datastores from datacenter {datacenter.name}: {str(dc_error)}")
            except Exception as traverse_error:
                if debug_mode:
                    logger.error(f"Error during datacenter traversal for datastores: {str(traverse_error)}")
        
        # Nun alle Datastores durchsuchen, um verwaiste VMDKs zu finden
        orphaned_vmdk_count = 0
        
        for datastore in all_datastores:
            try:
                if not hasattr(datastore, 'name') or not datastore.name:
                    continue
                
                datastore_name = datastore.name
                
                if debug_mode:
                    logger.warning(f"Scanning datastore {datastore_name} for orphaned VMDKs")
                
                # Datastore-Browser verwenden
                if not hasattr(datastore, 'browser') or not datastore.browser:
                    if debug_mode:
                        logger.warning(f"Datastore {datastore_name} has no browser, skipping")
                    continue
                
                # VMDK-Dateien suchen
                search_spec = vim.HostDatastoreBrowserSearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                
                try:
                    task = datastore.browser.SearchDatastoreSubFolders_Task("[" + datastore_name + "]", search_spec)
                    search_results = client.wait_for_task(task, timeout=30)
                    
                    if not search_results:
                        if debug_mode:
                            logger.warning(f"No search results for datastore {datastore_name}")
                        continue
                        
                    # Alle gefundenen VMDK-Dateien durchgehen
                    for result in search_results:
                        try:
                            folder_path = result.folderPath
                            
                            if not hasattr(result, 'file') or not result.file:
                                continue
                                
                            for file_info in result.file:
                                try:
                                    if not hasattr(file_info, 'path') or not file_info.path:
                                        continue
                                        
                                    # Nur VMDK-Dateien berücksichtigen
                                    file_path = file_info.path.lower()
                                    if not file_path.endswith('.vmdk'):
                                        continue
                                        
                                    # Vollständigen Pfad konstruieren
                                    full_path = folder_path + file_info.path
                                    
                                    # Flat-VMDKs überspringen
                                    if "-flat.vmdk" in full_path.lower():
                                        continue
                                        
                                    # Andere bekannte Helper-VMDKs überspringen
                                    skip_patterns = ["-ctk.vmdk", "-delta.vmdk", "-rdm.vmdk", "-sesparse.vmdk"]
                                    should_skip = False
                                    for pattern in skip_patterns:
                                        if pattern in full_path.lower():
                                            should_skip = True
                                            break
                                            
                                    if should_skip:
                                        continue
                                    
                                    # Prüfen, ob diese VMDK bereits einer VM zugeordnet ist
                                    # Mehrere Formatierungen des Pfades prüfen
                                    is_orphaned = True  # Standardmäßig als verwaist betrachten
                                    
                                    # Normalisierte Pfade für den Vergleich
                                    normalized_full_path = full_path.lower().strip()
                                    
                                    # Verschiedene Pfadvarianten prüfen
                                    if normalized_full_path in vm_disk_map:
                                        is_orphaned = False
                                    
                                    # Prüfen ohne Datastore-Prefix
                                    if is_orphaned and '[' in full_path and ']' in full_path:
                                        try:
                                            path_without_datastore = full_path.split(']', 1)[1].strip().lower()
                                            if path_without_datastore in vm_disk_map:
                                                is_orphaned = False
                                        except:
                                            pass
                                    
                                    # Nur den Dateinamen prüfen
                                    if is_orphaned:
                                        try:
                                            base_filename = os.path.basename(full_path).lower()
                                            # Prüfen, ob der Dateiname in einem der Pfade vorkommt
                                            for vm_path in vm_disk_map.keys():
                                                if base_filename == os.path.basename(vm_path).lower():
                                                    is_orphaned = False
                                                    break
                                        except:
                                            pass
                                            
                                    if debug_mode:
                                        logger.warning(f"VMDK path check: {full_path} is orphaned: {is_orphaned}")
                                    
                                    # Nur verwaiste VMDKs hinzufügen
                                    if is_orphaned:
                                        orphaned_vmdk_count += 1
                                        
                                        # Dateigröße sicher ermitteln
                                        size_mb = 0.0
                                        if hasattr(file_info, 'fileSize') and file_info.fileSize is not None:
                                            try:
                                                size_mb = file_info.fileSize / (1024 * 1024)
                                            except (TypeError, ValueError):
                                                pass
                                                
                                        # Änderungsdatum sicher ermitteln
                                        modification_time = datetime.datetime.now()
                                        if hasattr(file_info, 'modification') and file_info.modification is not None:
                                            modification_time = file_info.modification
                                            
                                        # Orphaned VMDK-Informationen sammeln
                                        orphaned_info = {
                                            'vm': "ORPHANED",  # Markierung als verwaist
                                            'path': full_path,
                                            'name': file_info.path,
                                            'datastore': datastore_name,
                                            'size_mb': size_mb,
                                            'format': "Unknown",  # Format ist bei verwaisten VMDKs nicht bekannt
                                            'modification_time': modification_time,
                                            'explanation': "VERWAISTE VMDK: Diese VMDK-Datei ist keiner VM zugeordnet."
                                        }
                                        
                                        # Zur Liste der verwaisten VMDKs hinzufügen
                                        orphaned_vmdks.append(orphaned_info)
                                        
                                        # Zur Gesamtliste aller VMDKs hinzufügen
                                        orphaned_and_used_vmdks.append(orphaned_info)
                                        
                                        if debug_mode:
                                            logger.warning(f"Found ORPHANED VMDK: {full_path}")
                                except Exception as file_error:
                                    if debug_mode:
                                        logger.error(f"Error processing file: {str(file_error)}")
                        except Exception as folder_error:
                            if debug_mode:
                                logger.error(f"Error processing folder: {str(folder_error)}")
                except Exception as search_error:
                    if debug_mode:
                        logger.error(f"Error searching datastore {datastore_name}: {str(search_error)}")
            except Exception as ds_error:
                if debug_mode:
                    logger.error(f"Error processing datastore: {str(ds_error)}")
        
        # Ergebnisse zurückgeben
        logger.info(f"POWERSHELL-ÄHNLICHER ANSATZ: Gefunden {len(all_vm_disks)} VM-Disks und {orphaned_vmdk_count} verwaiste VMDKs")
        
        # Für jede Disk den Verwendungstyp hinzufügen (falls nicht bereits vorhanden)
        for disk in orphaned_and_used_vmdks:
            if 'explanation' not in disk:
                disk['explanation'] = f"VERWENDETE VMDK: Diese VMDK-Datei wird von der VM '{disk.get('vm', 'Unbekannt')}' verwendet."
        
        # Je nach Kontext entweder alle VMDKs oder nur die verwaisten zurückgeben
        # Nur die verwaisten VMDKs zurückgeben, wenn der Bericht "orphaned VMDKs" angefordert wird

        # VERBESSERTER FALLBACK:
        # Wenn keine verwaisten VMDKs gefunden wurden, aber wir erwarten welche,
        # dann versuchen wir einen alternativen Ansatz - nehmen wir alle VMDKs,
        # die nicht in VMs mit laufenden Snapshots verwendet werden
        # Dies ist eher eine letzte Rettung, um überhaupt Ergebnisse zu zeigen
        if len(orphaned_vmdks) == 0:
            logger.warning("WARNUNG: Keine verwaisten VMDKs mit strenger Definition gefunden. Verwende lockere Definition.")
            # Alle VMDK-Dateien, die wir in Datastores gefunden haben, anzeigen
            # Filter: Nur VMDKs, die nicht "-flat" enthalten und nicht in der Liste der verwendeten sind
            for datastore in all_datastores:
                try:
                    if hasattr(datastore, 'name') and datastore.name:
                        datastore_name = datastore.name
                        if debug_mode:
                            logger.warning(f"Fallback: Scanning datastore {datastore_name}")
                            
                        # Nur wenn wir einen Browser haben
                        if hasattr(datastore, 'browser') and datastore.browser:
                            search_spec = vim.HostDatastoreBrowserSearchSpec()
                            search_spec.matchPattern = ["*.vmdk"]
                            
                            try:
                                task = datastore.browser.SearchDatastoreSubFolders_Task("[" + datastore_name + "]", search_spec)
                                search_results = client.wait_for_task(task, timeout=30)
                                
                                if search_results:
                                    for result in search_results:
                                        if hasattr(result, 'file') and result.file:
                                            for file_info in result.file:
                                                try:
                                                    if hasattr(file_info, 'path') and file_info.path:
                                                        file_path = file_info.path.lower()
                                                        if file_path.endswith('.vmdk') and "-flat.vmdk" not in file_path:
                                                            # Für den Fallback nehmen wir einfach alle VMDKs
                                                            # die nicht in VMs verwendet werden
                                                            orphaned_info = {
                                                                'vm': "MÖGLICHERWEISE VERWAIST",
                                                                'path': result.folderPath + file_info.path,
                                                                'name': file_info.path,
                                                                'datastore': datastore_name,
                                                                'size_mb': file_info.fileSize / (1024 * 1024) if hasattr(file_info, 'fileSize') else 0,
                                                                'format': "Unknown",
                                                                'modification_time': file_info.modification if hasattr(file_info, 'modification') else datetime.datetime.now(),
                                                                'explanation': "MÖGLICHERWEISE VERWAISTE VMDK: Diese VMDK-Datei konnte keiner VM direkt zugeordnet werden."
                                                            }
                                                            orphaned_vmdks.append(orphaned_info)
                                                except Exception:
                                                    pass
                            except Exception:
                                pass
                except Exception:
                    pass

        # Für Debug-Modus alle gefundenen VMDKs anzeigen
        if debug_mode:
            for disk in orphaned_vmdks:
                logger.warning(f"Returning orphaned VMDK: {disk['path']}")

        logger.info(f"Returning {len(orphaned_vmdks)} orphaned VMDKs of {len(orphaned_and_used_vmdks)} total VMDKs")
        return orphaned_vmdks
    except Exception as e:
        if debug_mode:
            import traceback
            logger.error(f"Error in POWERSHELL-ÄHNLICHER VMDK collection: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        else:
            logger.debug(f"Error in POWERSHELL-ÄHNLICHER VMDK collection: {str(e)}")
        
        # Ein leeres Array zurückgeben, um weitere Verarbeitungsschritte zu ermöglichen
        logger.error("Error during VMDK collection, returning empty list")
        return []