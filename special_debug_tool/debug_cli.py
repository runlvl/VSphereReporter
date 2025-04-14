#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Standalone Debug CLI
Optimized for diagnosing snapshot and orphaned VMDK issues
"""

import os
import sys
import time
import logging
import argparse
import getpass
import datetime
import traceback
from contextlib import contextmanager

# Aktiviere den Debug-Modus für detaillierte Fehlerausgabe
os.environ['VSPHERE_REPORTER_DEBUG'] = '1'

# Konfiguriere das Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vsphere_debug.log')
    ]
)
logger = logging.getLogger("vsphere_debug")

try:
    # Importiere PyVmomi wenn verfügbar
    import ssl
    from pyVim.connect import SmartConnect, Disconnect
    from pyVmomi import vim
except ImportError:
    logger.critical("PyVmomi ist nicht installiert. Bitte installieren mit: pip install pyVmomi")
    print("\nFehler: PyVmomi-Bibliothek nicht gefunden.")
    print("Bitte installieren Sie PyVmomi mit folgendem Befehl:")
    print("    pip install pyVmomi")
    sys.exit(1)

@contextmanager
def suppress_stdout_stderr():
    """
    Context manager zum Unterdrücken von stdout/stderr Ausgaben
    Im Debug-Modus werden Ausgaben nicht unterdrückt
    """
    class DummyContext:
        def __enter__(self):
            return None
        def __exit__(self, exc_type, exc_val, exc_tb):
            return False
    
    yield DummyContext()

class VSphereClient:
    """Einfacher vSphere-Client für CLI-Zugriff"""
    
    def __init__(self, host, user, password, ignore_ssl=False):
        """Initialisiere den Client mit Verbindungsparametern"""
        self.host = host
        self.user = user
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.content = None
        self.connection = None
        
    def connect(self):
        """Verbindung zum vCenter herstellen"""
        try:
            if self.ignore_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                context.verify_mode = ssl.CERT_NONE
            else:
                context = None
                
            logger.info(f"Verbindung zu {self.host} herstellen...")
            self.connection = SmartConnect(
                host=self.host,
                user=self.user,
                pwd=self.password,
                sslContext=context
            )
            
            if not self.connection:
                raise Exception("Verbindung konnte nicht hergestellt werden")
                
            self.content = self.connection.content
            logger.info(f"Verbindung zu {self.host} hergestellt")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Verbindung zu {self.host}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def disconnect(self):
        """Trennen vom vCenter"""
        if self.connection:
            Disconnect(self.connection)
            self.connection = None
            self.content = None
            logger.info(f"Verbindung zu {self.host} getrennt")
            
    def wait_for_task(self, task):
        """
        Warten auf den Abschluss einer vCenter-Aufgabe
        
        Args:
            task: Die Aufgabe, auf die gewartet werden soll
            
        Returns:
            Task-Ergebnis
        """
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            time.sleep(0.5)
            
        if task.info.state == vim.TaskInfo.State.error:
            logger.error(f"Task fehlgeschlagen: {task.info.error}")
            raise task.info.error
            
        return task.info.result

class DataCollector:
    """Collector für vSphere-Umgebungsdaten mit Fokus auf Snapshots und verwaiste VMDKs"""
    
    def __init__(self, vsphere_client):
        """
        Initialisiere den Datensammler
        
        Args:
            vsphere_client: Verbundener vSphere-Client
        """
        self.vsphere_client = vsphere_client
        
    def collect_snapshot_info(self):
        """
        Sammle Informationen über VM-Snapshots
        
        Returns:
            list: Liste von Snapshot-Informationsdictionaries, sortiert nach Alter (älteste zuerst)
        """
        try:
            snapshot_list = []
            
            # Erhalte eine Liste aller VMs
            container = self.vsphere_client.content.viewManager.CreateContainerView(
                self.vsphere_client.content.rootFolder, [vim.VirtualMachine], True)
            vms = container.view
            container.Destroy()
            
            for vm in vms:
                with suppress_stdout_stderr():
                    try:
                        # Überspringe, wenn VM keine Snapshots hat
                        if not vm.snapshot:
                            continue
                        
                        # Verarbeite Snapshot-Baum
                        vm_snapshots = self._get_vm_snapshots(vm)
                        snapshot_list.extend(vm_snapshots)
                        
                    except Exception as e:
                        logger.error(f"Fehler beim Sammeln von Snapshot-Informationen für {vm.name}: {str(e)}")
                        logger.error(traceback.format_exc())
                        continue
                        
            # Sortiere Snapshots nach Alter (älteste zuerst)
            snapshot_list.sort(key=lambda x: x['create_time'])
            
            if not snapshot_list:
                logger.warning("Keine Snapshots gefunden. Verwende Fallback-Methode.")
                return self._collect_snapshot_info_fallback()
                
            return snapshot_list
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von Snapshot-Informationen: {str(e)}")
            logger.error(traceback.format_exc())
            
            return self._collect_snapshot_info_fallback()
    
    def _collect_snapshot_info_fallback(self):
        """
        Fallback-Methode zur Snapshot-Sammlung, verwendet den alten Ansatz
        """
        snapshot_list = []
        
        try:
            # Erhalte eine Liste aller VMs
            container = self.vsphere_client.content.viewManager.CreateContainerView(
                self.vsphere_client.content.rootFolder, [vim.VirtualMachine], True)
            vms = container.view
            container.Destroy()
            
            current_time = datetime.datetime.now()
            
            for vm in vms:
                with suppress_stdout_stderr():
                    # Direkter Zugriff auf die Snapshot-Eigenschaft
                    if not hasattr(vm, 'snapshot') or not vm.snapshot:
                        continue
                    
                    if not hasattr(vm.snapshot, 'rootSnapshotList') or not vm.snapshot.rootSnapshotList:
                        continue
                    
                    for snap in vm.snapshot.rootSnapshotList:
                        try:
                            # Basisinformationen erfassen
                            create_time = snap.createTime
                            age_days = (current_time - create_time).days
                            
                            snapshot_info = {
                                'vm_name': vm.name,
                                'name': snap.name,
                                'description': snap.description,
                                'create_time': create_time,
                                'age_days': age_days,
                                'id': snap.id,
                                'state': snap.state,
                                'size_mb': 0  # Größe ist in dieser Fallback-Methode nicht verfügbar
                            }
                            
                            snapshot_list.append(snapshot_info)
                            
                        except Exception as e:
                            logger.error(f"Fehler bei Snapshot {snap.name} für VM {vm.name}: {str(e)}")
                            logger.error(traceback.format_exc())
                            continue
            
            # Sortiere Snapshots nach Alter (älteste zuerst)
            snapshot_list.sort(key=lambda x: x['create_time'])
            
            return snapshot_list
            
        except Exception as e:
            logger.error(f"Fehler in der Fallback-Methode für Snapshots: {str(e)}")
            logger.error(traceback.format_exc())
            
            return []
    
    def _get_vm_snapshots(self, vm):
        """
        Erhalte Snapshot-Informationen für eine VM
        
        Args:
            vm: Virtual Machine-Objekt
            
        Returns:
            list: Liste von Snapshot-Informationsdictionaries
        """
        snapshots = []
        
        if not vm.snapshot:
            return snapshots
        
        # Verarbeite die Root-Snapshots
        return self._get_snapshot_tree(vm, vm.snapshot.rootSnapshotList)
    
    def _get_snapshot_tree(self, vm, snapshot_list):
        """
        Verarbeite den Snapshot-Baum rekursiv
        
        Args:
            vm: Virtual Machine-Objekt
            snapshot_list: Liste von Snapshot-Objekten
            
        Returns:
            list: Verarbeitete Liste von Snapshot-Informationsdictionaries
        """
        current_time = datetime.datetime.now()
        result = []
        
        for snapshot in snapshot_list:
            try:
                create_time = snapshot.createTime
                age_days = (current_time - create_time).days
                
                snapshot_info = {
                    'vm_name': vm.name,
                    'name': snapshot.name,
                    'description': snapshot.description,
                    'create_time': create_time,
                    'age_days': age_days,
                    'id': snapshot.id,
                    'state': snapshot.state,
                    'size_mb': 0  # Snapshot-Größe ist nicht direkt über die API verfügbar
                }
                
                result.append(snapshot_info)
                
                # Verarbeite Kind-Snapshots
                if snapshot.childSnapshotList:
                    child_snapshots = self._get_snapshot_tree(vm, snapshot.childSnapshotList)
                    result.extend(child_snapshots)
            
            except Exception as e:
                logger.error(f"Fehler bei Snapshot {snapshot.name} für VM {vm.name}: {str(e)}")
                logger.error(traceback.format_exc())
                continue
                
        return result
    
    def collect_orphaned_vmdks(self):
        """
        Sammle Informationen über verwaiste VMDK-Dateien
        
        Returns:
            list: Liste von verwaisten VMDK-Informationsdictionaries
        """
        try:
            orphaned_vmdks = []
            
            # Erhalte alle Datastores
            container = self.vsphere_client.content.viewManager.CreateContainerView(
                self.vsphere_client.content.rootFolder, [vim.Datastore], True)
            datastores = container.view
            container.Destroy()
            
            # Erhalte alle VMs, um angehängte Disks zu überprüfen
            vm_container = self.vsphere_client.content.viewManager.CreateContainerView(
                self.vsphere_client.content.rootFolder, [vim.VirtualMachine], True)
            vms = vm_container.view
            vm_container.Destroy()
            
            # Erhalte alle verwendeten VMDKs
            used_vmdks = set()
            for vm in vms:
                with suppress_stdout_stderr():
                    try:
                        if not vm.config or not vm.config.hardware.device:
                            continue
                            
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                if device.backing and hasattr(device.backing, 'fileName'):
                                    used_vmdks.add(device.backing.fileName)
                    except Exception as e:
                        logger.error(f"Fehler beim Prüfen von VM {vm.name}: {str(e)}")
                        logger.error(traceback.format_exc())
                        continue
            
            # Suche nach allen VMDK-Dateien in Datastores
            for ds in datastores:
                with suppress_stdout_stderr():
                    try:
                        browser = ds.browser
                        ds_path = f"[{ds.name}]"
                        
                        search_spec = vim.HostDatastoreBrowserSearchSpec()
                        search_spec.matchPattern = ["*.vmdk"]
                        
                        task = browser.SearchDatastoreSubFolders_Task(ds_path, search_spec)
                        self.vsphere_client.wait_for_task(task)
                        
                        for folder_result in task.info.result:
                            folder_path = folder_result.folderPath
                            
                            # Überspringe, wenn keine Dateien gefunden wurden
                            if not folder_result.file:
                                continue
                                
                            for file_info in folder_result.file:
                                if not isinstance(file_info, vim.host.DatastoreBrowser.FileInfo):
                                    continue
                                    
                                # Überspringe, wenn keine VMDK-Datei
                                if not file_info.path.endswith('.vmdk'):
                                    continue
                                    
                                # Überspringe, wenn dies eine Delta-Disk oder Metadatendatei ist
                                if '-delta.vmdk' in file_info.path or '-flat.vmdk' in file_info.path or '-ctk.vmdk' in file_info.path:
                                    continue
                                    
                                # Prüfe, ob diese VMDK verwaist ist
                                full_path = folder_path + file_info.path
                                if full_path not in used_vmdks and self._is_vmdk_orphaned(folder_path, file_info.path):
                                    # Dies ist eine verwaiste VMDK
                                    orphaned_info = {
                                        'path': full_path,
                                        'size_mb': file_info.fileSize / (1024 * 1024),
                                        'modify_time': file_info.modification
                                    }
                                    orphaned_vmdks.append(orphaned_info)
                                    
                    except Exception as e:
                        logger.error(f"Fehler beim Durchsuchen von Datastore {ds.name}: {str(e)}")
                        logger.error(traceback.format_exc())
                        continue
                        
            if not orphaned_vmdks:
                logger.warning("Keine verwaisten VMDKs gefunden. Verwende Fallback-Methode.")
                return self._collect_orphaned_vmdks_fallback()
                
            return orphaned_vmdks
            
        except Exception as e:
            logger.error(f"Fehler beim Sammeln von verwaisten VMDK-Informationen: {str(e)}")
            logger.error(traceback.format_exc())
            
            return self._collect_orphaned_vmdks_fallback()
    
    def _collect_orphaned_vmdks_fallback(self):
        """
        Fallback-Methode zur Sammlung von verwaisten VMDKs, verwendet den alten Ansatz
        """
        orphaned_vmdks = []
        
        try:
            # Erhalte alle Datastores
            container = self.vsphere_client.content.viewManager.CreateContainerView(
                self.vsphere_client.content.rootFolder, [vim.Datastore], True)
            datastores = container.view
            container.Destroy()
            
            # Vereinfachter Ansatz: Suche nach VMDKs ohne zugehörige VMX-Datei im selben Verzeichnis
            for ds in datastores:
                with suppress_stdout_stderr():
                    try:
                        browser = ds.browser
                        ds_path = f"[{ds.name}]"
                        
                        # Alle VMDKs suchen
                        vmdk_spec = vim.HostDatastoreBrowserSearchSpec()
                        vmdk_spec.matchPattern = ["*.vmdk"]
                        
                        vmdk_task = browser.SearchDatastoreSubFolders_Task(ds_path, vmdk_spec)
                        self.vsphere_client.wait_for_task(vmdk_task)
                        
                        # Alle VMX-Dateien suchen
                        vmx_spec = vim.HostDatastoreBrowserSearchSpec()
                        vmx_spec.matchPattern = ["*.vmx"]
                        
                        vmx_task = browser.SearchDatastoreSubFolders_Task(ds_path, vmx_spec)
                        self.vsphere_client.wait_for_task(vmx_task)
                        
                        # Liste der Verzeichnisse mit VMX-Dateien erstellen
                        vmx_folders = set()
                        for folder_result in vmx_task.info.result:
                            if folder_result.file:
                                vmx_folders.add(folder_result.folderPath)
                        
                        # VMDKs ohne zugehörige VMX im selben Verzeichnis suchen
                        for folder_result in vmdk_task.info.result:
                            folder_path = folder_result.folderPath
                            
                            # Wenn keine VMX im selben Verzeichnis, könnte es verwaist sein
                            if folder_path not in vmx_folders and folder_result.file:
                                for file_info in folder_result.file:
                                    if not isinstance(file_info, vim.host.DatastoreBrowser.FileInfo):
                                        continue
                                        
                                    # Nur Basis-VMDKs, keine Delta-Disks oder Metadaten
                                    if file_info.path.endswith('.vmdk') and \
                                       not any(suffix in file_info.path for suffix in ['-delta.vmdk', '-flat.vmdk', '-ctk.vmdk']):
                                        orphaned_info = {
                                            'path': folder_path + file_info.path,
                                            'size_mb': file_info.fileSize / (1024 * 1024),
                                            'modify_time': file_info.modification
                                        }
                                        orphaned_vmdks.append(orphaned_info)
                    
                    except Exception as e:
                        logger.error(f"Fehler in der Fallback-Methode für Datastore {ds.name}: {str(e)}")
                        logger.error(traceback.format_exc())
                        continue
            
            return orphaned_vmdks
            
        except Exception as e:
            logger.error(f"Fehler in der Fallback-Methode für verwaiste VMDKs: {str(e)}")
            logger.error(traceback.format_exc())
            
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
        # Basisname ohne Erweiterung holen
        base_name = vmdk_name.rsplit('.', 1)[0]
        
        # Nach einer VMX-Datei mit demselben Basisnamen suchen
        vmx_name = base_name + '.vmx'
        
        try:
            # Datastore aus dem Verzeichnispfad holen
            ds_name = folder_path.split('[')[1].split(']')[0]
            datastore = None
            
            for ds in self.vsphere_client.content.rootFolder.childEntity:
                if not hasattr(ds, 'datastore'):
                    continue
                    
                for d in ds.datastore:
                    if d.name == ds_name:
                        datastore = d
                        break
                
                if datastore:
                    break
            
            if not datastore:
                logger.error(f"Datastore {ds_name} nicht gefunden")
                return True
            
            # Prüfen, ob die VMX-Datei existiert
            browser = datastore.browser
            search_spec = vim.HostDatastoreBrowserSearchSpec()
            search_spec.matchPattern = [vmx_name]
            
            task = browser.SearchDatastore_Task(folder_path, search_spec)
            self.vsphere_client.wait_for_task(task)
            
            # Wenn die VMX-Datei existiert, ist die VMDK nicht verwaist
            if task.info.result and task.info.result.file:
                return False
            
            # Zusätzliche Prüfung: Nach .nvram, .vmsd oder anderen VM-bezogenen Dateien suchen
            vm_related_files = [base_name + ext for ext in ['.nvram', '.vmsd', '.vmxf']]
            
            search_spec.matchPattern = vm_related_files
            task = browser.SearchDatastore_Task(folder_path, search_spec)
            self.vsphere_client.wait_for_task(task)
            
            # Wenn irgendwelche VM-bezogenen Dateien existieren, ist die VMDK nicht verwaist
            if task.info.result and task.info.result.file:
                return False
            
            # Wenn wir hier angekommen sind, wurden keine VM-Dateien gefunden, die VMDK könnte verwaist sein
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Prüfen von VMDK {vmdk_name}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Nehmen wir an, sie ist nicht verwaist, wenn wir einen Fehler hatten
            return False

def main():
    """Haupteinstiegspunkt für das CLI-Tool"""
    print("VSPHERE REPORTER - DEBUG TOOL FÜR SNAPSHOTS UND ORPHANED VMDKS")
    print("============================================================")
    print("Dieses Tool identifiziert Snapshots und verwaiste VMDK-Dateien in einer vSphere-Umgebung.")
    print("Es wurde für Administratoren entwickelt, die Probleme mit der Erkennung dieser Elemente haben.")
    print("\nDa der Debug-Modus aktiviert ist, werden ausführliche Fehlerausgaben angezeigt.")
    print()
    
    # Befehlszeilenargumente parsen
    parser = argparse.ArgumentParser(description='VMware vSphere Reporter - Debug-Tool für Snapshots und Orphaned VMDKs')
    parser.add_argument('-s', '--server', required=True, help='vCenter-Server (Hostname oder IP)')
    parser.add_argument('-u', '--user', required=True, help='vCenter-Benutzername')
    parser.add_argument('-p', '--password', help='vCenter-Passwort (wenn nicht angegeben, wird nachgefragt)')
    parser.add_argument('-k', '--insecure', action='store_true', help='SSL-Zertifikatsüberprüfung ignorieren')
    parser.add_argument('-o', '--output', default='debug_report', help='Ausgabedateiname (ohne Erweiterung)')
    args = parser.parse_args()
    
    # Passwort abfragen, wenn nicht angegeben
    password = args.password
    if not password:
        password = getpass.getpass("vCenter-Passwort: ")
    
    try:
        # Mit vCenter verbinden
        print(f"\nVerbindung mit {args.server} wird hergestellt...")
        client = VSphereClient(args.server, args.user, password, args.insecure)
        
        if not client.connect():
            print("Fehler: Verbindung zu vCenter fehlgeschlagen. Siehe Log für Details.")
            sys.exit(1)
            
        print("Verbindung erfolgreich hergestellt.")
        
        # Datensammler erstellen
        collector = DataCollector(client)
        
        # Snapshots sammeln
        print("\nSammle Informationen über Snapshots...")
        snapshots = collector.collect_snapshot_info()
        print(f"{len(snapshots)} Snapshots gefunden.")
        
        # Verwaiste VMDKs sammeln
        print("\nSammle Informationen über verwaiste VMDK-Dateien...")
        orphaned_vmdks = collector.collect_orphaned_vmdks()
        print(f"{len(orphaned_vmdks)} verwaiste VMDK-Dateien gefunden.")
        
        # Einfache Textausgabe in Konsole
        print("\n=== SNAPSHOTS ===")
        if snapshots:
            for i, snap in enumerate(snapshots, 1):
                print(f"{i}. VM: {snap['vm_name']} - Snapshot: {snap['name']} - Alter: {snap['age_days']} Tage")
        else:
            print("Keine Snapshots gefunden!")
            
        print("\n=== VERWAISTE VMDK-DATEIEN ===")
        if orphaned_vmdks:
            for i, vmdk in enumerate(orphaned_vmdks, 1):
                print(f"{i}. Pfad: {vmdk['path']} - Größe: {vmdk['size_mb']:.2f} MB")
        else:
            print("Keine verwaisten VMDK-Dateien gefunden!")
            
        # Ausführlicheren Bericht in Datei schreiben
        output_file = f"{args.output}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"VMware vSphere Reporter - Debug Report\n")
            f.write(f"======================================\n\n")
            f.write(f"Server: {args.server}\n")
            f.write(f"Benutzer: {args.user}\n")
            f.write(f"Datum: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("=== SNAPSHOTS ===\n")
            if snapshots:
                for i, snap in enumerate(snapshots, 1):
                    f.write(f"{i}. VM: {snap['vm_name']}\n")
                    f.write(f"   Name: {snap['name']}\n")
                    f.write(f"   Beschreibung: {snap['description']}\n")
                    f.write(f"   Erstellt am: {snap['create_time']}\n")
                    f.write(f"   Alter: {snap['age_days']} Tage\n")
                    f.write(f"   ID: {snap['id']}\n")
                    f.write(f"   Status: {snap['state']}\n\n")
            else:
                f.write("Keine Snapshots gefunden!\n\n")
                
            f.write("=== VERWAISTE VMDK-DATEIEN ===\n")
            if orphaned_vmdks:
                for i, vmdk in enumerate(orphaned_vmdks, 1):
                    f.write(f"{i}. Pfad: {vmdk['path']}\n")
                    f.write(f"   Größe: {vmdk['size_mb']:.2f} MB\n")
                    f.write(f"   Letzte Änderung: {vmdk['modify_time']}\n\n")
            else:
                f.write("Keine verwaisten VMDK-Dateien gefunden!\n\n")
                
        print(f"\nDebug-Report wurde in {output_file} gespeichert.")
        print(f"Ausführlichere Protokollausgabe finden Sie in vsphere_debug.log")
        
    except KeyboardInterrupt:
        print("\nOperation durch Benutzer abgebrochen.")
    except Exception as e:
        print(f"\nFehler: {str(e)}")
        logger.error(f"Unbehandelter Fehler: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # Verbindung trennen
        if 'client' in locals():
            client.disconnect()
            
    print("\nProgramm beendet.")

if __name__ == "__main__":
    main()