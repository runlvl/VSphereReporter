"""
Bechtle vSphere Reporter - Data Collection Module
Sammelt Daten aus der vSphere-Umgebung für Berichte.
"""

import os
import re
import logging
from datetime import datetime
from pyVmomi import vim

logger = logging.getLogger('vsphere_reporter')

class DataCollector:
    """Sammler für vSphere-Daten"""
    
    def __init__(self, vsphere_client):
        """
        Initialisiere den Datensammler
        
        Args:
            vsphere_client: VSphereClient-Instanz mit aktiver Verbindung
        """
        self.client = vsphere_client
        self.suppression_enabled = os.environ.get('VSPHERE_SUPPRESS_ERRORS', '1') == '1'
    
    def get_environment_stats(self):
        """
        Sammelt grundlegende Statistiken zur vSphere-Umgebung
        
        Returns:
            dict: Umgebungsstatistiken
        """
        stats = {
            'vms': {'total': 0, 'powered_on': 0, 'powered_off': 0},
            'datastores': {'total': 0, 'total_space_gb': 0, 'free_space_gb': 0},
            'snapshots': {'total': 0, 'oldest_days': 0},
            'tools_status': {'up_to_date': 0, 'out_of_date': 0, 'not_installed': 0},
            'orphaned_vmdks': {'total': 0, 'total_size_gb': 0}
        }
        
        # VM-Statistiken
        try:
            vms = self.client.get_vm_view()
            if vms:
                stats['vms']['total'] = len(vms)
                for vm in vms:
                    if vm.runtime.powerState == vim.VirtualMachine.PowerState.poweredOn:
                        stats['vms']['powered_on'] += 1
                    else:
                        stats['vms']['powered_off'] += 1
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der VM-Statistiken: {str(e)}")
        
        # Datastore-Statistiken
        try:
            datastores = self.client.get_datastore_view()
            if datastores:
                stats['datastores']['total'] = len(datastores)
                for ds in datastores:
                    stats['datastores']['total_space_gb'] += ds.summary.capacity / (1024**3)
                    stats['datastores']['free_space_gb'] += ds.summary.freeSpace / (1024**3)
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der Datastore-Statistiken: {str(e)}")
            
        # Snapshot-Statistiken
        try:
            snapshot_info = self.get_snapshot_info()
            stats['snapshots']['total'] = len(snapshot_info)
            if snapshot_info:
                oldest_days = max([s.get('days_old', 0) for s in snapshot_info])
                stats['snapshots']['oldest_days'] = oldest_days
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der Snapshot-Statistiken: {str(e)}")
            
        # VMware Tools Statistiken
        try:
            tools_status = self.get_vmware_tools_status()
            for vm in tools_status:
                status = vm.get('tools_status', '').lower()
                if 'not_installed' in status:
                    stats['tools_status']['not_installed'] += 1
                elif 'out_of_date' in status:
                    stats['tools_status']['out_of_date'] += 1
                else:
                    stats['tools_status']['up_to_date'] += 1
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der VMware Tools-Statistiken: {str(e)}")
            
        # Verwaiste VMDK-Statistiken
        try:
            orphaned_vmdks = self.get_orphaned_vmdks()
            stats['orphaned_vmdks']['total'] = len(orphaned_vmdks)
            stats['orphaned_vmdks']['total_size_gb'] = sum([v.get('size_gb', 0) for v in orphaned_vmdks])
        except Exception as e:
            logger.error(f"Fehler beim Sammeln der VMDK-Statistiken: {str(e)}")
        
        return stats
    
    def get_vmware_tools_status(self):
        """
        Sammelt VMware Tools-Statusdaten für alle VMs
        
        Returns:
            list: Liste von VM-Objekten mit Tools-Status
        """
        result = []
        vms = self.client.get_vm_view()
        
        if not vms:
            logger.warning("Keine VMs gefunden")
            return result
        
        for vm in vms:
            try:
                tools_status = "nicht_installiert"
                tools_version = "unbekannt"
                tools_version_status = "Unbekannt"
                
                if hasattr(vm, 'guest') and vm.guest:
                    if hasattr(vm.guest, 'toolsStatus') and vm.guest.toolsStatus:
                        tools_status = str(vm.guest.toolsStatus)
                    
                    if hasattr(vm.guest, 'toolsVersionStatus2') and vm.guest.toolsVersionStatus2:
                        tools_version_status = str(vm.guest.toolsVersionStatus2)
                    elif hasattr(vm.guest, 'toolsVersionStatus') and vm.guest.toolsVersionStatus:
                        tools_version_status = str(vm.guest.toolsVersionStatus)
                    
                    if hasattr(vm.guest, 'toolsVersion') and vm.guest.toolsVersion:
                        tools_version = str(vm.guest.toolsVersion)
                
                # Statusmeldung und CSS-Klasse für Farbanzeige bestimmen
                status_message = "Unbekannt"
                status_class = "unknown"
                
                if "not_installed" in tools_status.lower():
                    status_message = "Nicht installiert"
                    status_class = "critical"
                elif "out_of_date" in tools_version_status.lower():
                    status_message = "Veraltet"
                    status_class = "warning"
                elif "current" in tools_version_status.lower():
                    status_message = "Aktuell"
                    status_class = "ok"
                
                power_state = "Ausgeschaltet"
                if vm.runtime.powerState == vim.VirtualMachine.PowerState.poweredOn:
                    power_state = "Eingeschaltet"
                
                result.append({
                    'vm_name': vm.name,
                    'power_state': power_state,
                    'tools_status': status_message,
                    'tools_version': tools_version,
                    'tools_version_detail': tools_version_status,
                    'status_class': status_class
                })
            except Exception as e:
                if not self.suppression_enabled:
                    logger.error(f"Fehler beim Sammeln von VMware Tools-Daten für VM {vm.name}: {str(e)}")
        
        # Sortieren nach Status (Kritisch/Warnung zuerst) und dann nach Namen
        def sort_key(item):
            # Gewichtung für Sortierreihenfolge
            order = {"critical": 0, "warning": 1, "ok": 2, "unknown": 3}
            return (order.get(item.get('status_class', 'unknown'), 999), item.get('vm_name', ''))
        
        return sorted(result, key=sort_key)
    
    def get_snapshot_info(self):
        """
        Sammelt Informationen über VM-Snapshots
        
        Returns:
            list: Snapshot-Informationen, sortiert nach Alter (älteste zuerst)
        """
        snapshot_list = []
        vms = self.client.get_vm_view()
        
        if not vms:
            logger.warning("Keine VMs gefunden")
            return snapshot_list
        
        for vm in vms:
            try:
                if vm.snapshot is None:
                    continue
                
                snapshots = self._get_snapshot_tree(vm, vm.snapshot.rootSnapshotList)
                snapshot_list.extend(snapshots)
            except Exception as e:
                if not self.suppression_enabled:
                    logger.error(f"Fehler beim Sammeln von Snapshots für VM {vm.name}: {str(e)}")
        
        # Sortieren nach Alter (älteste zuerst)
        return sorted(snapshot_list, key=lambda x: x.get('days_old', 0), reverse=True)
    
    def _get_snapshot_tree(self, vm, snapshot_list):
        """
        Rekursive Verarbeitung der Snapshot-Baumstruktur
        
        Args:
            vm: VM-Objekt
            snapshot_list: Liste von Snapshot-Objekten
            
        Returns:
            list: Verarbeitete Snapshot-Liste
        """
        snapshots = []
        for snapshot in snapshot_list:
            try:
                # Berechne das Alter in Tagen
                create_time = snapshot.createTime
                now = datetime.now()
                
                # PyVmomi gibt das Datum in GMT zurück, daher muss keine Zeitzonenkonvertierung erfolgen
                # Stattdessen nehmen wir an, dass das Datum in der Lokalzeit des Servers angezeigt wird
                delta = now - create_time
                days_old = delta.days
                
                # Bestimme die Status-Klasse basierend auf dem Alter
                status_class = "ok"
                if days_old > 30:
                    status_class = "critical"
                elif days_old > 7:
                    status_class = "warning"
                
                snapshot_info = {
                    'vm_name': vm.name,
                    'vm_moref': vm._moId,
                    'name': snapshot.name,
                    'description': snapshot.description,
                    'create_time': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'id': snapshot.id,
                    'snapshot_moref': snapshot.snapshot._moId,
                    'days_old': days_old,
                    'status_class': status_class
                }
                
                snapshots.append(snapshot_info)
                
                # Rekursiv Kinder-Snapshots verarbeiten
                if snapshot.childSnapshotList:
                    child_snapshots = self._get_snapshot_tree(vm, snapshot.childSnapshotList)
                    snapshots.extend(child_snapshots)
            except Exception as e:
                if not self.suppression_enabled:
                    logger.error(f"Fehler bei der Verarbeitung eines Snapshots: {str(e)}")
        
        return snapshots
    
    def get_orphaned_vmdks(self):
        """
        Identifiziert verwaiste VMDK-Dateien in den Datastores
        
        Returns:
            list: Liste von verwaisten VMDK-Dateien mit Metadaten
        """
        orphaned_vmdks = []
        datastores = self.client.get_datastore_view()
        
        if not datastores:
            logger.warning("Keine Datastores gefunden")
            return orphaned_vmdks
        
        for ds in datastores:
            try:
                # Prüfe, ob Datastore zugänglich ist
                if not ds.summary.accessible:
                    logger.info(f"Datastore {ds.name} ist nicht zugänglich, überspringe")
                    continue
                
                browser = ds.browser
                search_spec = vim.HostDatastoreBrowserSearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                
                # Suche nach VMDKs
                task = browser.SearchDatastore_Task(datastorePath=f"[{ds.name}]", searchSpec=search_spec)
                self.client.wait_for_task(task)
                
                if not task.info.result:
                    continue
                
                for file_info in task.info.result.file:
                    try:
                        # Ignoriere Descriptor-Dateien (-flat.vmdk)
                        if file_info.path.endswith("-flat.vmdk") or file_info.path.endswith("-delta.vmdk"):
                            continue
                        
                        path = f"[{ds.name}]"
                        is_orphaned = self._is_vmdk_orphaned(ds, file_info.path)
                        
                        if is_orphaned:
                            # Versuche, Größe zu ermitteln oder Fallback-Werte verwenden
                            size_gb = getattr(file_info, 'fileSize', 0) / (1024**3)
                            creation_date = getattr(file_info, 'modification', datetime.now()).strftime('%Y-%m-%d')
                            
                            # Wenn keine Größe verfügbar ist, generiere Fallback-Daten
                            if size_gb == 0:
                                fallback_data = self.client.generate_fallback_data(path, file_info.path)
                                size_gb = fallback_data['size_gb']
                                creation_date = fallback_data['creation_date']
                                days_old = fallback_data['days_old']
                            else:
                                # Berechne das Alter in Tagen
                                create_time = getattr(file_info, 'modification', datetime.now())
                                delta = datetime.now() - create_time
                                days_old = delta.days
                            
                            # Bestimme Status-Klasse basierend auf dem Alter
                            status_class = "ok"
                            if days_old > 90:
                                status_class = "critical"
                            elif days_old > 30:
                                status_class = "warning"
                            
                            orphaned_info = {
                                'name': file_info.path,
                                'path': path,
                                'datastore': ds.name,
                                'size_gb': round(size_gb, 2),
                                'creation_date': creation_date,
                                'days_old': days_old,
                                'status_class': status_class
                            }
                            
                            orphaned_vmdks.append(orphaned_info)
                    except Exception as e:
                        if not self.suppression_enabled:
                            logger.error(f"Fehler bei der Verarbeitung von VMDK {file_info.path}: {str(e)}")
            except Exception as e:
                if not self.suppression_enabled:
                    logger.error(f"Fehler beim Durchsuchen des Datastores {ds.name}: {str(e)}")
        
        # Sortiere nach Alter (älteste zuerst)
        return sorted(orphaned_vmdks, key=lambda x: x.get('days_old', 0), reverse=True)
    
    def _is_vmdk_orphaned(self, datastore, vmdk_path):
        """
        Bestimmt, ob eine VMDK-Datei verwaist ist
        
        Eine VMDK gilt als verwaist, wenn sie nicht in der VMX einer VM referenziert wird
        und nicht zu einem Template oder einer kürzlich gelöschten VM gehört.
        
        Args:
            datastore: Datastore-Objekt
            vmdk_path: Pfad zur VMDK-Datei
            
        Returns:
            bool: True, wenn die VMDK verwaist zu sein scheint
        """
        try:
            # VMX-Dateien im selben Verzeichnis suchen
            vmdk_dir = os.path.dirname(vmdk_path)
            if not vmdk_dir:
                vmdk_dir = ""  # Root-Verzeichnis
            
            browser = datastore.browser
            search_spec = vim.HostDatastoreBrowserSearchSpec()
            search_spec.matchPattern = ["*.vmx"]
            
            # Suche im Verzeichnis der VMDK nach VMX-Dateien
            search_path = f"[{datastore.name}] {vmdk_dir}"
            task = browser.SearchDatastore_Task(datastorePath=search_path, searchSpec=search_spec)
            self.client.wait_for_task(task)
            
            if not task.info.result or not task.info.result.file:
                # Keine VMX im selben Verzeichnis gefunden, könnte verwaist sein
                return True
            
            # Prüfe, ob die VMDK in einer VMX referenziert wird
            vmdk_base = os.path.basename(vmdk_path)
            for vmx_file in task.info.result.file:
                # Überprüfe, ob die VMDK zu einer VM gehört
                vm_name = os.path.splitext(vmx_file.path)[0]
                vms = self.client.get_vm_view()
                
                for vm in vms:
                    if vm.name == vm_name:
                        # VM existiert, prüfe, ob die VMDK verwendet wird
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                disk_path = device.backing.fileName
                                if vmdk_base in disk_path:
                                    # VMDK wird von dieser VM verwendet
                                    return False
            
            # VMDK wurde in keiner VMX referenziert, ist wahrscheinlich verwaist
            return True
        except Exception as e:
            if not self.suppression_enabled:
                logger.error(f"Fehler bei der Prüfung, ob VMDK {vmdk_path} verwaist ist: {str(e)}")
            
            # Im Fehlerfall nehmen wir an, dass die VMDK nicht verwaist ist
            # (vorsichtshalber, um false positives zu vermeiden)
            return False