"""
VMware vSphere Reporter - vSphere Client Module
Vereinfachte Version für maximale Kompatibilität
Version v18 - Rohdatenanzeige und Fehlerdiagnose
"""

import ssl
import time
import logging
import socket
import traceback
from datetime import datetime
import urllib.parse

try:
    from pyVim import connect
    from pyVmomi import vim, vmodl
except ImportError:
    print("PyVmomi nicht gefunden. Bitte installieren Sie: pip install pyvmomi>=7.0.0")

class VSphereClient:
    """vSphere-Client für den Zugriff auf vCenter-APIs"""
    
    def __init__(self):
        """Initialisiere den Client"""
        self.service_instance = None
        self.content = None
        self.connected = False
        self.debug_mode = True  # Immer Debug-Modus aktivieren
        self.logger = logging.getLogger('vsphere_reporter')
        self.connection_info = {}
        self.error_log = []
        self.raw_data = {}
        self.demo_mode = False

    def log_error(self, error_msg, exception=None):
        """
        Protokolliere einen Fehler mit Stacktrace
        
        Args:
            error_msg: Fehlermeldung
            exception: Die aufgetretene Exception (optional)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_entry = f"[{timestamp}] {error_msg}"
        
        if exception:
            stack_trace = traceback.format_exc()
            error_entry += f"\nException: {str(exception)}\nStacktrace: {stack_trace}"
        
        self.error_log.append(error_entry)
        self.logger.error(error_msg)
        
        if exception:
            self.logger.error(f"Exception: {str(exception)}")
            self.logger.debug(f"Stacktrace: {traceback.format_exc()}")

    def connect_to_server(self, host, username, password, port=443, disable_ssl_verification=True):
        """
        Verbindung zum vCenter-Server herstellen
        
        Args:
            host: Hostname oder IP-Adresse des vCenter-Servers
            username: Benutzername für die Anmeldung
            password: Passwort für die Anmeldung
            port: Port für die Verbindung (Standard: 443)
            disable_ssl_verification: SSL-Verifizierung deaktivieren (Standard: True)
            
        Returns:
            bool: True bei erfolgreicher Verbindung, False bei Fehler
        """
        if not host or not username or not password:
            self.log_error("Verbindungsdaten sind unvollständig")
            return False
        
        self.connection_info = {
            'host': host,
            'username': username,
            'port': port,
            'disable_ssl_verification': disable_ssl_verification
        }
        
        self.logger.info(f"Verbinde mit vCenter {host}")
        
        try:
            if disable_ssl_verification:
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                context.verify_mode = ssl.CERT_NONE
            else:
                context = None
                
            socket.setdefaulttimeout(180)  # Erhöhtes Timeout für stabile Verbindung

            self.service_instance = connect.SmartConnect(
                host=host,
                user=username,
                pwd=password,
                port=port,
                sslContext=context,
                connectionPoolTimeout=180
            )
            
            if not self.service_instance:
                self.log_error(f"Verbindung zu {host} fehlgeschlagen - Keine ServiceInstance zurückgegeben")
                return False
                
            self.content = self.service_instance.RetrieveContent()
            if not self.content:
                self.log_error(f"Verbindung zu {host} hergestellt, aber Content konnte nicht abgerufen werden")
                return False
                
            about = self.content.about
            self.logger.info(f"Erfolgreich verbunden mit {host} - {about.fullName}")
            self.connected = True
            return True
            
        except vim.fault.InvalidLogin as e:
            self.log_error(f"Ungültige Anmeldedaten für {host}", e)
            return False
        except (socket.gaierror, socket.error) as e:
            self.log_error(f"Netzwerkfehler bei Verbindung zu {host}", e)
            return False
        except Exception as e:
            self.log_error(f"Unerwarteter Fehler bei Verbindung zu {host}", e)
            return False

    def disconnect(self):
        """Trennen vom vCenter-Server"""
        if self.service_instance:
            connect.Disconnect(self.service_instance)
            self.logger.info("Verbindung zum vCenter getrennt")
            self.connected = False
            self.service_instance = None
            self.content = None

    def wait_for_task(self, task):
        """
        Warten auf Abschluss einer vCenter-Task
        
        Args:
            task: vCenter-Task
            
        Returns:
            task: Abgeschlossene Task
        """
        if not task:
            self.log_error("Keine Task zum Warten angegeben")
            return None
            
        try:
            state = task.info.state
            while state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
                time.sleep(1)
                state = task.info.state
                
            if state == vim.TaskInfo.State.error:
                error_msg = f"Task fehlgeschlagen: {task.info.error.msg}"
                self.log_error(error_msg)
                raise Exception(error_msg)
                
            return task
            
        except Exception as e:
            self.log_error(f"Fehler beim Warten auf Task", e)
            return None

    def collect_all_vmdk_files(self):
        """
        Sammle alle VMDK-Dateien aus den Datastores
        Sonderimplementierung mit Rohdatenanzeige für Fehlerdiagnose
        
        Returns:
            dict: Gesammelte Rohdaten
        """
        if not self.connected and not self.demo_mode:
            self.log_error("Keine Verbindung zum vCenter")
            return None
            
        # Lösche vorherige Rohdaten
        self.raw_data = {
            'datastore_browser_data': [],
            'vm_disk_data': [],
            'all_vmdk_paths': [],
            'registered_vmdk_paths': [],
            'orphaned_vmdks': []
        }
            
        try:
            # 1. Sammle alle registrierten VMDKs von VMs
            if self.content:
                container = self.content.viewManager.CreateContainerView(
                    container=self.content.rootFolder,
                    type=[vim.VirtualMachine],
                    recursive=True
                )
                
                vms = container.view
                self.logger.info(f"Gefundene VMs: {len(vms)}")
                self.raw_data['vm_count'] = len(vms)
                
                for vm in vms:
                    try:
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                disk_path = device.backing.fileName
                                
                                disk_info = {
                                    'vm_name': vm.name,
                                    'disk_path': disk_path,
                                    'disk_size_gb': device.capacityInKB / 1024 / 1024,
                                    'device_key': device.key
                                }
                                
                                self.raw_data['vm_disk_data'].append(disk_info)
                                self.raw_data['registered_vmdk_paths'].append(disk_path)
                    except Exception as e:
                        self.log_error(f"Fehler beim Sammeln von Disks für VM {vm.name}", e)
            
            # 2. Durchsuche alle Datastores nach VMDKs
            datastores = self.get_all_datastores()
            if not datastores:
                self.log_error("Keine Datastores gefunden")
                return self.raw_data
                
            self.raw_data['datastore_count'] = len(datastores)
            
            for ds in datastores:
                try:
                    ds_browser = ds.browser
                    if not ds_browser:
                        self.log_error(f"Kein Browser für Datastore {ds.name} verfügbar")
                        continue
                        
                    # Erstelle eine Suche im Datastore-Root
                    search_spec = vim.host.DatastoreBrowser.SearchSpec()
                    search_spec.matchPattern = ["*.vmdk"]
                    search_spec.details = vim.host.DatastoreBrowser.FileInfo.Details()
                    search_spec.searchCaseInsensitive = True
                    
                    # Starte die Suche
                    task = ds_browser.SearchDatastoreSubFolders_Task(
                        datastorePath=f"[{ds.name}]", 
                        searchSpec=search_spec
                    )
                    
                    # Warte auf die Ergebnisse
                    task_result = self.wait_for_task(task)
                    if not task_result:
                        self.log_error(f"Die Suche im Datastore {ds.name} wurde abgebrochen")
                        continue
                        
                    # Verarbeite die Ergebnisse
                    search_results = task.info.result
                    for result in search_results:
                        folder_path = result.folderPath
                        self.raw_data['datastore_browser_data'].append({
                            'datastore': ds.name,
                            'folder': folder_path,
                            'file_count': len(result.file) if hasattr(result, 'file') else 0
                        })
                        
                        if hasattr(result, 'file') and result.file:
                            for file_info in result.file:
                                if file_info.path.endswith('.vmdk') and not file_info.path.endswith('-flat.vmdk'):
                                    # Erstelle den vollständigen Pfad für die VMDK
                                    vmdk_path = f"{folder_path}{file_info.path}"
                                    
                                    self.raw_data['all_vmdk_paths'].append({
                                        'path': vmdk_path,
                                        'size_kb': file_info.fileSize if hasattr(file_info, 'fileSize') else 0,
                                        'modification_time': str(file_info.modification) if hasattr(file_info, 'modification') else 'Unbekannt'
                                    })
                                    
                except Exception as e:
                    self.log_error(f"Fehler beim Durchsuchen des Datastores {ds.name}", e)
            
            # 3. Identifiziere verwaiste VMDKs
            registered_paths = set(self.raw_data['registered_vmdk_paths'])
            
            for vmdk in self.raw_data['all_vmdk_paths']:
                if vmdk['path'] not in registered_paths and not self._is_template_or_snapshot_vmdk(vmdk['path']):
                    self.raw_data['orphaned_vmdks'].append(vmdk)
            
            return self.raw_data
            
        except Exception as e:
            self.log_error("Fehler beim Sammeln der VMDK-Dateien", e)
            return self.raw_data
            
    def _is_template_or_snapshot_vmdk(self, path):
        """
        Überprüft, ob eine VMDK zu einem Template oder Snapshot gehört
        
        Args:
            path: Pfad zur VMDK-Datei
            
        Returns:
            bool: True, wenn die VMDK zu einem Template oder Snapshot gehört
        """
        path_lower = path.lower()
        snapshot_indicators = ['-snapshot', '-000', '_snapshot', '_delta_']
        
        # Überprüfe auf Snapshot-Indikatoren
        return any(indicator in path_lower for indicator in snapshot_indicators)

    def get_all_datastores(self):
        """
        Alle Datastores abrufen
        
        Returns:
            list: Liste aller Datastores
        """
        if not self.connected and not self.demo_mode:
            self.log_error("Keine Verbindung zum vCenter")
            return []
            
        try:
            if not self.content:
                self.log_error("Kein Content verfügbar")
                return []
                
            container = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.Datastore],
                recursive=True
            )
            
            datastores = container.view
            container.Destroy()
            
            self.logger.info(f"Gefundene Datastores: {len(datastores)}")
            return datastores
            
        except Exception as e:
            self.log_error("Fehler beim Abrufen der Datastores", e)
            return []
            
    def set_demo_mode(self, enabled=True):
        """
        Demo-Modus aktivieren/deaktivieren
        
        Args:
            enabled: True zum Aktivieren, False zum Deaktivieren
        """
        self.demo_mode = enabled
        self.logger.info(f"Demo-Modus {'aktiviert' if enabled else 'deaktiviert'}")
        
    def get_error_log(self):
        """
        Fehlerlog abrufen
        
        Returns:
            list: Liste aller Fehler
        """
        return self.error_log