"""
VMware vSphere Reporter - vSphere Client Module
Optimierte Version basierend auf dem erfolgreichen Ansatz aus v18
Version v19 - Verbesserte Datenerfassung mit Fehlertoleranz
"""

import ssl
import time
import logging
import socket
import traceback
from datetime import datetime

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
        
        # Statusanzeige für erfolgreiche Datensammlungen
        self.collection_status = {
            'vmware_tools': False,
            'snapshots': False,
            'orphaned_vmdks': False
        }
        
    def set_demo_mode(self, mode):
        """Setzt den Demo-Modus
        
        Args:
            mode (bool): True für Demo-Modus, False für Echtmodus
        """
        self.demo_mode = mode
        self.logger.info(f"Demo-Modus {'aktiviert' if mode else 'deaktiviert'}")

    def log_error(self, error_msg, exception=None):
        """Protokolliere einen Fehler mit Stacktrace"""
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
        """Verbindung zum vCenter-Server herstellen"""
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
        """Warten auf Abschluss einer vCenter-Task"""
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
            
    def collect_vmware_tools_status(self):
        """Sammle Informationen über VMware-Tools-Status"""
        if not self.connected and not self.demo_mode:
            self.log_error("Keine Verbindung zum vCenter")
            return None
            
        try:
            self.logger.info("Sammle VMware-Tools-Statusinformationen...")
            
            if self.demo_mode:
                from demo_data import get_demo_data
                self.collection_status['vmware_tools'] = True
                return {"demo": True, "data": get_demo_data().get('vmware_tools_data', [])}
                
            # Container für VM-Objekte erstellen
            container = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.VirtualMachine],
                recursive=True
            )
            
            vms = container.view
            container.Destroy()
            
            tools_status_data = []
            
            for vm in vms:
                try:
                    # Nur eingeschaltete VMs berücksichtigen
                    if vm.runtime.powerState != vim.VirtualMachine.PowerState.poweredOn:
                        continue
                        
                    if not vm.guest:
                        continue
                        
                    # Informationen sammeln
                    tools_info = {
                        'name': vm.name,
                        'tools_version': vm.guest.toolsVersion if vm.guest.toolsVersion else 'Nicht installiert',
                        'tools_status': vm.guest.toolsVersionStatus if vm.guest.toolsVersionStatus else 'Unbekannt',
                        'tools_running_status': vm.guest.toolsRunningStatus if vm.guest.toolsRunningStatus else 'Unbekannt',
                        'last_update': '',
                        'os': vm.guest.guestFullName if vm.guest.guestFullName else 'Unbekannt'
                    }
                    
                    # Farbkodierung basierend auf Status
                    if tools_info['tools_status'] == 'guestToolsCurrent':
                        tools_info['status_class'] = 'success'
                        tools_info['status_text'] = 'Aktuell'
                    elif tools_info['tools_status'] == 'guestToolsNeedUpgrade':
                        tools_info['status_class'] = 'warning'
                        tools_info['status_text'] = 'Update verfügbar'
                    elif tools_info['tools_status'] == 'guestToolsNotInstalled':
                        tools_info['status_class'] = 'danger'
                        tools_info['status_text'] = 'Nicht installiert'
                    else:
                        tools_info['status_class'] = 'secondary'
                        tools_info['status_text'] = 'Unbekannt'
                    
                    # Laufend/Nicht laufend Status
                    if tools_info['tools_running_status'] == 'guestToolsRunning':
                        tools_info['running_class'] = 'success'
                        tools_info['running_text'] = 'Laufend'
                    elif tools_info['tools_running_status'] == 'guestToolsNotRunning':
                        tools_info['running_class'] = 'danger'
                        tools_info['running_text'] = 'Nicht laufend'
                    else:
                        tools_info['running_class'] = 'secondary'
                        tools_info['running_text'] = 'Unbekannt'
                    
                    tools_status_data.append(tools_info)
                except Exception as e:
                    self.log_error(f"Fehler beim Sammeln von VMware-Tools-Daten für VM {vm.name}", e)
            
            # Nach VMware-Tools-Version sortieren (älteste zuerst)
            tools_status_data.sort(
                key=lambda x: (x['tools_status'] != 'guestToolsNeedUpgrade', x['tools_status'] != 'guestToolsNotInstalled', x['tools_version'])
            )
            
            self.collection_status['vmware_tools'] = True
            return tools_status_data
            
        except Exception as e:
            self.log_error("Fehler beim Sammeln der VMware-Tools-Statusinformationen", e)
            return []
            
    def collect_snapshot_info(self):
        """Sammle Informationen über VM-Snapshots"""
        if not self.connected and not self.demo_mode:
            self.log_error("Keine Verbindung zum vCenter")
            return None
            
        try:
            self.logger.info("Sammle Snapshot-Informationen...")
            
            if self.demo_mode:
                from demo_data import get_demo_data
                self.collection_status['snapshots'] = True
                return {"demo": True, "data": get_demo_data().get('snapshots_data', [])}
                
            # Container für VM-Objekte erstellen
            container = self.content.viewManager.CreateContainerView(
                container=self.content.rootFolder,
                type=[vim.VirtualMachine],
                recursive=True
            )
            
            vms = container.view
            container.Destroy()
            
            snapshot_data = []
            now = datetime.now()
            
            for vm in vms:
                try:
                    if not vm.snapshot:
                        continue
                        
                    snapshot_list = vm.snapshot.rootSnapshotList
                    if not snapshot_list:
                        continue
                        
                    # Snapshots rekursiv verarbeiten
                    self._process_snapshot_tree(vm, snapshot_list, snapshot_data, now)
                except Exception as e:
                    self.log_error(f"Fehler beim Sammeln von Snapshot-Daten für VM {vm.name}", e)
            
            # Nach Alter sortieren (älteste zuerst)
            snapshot_data.sort(key=lambda x: x['create_time'] if x['create_time'] else datetime.now())
            
            # Farbkodierung für Alter hinzufügen
            for snapshot in snapshot_data:
                try:
                    days = snapshot['days_old']
                    if days <= 7:
                        snapshot['age_class'] = 'success'
                    elif days <= 30:
                        snapshot['age_class'] = 'warning'
                    else:
                        snapshot['age_class'] = 'danger'
                except:
                    snapshot['age_class'] = 'secondary'
            
            self.collection_status['snapshots'] = True
            return snapshot_data
            
        except Exception as e:
            self.log_error("Fehler beim Sammeln der Snapshot-Informationen", e)
            return []
            
    def _process_snapshot_tree(self, vm, snapshot_list, snapshot_data, now, parent_path=None):
        """Verarbeite Snapshots rekursiv"""
        for snapshot in snapshot_list:
            try:
                # Pfad aufbauen
                if parent_path:
                    path = f"{parent_path} > {snapshot.name}"
                else:
                    path = snapshot.name
                    
                # Altersinformationen berechnen
                create_time = snapshot.createTime
                if create_time:
                    td = now - create_time.replace(tzinfo=None)
                    days_old = td.days
                    hours_old = int(td.seconds / 3600)
                else:
                    days_old = None
                    hours_old = None
                    
                # Größeninformationen (können NULL sein)
                if hasattr(snapshot, 'sizeInGB') and snapshot.sizeInGB:
                    size_gb = snapshot.sizeInGB
                else:
                    size_gb = None
                
                # Snapshot-Daten sammeln
                snap_info = {
                    'vm_name': vm.name,
                    'name': snapshot.name,
                    'path': path,
                    'description': snapshot.description,
                    'create_time': create_time,
                    'days_old': days_old,
                    'hours_old': hours_old,
                    'size_gb': size_gb,
                    'id': snapshot.id,
                    # Formatierte Anzeigewerte
                    'create_time_str': create_time.strftime('%Y-%m-%d %H:%M:%S') if create_time else 'Unbekannt',
                    'age_str': f"{days_old} Tage, {hours_old} Stunden" if days_old is not None else 'Unbekannt',
                    'size_str': f"{size_gb:.2f} GB" if size_gb else 'Unbekannt'
                }
                
                snapshot_data.append(snap_info)
                
                # Rekursiv über Kinder-Snapshots gehen
                if hasattr(snapshot, 'childSnapshotList') and snapshot.childSnapshotList:
                    self._process_snapshot_tree(vm, snapshot.childSnapshotList, snapshot_data, now, path)
            except Exception as e:
                self.log_error(f"Fehler bei der Verarbeitung eines Snapshots für VM {vm.name}", e)
                continue

    def collect_all_vmdk_files(self):
        """
        Sammle alle VMDK-Dateien aus den Datastores
        Basierend auf dem erfolgreichen Ansatz aus v18, aber mit verbesserter Fehlerbehandlung
        """
        if not self.connected and not self.demo_mode:
            self.log_error("Keine Verbindung zum vCenter")
            return None
            
        try:
            self.logger.info("Sammle VMDK-Dateien und identifiziere verwaiste VMDKs...")
            
            if self.demo_mode:
                from demo_data import get_demo_data
                self.collection_status['orphaned_vmdks'] = True
                demo_data = get_demo_data()
                # Daten direkt in das raw_data-Attribut setzen
                self.raw_data = demo_data.get('raw_data', {})
                # Objekte für orphaned_vmdks direkt zurückgeben
                return {
                    "demo": True,
                    "orphaned_vmdks": demo_data.get('orphaned_vmdks', [])
                }
            
            # Initialisiere die Rohdatenstruktur
            self.raw_data = {
                'datastore_browser_data': [],
                'vm_disk_data': [],
                'all_vmdk_paths': [],
                'registered_vmdk_paths': [],
                'orphaned_vmdks': []
            }
            
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
                        if not hasattr(vm, 'config') or not vm.config or not hasattr(vm.config, 'hardware') or not vm.config.hardware:
                            continue
                            
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk):
                                try:
                                    disk_path = device.backing.fileName
                                    
                                    disk_info = {
                                        'vm_name': vm.name,
                                        'disk_path': disk_path,
                                        'disk_size_gb': device.capacityInKB / 1024 / 1024 if hasattr(device, 'capacityInKB') else None,
                                        'device_key': device.key
                                    }
                                    
                                    self.raw_data['vm_disk_data'].append(disk_info)
                                    self.raw_data['registered_vmdk_paths'].append(disk_path)
                                except AttributeError:
                                    # Manche Disks haben kein backing oder fileName, diese überspringen
                                    continue
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
                        
                        files_count = len(result.file) if hasattr(result, 'file') and result.file else 0
                        
                        self.raw_data['datastore_browser_data'].append({
                            'datastore': ds.name,
                            'folder': folder_path,
                            'file_count': files_count
                        })
                        
                        if hasattr(result, 'file') and result.file:
                            for file_info in result.file:
                                try:
                                    if not hasattr(file_info, 'path') or not file_info.path:
                                        continue
                                        
                                    file_path = file_info.path
                                    if not file_path.endswith('.vmdk') or file_path.endswith('-flat.vmdk'):
                                        continue
                                        
                                    # Erstelle den vollständigen Pfad für die VMDK
                                    vmdk_path = f"{folder_path}{file_path}"
                                    
                                    # Sammle alle verfügbaren Metadaten (einige können NULL sein)
                                    vmdk_data = {
                                        'path': vmdk_path,
                                        'size_kb': file_info.fileSize if hasattr(file_info, 'fileSize') else None,
                                        'modification_time': str(file_info.modification) if hasattr(file_info, 'modification') else None
                                    }
                                    
                                    self.raw_data['all_vmdk_paths'].append(vmdk_data)
                                except Exception as e:
                                    self.log_error(f"Fehler beim Verarbeiten der VMDK-Datei in {folder_path}", e)
                                    continue
                        
                except Exception as e:
                    self.log_error(f"Fehler beim Durchsuchen des Datastores {ds.name}", e)
            
            # 3. Identifiziere verwaiste VMDKs
            registered_paths = set(self.raw_data['registered_vmdk_paths'])
            
            for vmdk in self.raw_data['all_vmdk_paths']:
                try:
                    vmdk_path = vmdk['path']
                    
                    # VMDKs aus Templates und Snapshots ausschließen
                    if vmdk_path in registered_paths:
                        vmdk['status'] = 'registered'
                    elif self._is_template_or_snapshot_vmdk(vmdk_path):
                        vmdk['status'] = 'template_or_snapshot'
                    else:
                        vmdk['status'] = 'orphaned'
                        self.raw_data['orphaned_vmdks'].append(vmdk)
                except Exception as e:
                    self.log_error(f"Fehler beim Identifizieren des Status für VMDK {vmdk.get('path', 'Unbekannt')}", e)
            
            # Erfolgreichen Abschluss markieren
            self.collection_status['orphaned_vmdks'] = True
            return self.raw_data
            
        except Exception as e:
            self.log_error("Fehler beim Sammeln der VMDK-Dateien", e)
            return self.raw_data
            
    def _is_template_or_snapshot_vmdk(self, path):
        """Überprüft, ob eine VMDK zu einem Template oder Snapshot gehört"""
        if not path:
            return False
            
        path_lower = path.lower()
        snapshot_indicators = [
            '-snapshot', 
            '-000', 
            '_snapshot', 
            '_delta_',
            'clone',
            'replica'
        ]
        
        # Überprüfe auf Snapshot-Indikatoren
        return any(indicator in path_lower for indicator in snapshot_indicators)

    def get_all_datastores(self):
        """Alle Datastores abrufen"""
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
        """Demo-Modus aktivieren/deaktivieren"""
        self.demo_mode = enabled
        self.logger.info(f"Demo-Modus {'aktiviert' if enabled else 'deaktiviert'}")
        
    def get_error_log(self):
        """Fehlerlog abrufen"""
        return self.error_log