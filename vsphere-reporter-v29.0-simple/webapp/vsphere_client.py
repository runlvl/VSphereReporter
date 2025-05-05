#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VSphere Reporter - VSphere-Client
Dient zur Verbindung mit dem vCenter und zum Abrufen von Informationen
"""

import os
import re
import ssl
import logging
import socket
import humanize
from datetime import datetime, timedelta
import atexit
from functools import wraps

# PyVmomi-Imports
try:
    import pyVmomi
    from pyVmomi import vim
    from pyVim.connect import SmartConnect, Disconnect
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

from webapp.utils.error_handler import VSphereReporterError, handle_vsphere_errors

# Logger konfigurieren
logger = logging.getLogger(__name__)

class VSphereClient:
    """
    Client für die Verbindung zum vCenter und das Abrufen von Informationen.
    """
    
    def __init__(self, host, user, password, ignore_ssl=False):
        """
        Initialisiere den Client mit Verbindungsparametern.
        
        Args:
            host: Hostname oder IP des vCenter-Servers
            user: Benutzername für die Anmeldung
            password: Passwort für die Anmeldung
            ignore_ssl: Bei True werden SSL-Zertifikatsprüfungen deaktiviert
        """
        self.host = host
        self.user = user
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.service_instance = None
        self.content = None
        
        # Überprüfe, ob die PyVmomi-Bibliothek verfügbar ist
        if not HAS_PYVMOMI:
            logger.error("PyVmomi ist nicht installiert. Bitte installieren Sie es mit: pip install pyvmomi")
            raise VSphereReporterError("PyVmomi ist nicht installiert. Bitte installieren Sie es mit: pip install pyvmomi")
    
    @handle_vsphere_errors
    def connect(self):
        """
        Stellt eine Verbindung zum vCenter her.
        
        Raises:
            VSphereReporterError: Bei Verbindungs- oder Authentifizierungsproblemen
        """
        try:
            # SSL-Kontext für die Verbindung vorbereiten
            ssl_context = None
            if self.ignore_ssl:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                ssl_context.verify_mode = ssl.CERT_NONE
            
            # Verbindung herstellen
            logger.info(f"Verbinde mit vCenter {self.host}...")
            self.service_instance = SmartConnect(
                host=self.host,
                user=self.user,
                pwd=self.password,
                sslContext=ssl_context
            )
            
            # Sicherstellen, dass die Verbindung beim Beenden getrennt wird
            atexit.register(Disconnect, self.service_instance)
            
            # Inhalt abrufen für spätere Verwendung
            self.content = self.service_instance.RetrieveContent()
            logger.info(f"Verbindung zu {self.host} erfolgreich hergestellt.")
            
            # Informationen über den vCenter-Server abrufen
            about = self.content.about
            logger.info(f"vCenter-Version: {about.version} (Build: {about.build})")
            logger.info(f"API-Version: {about.apiVersion}")
            
            return True
            
        except vim.fault.InvalidLogin:
            logger.error(f"Anmeldung fehlgeschlagen für Benutzer {self.user} auf Server {self.host}")
            raise VSphereReporterError(f"Anmeldung fehlgeschlagen für Benutzer {self.user} auf Server {self.host}")
            
        except (socket.gaierror, socket.error) as e:
            logger.error(f"Netzwerkfehler bei Verbindung zu {self.host}: {str(e)}")
            raise VSphereReporterError(f"Netzwerkfehler bei Verbindung zu {self.host}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Fehler beim Verbinden mit {self.host}: {str(e)}")
            raise VSphereReporterError(f"Fehler beim Verbinden mit {self.host}: {str(e)}")
    
    def disconnect(self):
        """
        Trennt die Verbindung zum vCenter.
        """
        if self.service_instance:
            Disconnect(self.service_instance)
            self.service_instance = None
            self.content = None
            logger.info(f"Verbindung zu {self.host} getrennt.")
    
    def is_connected(self):
        """
        Prüft, ob eine aktive Verbindung besteht.
        
        Returns:
            bool: True, wenn eine Verbindung aktiv ist
        """
        return self.service_instance is not None and self.content is not None
    
    @handle_vsphere_errors
    def get_vmware_tools_status(self):
        """
        Sammelt Informationen über den Status der VMware Tools für alle VMs.
        
        Returns:
            list: Liste von Dictionaries mit VM-Namen, Tools-Version, Status und Power-Status
        """
        if not self.is_connected():
            logger.error("Nicht mit vCenter verbunden.")
            raise VSphereReporterError("Nicht mit vCenter verbunden.")
        
        logger.info("Sammle Informationen über VMware Tools...")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        vm_list = container.view
        container.Destroy()
        
        result = []
        for vm in vm_list:
            # Power-Status bestimmen
            power_state = "Unbekannt"
            if vm.runtime.powerState == vim.VirtualMachine.PowerState.poweredOn:
                power_state = "Eingeschaltet"
            elif vm.runtime.powerState == vim.VirtualMachine.PowerState.poweredOff:
                power_state = "Ausgeschaltet"
            elif vm.runtime.powerState == vim.VirtualMachine.PowerState.suspended:
                power_state = "Angehalten"
            
            # Tools-Status bestimmen
            tools_status = "Nicht installiert"
            tools_version = "Nicht verfügbar"
            tools_version_status = "Nicht verfügbar"
            
            if vm.guest and vm.guest.toolsStatus:
                if vm.guest.toolsStatus == "toolsOk":
                    tools_status = "OK"
                elif vm.guest.toolsStatus == "toolsOld":
                    tools_status = "Veraltet"
                elif vm.guest.toolsStatus == "toolsNotRunning":
                    tools_status = "Nicht ausgeführt"
                elif vm.guest.toolsStatus == "toolsNotInstalled":
                    tools_status = "Nicht installiert"
                
                # Tools-Version
                if vm.config and vm.config.tools and vm.config.tools.toolsVersion:
                    tools_version = vm.config.tools.toolsVersion
                    
                    # Tools-Version-Status
                    if vm.guest.toolsVersionStatus:
                        if vm.guest.toolsVersionStatus == "guestToolsCurrent":
                            tools_version_status = "Aktuell"
                        elif vm.guest.toolsVersionStatus == "guestToolsNeedUpgrade":
                            tools_version_status = "Aktualisierung erforderlich"
                        elif vm.guest.toolsVersionStatus == "guestToolsSupportedOld":
                            tools_version_status = "Veraltet, aber unterstützt"
                        elif vm.guest.toolsVersionStatus == "guestToolsSupportedNew":
                            tools_version_status = "Neuer als Host"
                        elif vm.guest.toolsVersionStatus == "guestToolsTooOld":
                            tools_version_status = "Zu alt"
                        elif vm.guest.toolsVersionStatus == "guestToolsNotInstalled":
                            tools_version_status = "Nicht installiert"
                        else:
                            tools_version_status = vm.guest.toolsVersionStatus
            
            vm_data = {
                'name': vm.name,
                'power_state': power_state,
                'tools_status': tools_status,
                'tools_version': tools_version,
                'tools_version_status': tools_version_status,
                'status': 'ok' if tools_status == 'OK' else 'outdated'
            }
            
            result.append(vm_data)
        
        # Nach Namen sortieren
        result.sort(key=lambda x: x['name'])
        
        logger.info(f"Gesammelt: {len(result)} VMs mit VMware Tools-Informationen")
        return result
    
    @handle_vsphere_errors
    def get_snapshots(self):
        """
        Sammelt Informationen über VM-Snapshots.
        
        Returns:
            list: Liste von Snapshot-Informationen (VM-Name, Snapshot-Name, Erstellungsdatum, Alter, Größe)
        """
        if not self.is_connected():
            logger.error("Nicht mit vCenter verbunden.")
            raise VSphereReporterError("Nicht mit vCenter verbunden.")
        
        logger.info("Sammle Informationen über VM-Snapshots...")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        vm_list = container.view
        container.Destroy()
        
        result = []
        for vm in vm_list:
            if vm.snapshot:
                snapshots = self._get_vm_snapshots(vm)
                result.extend(snapshots)
        
        # Nach Alter sortieren (älteste zuerst)
        result.sort(key=lambda x: x.get('age_days', 0), reverse=True)
        
        logger.info(f"Gesammelt: {len(result)} Snapshots")
        return result
    
    def _get_vm_snapshots(self, vm):
        """
        Sammelt rekursiv Snapshot-Informationen für eine VM.
        
        Args:
            vm: Virtual Machine-Objekt
            
        Returns:
            list: Liste von Snapshot-Informationen
        """
        if not vm.snapshot:
            return []
        
        result = []
        
        def process_snapshot_tree(node, tree_location):
            # Snapshot-Alter berechnen
            create_time = node.createTime
            current_time = datetime.now()
            # Zeitzone anpassen, wenn create_time ein Offset hat
            if create_time.tzinfo:
                current_time = datetime.now(create_time.tzinfo)
            
            age = current_time - create_time
            age_days = age.days
            age_hours = age.seconds // 3600
            
            # Snapshot-Größe abschätzen
            size_bytes = 0
            if hasattr(node, 'vm') and hasattr(node.vm, 'layoutEx') and node.vm.layoutEx:
                for file in node.vm.layoutEx.file:
                    if hasattr(file, 'type') and hasattr(file, 'size'):
                        if file.type == "snapshotData" and file.size:
                            size_bytes += file.size
            
            # Humanize-Größe formatieren
            if size_bytes > 0:
                size_human = humanize.naturalsize(size_bytes, binary=True)
            else:
                size_human = "Unbekannt"
            
            # Status für UI-Formatierung
            if age_days > 30:
                status = "danger"  # Sehr alte Snapshots
            elif age_days > 7:
                status = "warning"  # Alte Snapshots
            else:
                status = "ok"  # Neuere Snapshots
            
            # Snapshot-Informationen sammeln
            snapshot_info = {
                'vm_name': vm.name,
                'name': node.name,
                'description': node.description if node.description else '',
                'create_time': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'age_days': age_days,
                'age_hours': age_hours,
                'age_text': f"{age_days} Tage, {age_hours} Stunden",
                'size_bytes': size_bytes,
                'size_human': size_human,
                'tree_location': tree_location,
                'status': status
            }
            
            result.append(snapshot_info)
            
            # Rekursiv durch Kinder gehen
            if node.childSnapshotList:
                for i, child in enumerate(node.childSnapshotList):
                    process_snapshot_tree(child, f"{tree_location}.{i+1}")
        
        # Root-Snapshots verarbeiten
        for i, root_snapshot in enumerate(vm.snapshot.rootSnapshotList):
            process_snapshot_tree(root_snapshot, str(i+1))
        
        return result
    
    @handle_vsphere_errors
    def get_orphaned_vmdks(self):
        """
        Sammelt Informationen über verwaiste VMDK-Dateien.
        
        Returns:
            list: Liste von verwaisten VMDK-Informationen (Datastore, Pfad, Größe)
        """
        if not self.is_connected():
            logger.error("Nicht mit vCenter verbunden.")
            raise VSphereReporterError("Nicht mit vCenter verbunden.")
        
        logger.info("Sammle Informationen über verwaiste VMDK-Dateien...")
        
        # Datastore-Abruf
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Datastore], True
        )
        
        datastores = container.view
        container.Destroy()
        
        result = []
        for datastore in datastores:
            try:
                # Browser für den Datastore abrufen
                browser = datastore.browser
                
                # Datastore-Pfad
                ds_path = f"[{datastore.name}]"
                
                # Durchsuche nach VMDK-Dateien
                search_spec = vim.HostDatastoreBrowserSearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                
                # Ausschließen von *-flat.vmdk und *-delta.vmdk, da diese zu regulären VMDKs gehören
                search_spec.searchCaseInsensitive = True
                
                # Suche durchführen
                task = browser.SearchDatastoreSubFolders_Task(
                    datastorePath=ds_path, searchSpec=search_spec
                )
                
                # Warten auf Abschluss der Aufgabe
                self._wait_for_task(task)
                
                # Ergebnisse prüfen
                search_results = task.info.result
                
                if search_results:
                    for search_result in search_results:
                        folder_path = search_result.folderPath
                        
                        # Für jede gefundene VMDK in diesem Ordner
                        for file_info in search_result.file:
                            # Flat-VMDKs und Delta-VMDKs überspringen
                            if file_info.path.endswith("-flat.vmdk") or file_info.path.endswith("-delta.vmdk"):
                                continue
                            
                            # Prüfen, ob die VMDK verwaist ist
                            if self._is_vmdk_orphaned(folder_path, file_info.path):
                                # Verwaiste VMDK gefunden
                                vmdk_path = f"{folder_path}/{file_info.path}"
                                
                                # Größe formatieren
                                size_bytes = file_info.fileSize
                                size_human = humanize.naturalsize(size_bytes, binary=True)
                                
                                # Info-Sammlung
                                orphaned_info = {
                                    'datastore': datastore.name,
                                    'path': vmdk_path,
                                    'file_name': file_info.path,
                                    'folder_path': folder_path,
                                    'size_bytes': size_bytes,
                                    'size_human': size_human,
                                    'modified': file_info.modification.strftime('%Y-%m-%d %H:%M:%S') if hasattr(file_info, 'modification') else 'Unbekannt'
                                }
                                
                                result.append(orphaned_info)
                
            except Exception as e:
                logger.warning(f"Fehler beim Durchsuchen von Datastore {datastore.name}: {str(e)}")
        
        # Nach Größe sortieren (größte zuerst)
        result.sort(key=lambda x: x.get('size_bytes', 0), reverse=True)
        
        logger.info(f"Gesammelt: {len(result)} verwaiste VMDK-Dateien")
        return result
    
    def _is_vmdk_orphaned(self, folder_path, vmdk_name):
        """
        Prüft, ob eine VMDK-Datei verwaist ist.
        
        Eine VMDK wird als verwaist betrachtet, wenn:
        1. Sie nicht mit einer aktiven VM verbunden ist
        2. Sie nicht von einer VM-Template verwendet wird
        3. Es keine zugehörige .vmx-Datei gibt
        
        Args:
            folder_path: Pfad zum Datastore-Ordner
            vmdk_name: Name der VMDK-Datei
            
        Returns:
            bool: True, wenn die VMDK verwaist ist
        """
        try:
            # Überprüfen, ob eine .vmx-Datei im gleichen Ordner existiert
            datastore_name = re.match(r'\[(.*?)\]', folder_path).group(1)
            container = self.content.viewManager.CreateContainerView(
                self.content.rootFolder, [vim.Datastore], True
            )
            
            # Datastore finden
            datastore = None
            for ds in container.view:
                if ds.name == datastore_name:
                    datastore = ds
                    break
            
            container.Destroy()
            
            if not datastore:
                logger.warning(f"Datastore nicht gefunden: {datastore_name}")
                return False
            
            # Relativen Pfad aus dem Datastore-Pfad extrahieren
            folder_relative_path = folder_path.replace(f"[{datastore_name}] ", "")
            
            # Browser für den Datastore abrufen
            browser = datastore.browser
            
            # Durchsuche nach VMX-Dateien im gleichen Ordner
            search_spec = vim.HostDatastoreBrowserSearchSpec()
            search_spec.matchPattern = ["*.vmx"]
            
            # Suche durchführen
            task = browser.SearchDatastore_Task(
                datastorePath=folder_path, searchSpec=search_spec
            )
            
            # Warten auf Abschluss der Aufgabe
            self._wait_for_task(task)
            
            # Prüfen, ob VMX-Dateien gefunden wurden
            search_result = task.info.result
            
            if search_result and search_result.file:
                # Es gibt VMX-Dateien im gleichen Ordner, also prüfen wir weiter
                
                # Prüfen, ob die VMDK in einer VM verwendet wird
                container = self.content.viewManager.CreateContainerView(
                    self.content.rootFolder, [vim.VirtualMachine], True
                )
                
                for vm in container.view:
                    if vm.config and vm.config.hardware and vm.config.hardware.device:
                        for device in vm.config.hardware.device:
                            if isinstance(device, vim.vm.device.VirtualDisk) and device.backing:
                                if hasattr(device.backing, 'fileName'):
                                    disk_path = device.backing.fileName
                                    
                                    # VMDK-Pfad aus Gerätedatei extrahieren
                                    if vmdk_name in disk_path:
                                        container.Destroy()
                                        return False  # VMDK wird von einer VM verwendet
                
                container.Destroy()
                
                # Die VMDK könnte zu einer VM gehören, die gerade ausgeschaltet ist oder nicht vollständig registriert ist
                # Dies erfordert weitere Kontextprüfungen...
                return True  # Vorläufig als verwaist betrachten
            else:
                # Keine VMX-Dateien gefunden, höchstwahrscheinlich verwaist
                return True
            
        except Exception as e:
            logger.warning(f"Fehler beim Prüfen des VMDK-Status für {vmdk_name}: {str(e)}")
            return False  # Im Zweifelsfall als nicht verwaist betrachten
    
    def _wait_for_task(self, task):
        """
        Wartet auf den Abschluss einer vCenter-Aufgabe.
        
        Args:
            task: Die Aufgabe, auf die gewartet werden soll
            
        Returns:
            Task-Ergebnis
        """
        while task.info.state == vim.TaskInfo.State.running:
            pass
        
        if task.info.state != vim.TaskInfo.State.success:
            if task.info.error:
                raise Exception(task.info.error.msg)
        
        return task.info.result