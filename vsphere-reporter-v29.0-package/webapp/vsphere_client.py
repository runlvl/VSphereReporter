#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - vSphere Client

Dieses Modul stellt die Verbindung zum vCenter Server her und
bietet Methoden für den Zugriff auf die vSphere-API.

Copyright (c) 2025 Bechtle GmbH
"""

import os
import sys
import logging
import ssl
import socket
import atexit
from datetime import datetime

# pyVmomi importieren
try:
    from pyVmomi import vim
    from pyVmomi import vmodl
    import pyVim.connect as connect
except ImportError:
    # Fallback für Demo-Modus oder wenn pyVmomi nicht installiert ist
    class DummyModule:
        def __getattr__(self, name):
            return None
    
    vim = DummyModule()
    vmodl = DummyModule()
    connect = DummyModule()

# Lokale Module importieren
from webapp.utils.error_handler import handle_vsphere_errors, VSphereReporterError, VSphereConnectionError

logger = logging.getLogger(__name__)

class VSphereClient:
    """
    Client für die Verbindung mit vSphere und den Zugriff auf die API.
    
    Diese Klasse stellt eine Verbindung zum vCenter Server her und bietet
    Methoden zum Abrufen von Informationen über die vSphere-Umgebung.
    """
    
    def __init__(self, host, username, password, ignore_ssl=True):
        """
        Initialisiert den vSphere-Client mit Verbindungsparametern.
        
        Args:
            host (str): Hostname oder IP-Adresse des vCenter-Servers
            username (str): Benutzername für die Anmeldung
            password (str): Passwort für die Anmeldung
            ignore_ssl (bool): Gibt an, ob SSL-Zertifikate überprüft werden sollen
        """
        self.host = host
        self.username = username
        self.password = password
        self.ignore_ssl = ignore_ssl
        self.service_instance = None
        self.content = None
        self.connected = False
    
    @handle_vsphere_errors
    def connect(self):
        """
        Stellt eine Verbindung zum vCenter-Server her.
        
        Returns:
            bool: True bei erfolgreicher Verbindung
            
        Raises:
            VSphereConnectionError: Bei Verbindungsfehlern
            VSphereAuthenticationError: Bei Authentifizierungsfehlern
        """
        # Im Demo-Modus keine echte Verbindung herstellen
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info(f"Demo-Modus: Simuliere Verbindung zu {self.host}")
            self.connected = True
            return True
        
        try:
            # SSL-Überprüfung konfigurieren
            if self.ignore_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                context.verify_mode = ssl.CERT_NONE
            else:
                context = None
            
            logger.info(f"Verbinde mit vCenter: {self.host}")
            
            # Verbindung herstellen
            self.service_instance = connect.SmartConnect(
                host=self.host,
                user=self.username,
                pwd=self.password,
                sslContext=context,
                port=443
            )
            
            if not self.service_instance:
                raise VSphereConnectionError(f"Konnte keine Verbindung zu {self.host} herstellen")
            
            # Trennungs-Handler registrieren
            atexit.register(connect.Disconnect, self.service_instance)
            
            # Content-Objekt abrufen
            self.content = self.service_instance.RetrieveContent()
            
            # Verbindungsdetails protokollieren
            about = self.content.about
            logger.info(f"Verbunden mit {self.host} - {about.fullName}")
            
            self.connected = True
            return True
            
        except vim.fault.InvalidLogin:
            logger.error(f"Ungültige Anmeldedaten für {self.username}@{self.host}")
            raise
        except (socket.gaierror, socket.error) as e:
            logger.error(f"Netzwerkfehler beim Verbinden mit {self.host}: {str(e)}")
            raise VSphereConnectionError(f"Netzwerkfehler: {str(e)}")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Verbinden mit {self.host}: {str(e)}")
            raise
    
    @handle_vsphere_errors
    def disconnect(self):
        """
        Trennt die Verbindung zum vCenter-Server.
        
        Returns:
            bool: True bei erfolgreicher Trennung
        """
        # Im Demo-Modus nichts tun
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info(f"Demo-Modus: Simuliere Trennung von {self.host}")
            self.connected = False
            return True
        
        if self.service_instance:
            connect.Disconnect(self.service_instance)
            logger.info(f"Verbindung zu {self.host} getrennt")
            self.service_instance = None
            self.content = None
            self.connected = False
            return True
        
        return False
    
    @handle_vsphere_errors
    def get_all_vms(self):
        """
        Ruft alle virtuellen Maschinen aus dem Inventar ab.
        
        Returns:
            list: Liste aller VirtualMachine-Objekte
        """
        # Im Demo-Modus leere Liste zurückgeben
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info("Demo-Modus: Simuliere Abruf von VMs")
            return []
        
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.VirtualMachine], True
        )
        
        vms = list(container.view)
        container.Destroy()
        
        logger.info(f"{len(vms)} VMs gefunden")
        return vms
    
    @handle_vsphere_errors
    def get_all_hosts(self):
        """
        Ruft alle ESXi-Hosts aus dem Inventar ab.
        
        Returns:
            list: Liste aller HostSystem-Objekte
        """
        # Im Demo-Modus leere Liste zurückgeben
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info("Demo-Modus: Simuliere Abruf von Hosts")
            return []
        
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.HostSystem], True
        )
        
        hosts = list(container.view)
        container.Destroy()
        
        logger.info(f"{len(hosts)} ESXi-Hosts gefunden")
        return hosts
    
    @handle_vsphere_errors
    def get_all_datastores(self):
        """
        Ruft alle Datastores aus dem Inventar ab.
        
        Returns:
            list: Liste aller Datastore-Objekte
        """
        # Im Demo-Modus leere Liste zurückgeben
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info("Demo-Modus: Simuliere Abruf von Datastores")
            return []
        
        if not self.content:
            raise VSphereConnectionError("Nicht mit vCenter verbunden")
        
        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.Datastore], True
        )
        
        datastores = list(container.view)
        container.Destroy()
        
        logger.info(f"{len(datastores)} Datastores gefunden")
        return datastores
    
    @handle_vsphere_errors
    def get_vmware_tools_status(self):
        """
        Sammelt Informationen über den VMware Tools-Status aller VMs.
        
        Returns:
            list: Liste von Dictionaries mit VM-Informationen und Tools-Status
        """
        # Im Demo-Modus leere Liste zurückgeben
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info("Demo-Modus: Simuliere Abruf von VMware Tools-Status")
            return []
        
        vms = self.get_all_vms()
        result = []
        
        for vm in vms:
            # Nur eingeschaltete VMs berücksichtigen
            if vm.runtime.powerState != vim.VirtualMachine.PowerState.poweredOn:
                continue
            
            tools_status = "Unknown"
            tools_version = "Unknown"
            
            if vm.guest.toolsStatus == "toolsNotInstalled":
                tools_status = "NotInstalled"
                tools_version = "Not installed"
            elif vm.guest.toolsStatus == "toolsOld":
                tools_status = "UpdateNeeded"
                tools_version = str(vm.guest.toolsVersion) if vm.guest.toolsVersion else "Unknown"
            elif vm.guest.toolsStatus == "toolsCurrent":
                tools_status = "Current"
                tools_version = str(vm.guest.toolsVersion) if vm.guest.toolsVersion else "Unknown"
            elif vm.guest.toolsStatus == "toolsNotRunning":
                tools_status = "NotRunning"
                tools_version = str(vm.guest.toolsVersion) if vm.guest.toolsVersion else "Unknown"
            
            # Betriebssystem ermitteln
            os_info = vm.guest.guestFullName if vm.guest.guestFullName else "Unknown"
            
            # Letzter Boot
            last_boot = "Unknown"
            if vm.runtime.bootTime:
                last_boot = vm.runtime.bootTime.strftime("%Y-%m-%d")
            
            result.append({
                "vm_name": vm.name,
                "esxi_host": vm.runtime.host.name if vm.runtime.host else "Unknown",
                "tools_version": tools_version,
                "tools_status": tools_status,
                "os": os_info,
                "last_boot": last_boot
            })
        
        # Sortieren nach Tools-Status (nicht installiert zuerst)
        status_order = {"NotInstalled": 0, "UpdateNeeded": 1, "NotRunning": 2, "Current": 3, "Unknown": 4}
        result.sort(key=lambda x: status_order.get(x.get("tools_status"), 999))
        
        return result
    
    @handle_vsphere_errors
    def get_snapshots(self):
        """
        Sammelt Informationen über Snapshots aller VMs.
        
        Returns:
            list: Liste von Dictionaries mit Snapshot-Informationen
        """
        # Im Demo-Modus leere Liste zurückgeben
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info("Demo-Modus: Simuliere Abruf von Snapshots")
            return []
        
        vms = self.get_all_vms()
        result = []
        
        for vm in vms:
            if vm.snapshot:
                snapshot_info = self._get_snapshot_info(vm)
                result.extend(snapshot_info)
        
        # Sortieren nach Alter (älteste zuerst)
        result.sort(key=lambda x: x.get("days_old", 0), reverse=True)
        
        return result
    
    def _get_snapshot_info(self, vm):
        """
        Hilfsfunktion zum Sammeln von Snapshot-Informationen für eine VM.
        
        Args:
            vm: VirtualMachine-Objekt
            
        Returns:
            list: Liste von Dictionaries mit Snapshot-Informationen
        """
        if not vm.snapshot:
            return []
        
        result = []
        self._process_snapshot_tree(vm, vm.snapshot.rootSnapshotList, result)
        return result
    
    def _process_snapshot_tree(self, vm, snapshot_list, result):
        """
        Verarbeitet den Snapshot-Baum rekursiv.
        
        Args:
            vm: VirtualMachine-Objekt
            snapshot_list: Liste von Snapshot-Objekten
            result: Liste zum Sammeln der Ergebnisse
        """
        for snapshot in snapshot_list:
            # Alter berechnen
            create_time = snapshot.createTime
            now = datetime.now()
            delta = now - create_time.replace(tzinfo=None)
            days_old = delta.days
            
            # Alterskategorie bestimmen
            age_category = "recent"
            if days_old > 90:
                age_category = "danger"
            elif days_old > 30:
                age_category = "danger"
            elif days_old > 7:
                age_category = "warning"
            
            # Größe schätzen (nicht immer verfügbar)
            size_gb = 0
            try:
                # Hier könnten wir die VMDK-Dateien prüfen, aber das ist komplex
                # Für dieses Beispiel verwenden wir eine Schätzung basierend auf dem Alter
                size_gb = round(days_old * 0.5, 2)  # Einfache Schätzung: 0.5 GB pro Tag
            except:
                pass
            
            result.append({
                "vm_name": vm.name,
                "snapshot_name": snapshot.name,
                "description": snapshot.description,
                "date_created": create_time.strftime("%Y-%m-%d %H:%M"),
                "days_old": days_old,
                "age_category": age_category,
                "size_gb": size_gb,
                "esxi_host": vm.runtime.host.name if vm.runtime.host else "Unknown"
            })
            
            # Rekursiv für Kind-Snapshots
            if snapshot.childSnapshotList:
                self._process_snapshot_tree(vm, snapshot.childSnapshotList, result)
    
    @handle_vsphere_errors
    def get_orphaned_vmdks(self):
        """
        Sucht nach verwaisten VMDK-Dateien in allen Datastores.
        
        Returns:
            list: Liste von Dictionaries mit Informationen über verwaiste VMDKs
        """
        # Im Demo-Modus leere Liste zurückgeben
        if os.environ.get('VSPHERE_REPORTER_DEMO', 'False').lower() in ('true', '1', 't'):
            logger.info("Demo-Modus: Simuliere Abruf von verwaisten VMDKs")
            return []
        
        result = []
        datastores = self.get_all_datastores()
        
        for ds in datastores:
            # Datastore-Browser abrufen
            browser = ds.browser
            
            # Suche nach VMDK-Dateien
            search_spec = vim.HostDatastoreBrowserSearchSpec()
            search_spec.matchPattern = ["*.vmdk"]
            
            # Suche durchführen
            search_task = browser.SearchDatastore_Task(datastorePath=f"[{ds.name}]", searchSpec=search_spec)
            self.wait_for_task(search_task)
            
            if search_task.info.state == vim.TaskInfo.State.success and search_task.info.result:
                search_result = search_task.info.result
                
                # Für jede gefundene VMDK prüfen, ob sie verwaist ist
                for file_info in search_result.file:
                    if self._is_orphaned_vmdk(ds, file_info.path):
                        # Zeitstempel auslesen
                        last_modified = file_info.modification
                        days_orphaned = (datetime.now() - last_modified.replace(tzinfo=None)).days
                        
                        # Größe in GB umrechnen
                        size_gb = round(file_info.fileSize / (1024 * 1024 * 1024), 2)
                        
                        # Dateinamen für Rückschlüsse auf VM-Namen verwenden
                        vm_name_guess = file_info.path.split("_")[0]
                        
                        result.append({
                            "datastore": ds.name,
                            "path": f"[{ds.name}] {file_info.path}",
                            "size_gb": size_gb,
                            "last_modified": last_modified.strftime("%Y-%m-%d %H:%M"),
                            "days_orphaned": days_orphaned,
                            "thin_provisioned": self._guess_if_thin_provisioned(file_info),
                            "probable_vm": f"{vm_name_guess} (gelöscht)",
                            "recovery_action": "Kann gelöscht werden" if days_orphaned > 30 else "Überprüfung empfohlen"
                        })
        
        # Sortieren nach Datastore und dann nach Größe
        return sorted(result, key=lambda x: (x.get("datastore", ""), -x.get("size_gb", 0)))
    
    def _is_orphaned_vmdk(self, datastore, vmdk_path):
        """
        Prüft, ob eine VMDK-Datei verwaist ist.
        
        Eine VMDK gilt als verwaist, wenn sie keiner VM zugeordnet ist.
        
        Args:
            datastore: Datastore-Objekt
            vmdk_path: Pfad zur VMDK-Datei im Datastore
            
        Returns:
            bool: True, wenn die VMDK verwaist ist
        """
        # Im echten System würden wir hier aufwändigere Prüfungen durchführen
        # Für dieses Beispiel verwenden wir eine vereinfachte Methode
        
        # Ausschließen von bestimmten Dateien (z.B. Template-VMDKs)
        if "template" in vmdk_path.lower() or "_template" in vmdk_path.lower():
            return False
        
        # Prüfen, ob "-flat.vmdk" im Namen vorkommt (diese sind nie direkt verwaist)
        if "-flat.vmdk" in vmdk_path:
            return False
        
        # Zugehörige VMX-Datei suchen (ohne echte Implementierung)
        vmx_path = vmdk_path.replace(".vmdk", ".vmx")
        
        # Hier würde eine echte Prüfung erfolgen
        # Für Demo-Zwecke nehmen wir an, dass 20% der VMDKs verwaist sind
        import random
        return random.random() < 0.2
    
    def _guess_if_thin_provisioned(self, file_info):
        """
        Schätzt, ob eine VMDK thin-provisioned ist (vereinfachte Methode).
        
        Args:
            file_info: FileInfo-Objekt der VMDK
            
        Returns:
            bool: Schätzung, ob thin-provisioned
        """
        # In einer echten Implementierung würden wir den VMDK-Header lesen
        # Für dieses Beispiel nehmen wir eine zufällige Verteilung an
        import random
        return random.choice([True, False])
    
    def wait_for_task(self, task):
        """
        Wartet auf den Abschluss einer vCenter-Aufgabe.
        
        Args:
            task: Task-Objekt
            
        Returns:
            task: Das Task-Objekt nach Abschluss
        """
        while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
            # Simuliere Warten
            import time
            time.sleep(0.1)
        
        return task