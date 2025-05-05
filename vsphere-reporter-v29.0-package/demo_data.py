#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Demo-Daten
Copyright (c) 2025 Bechtle GmbH

Dieses Modul generiert Beispieldaten für den Demo-Modus.
"""

import random
import datetime
import uuid
import logging
from typing import Dict, List, Any

def generate_demo_data() -> Dict[str, Any]:
    """
    Generiert Beispieldaten für den Demo-Modus.
    
    Returns:
        Dictionary mit Demo-Daten
    """
    logging.info("Generiere Demo-Daten...")
    
    # Aktuelle Zeit für realistische Zeitstempel
    now = datetime.datetime.now()
    
    # VMs generieren
    vms = generate_vms(30)
    
    # Hosts generieren
    hosts = generate_hosts(5)
    
    # Datastores generieren
    datastores = generate_datastores(10)
    
    # Netzwerke generieren
    networks = generate_networks(6)
    
    # VMware Tools generieren
    vmware_tools = generate_vmware_tools(vms)
    
    # Snapshots generieren
    snapshots = generate_snapshots(vms)
    
    # Verwaiste VMDKs generieren
    orphaned_vmdks = generate_orphaned_vmdks(datastores)
    
    # Gesamtdaten zurückgeben
    return {
        'vms': vms,
        'hosts': hosts,
        'datastores': datastores,
        'networks': networks,
        'vmware_tools': vmware_tools,
        'snapshots': snapshots,
        'orphaned_vmdks': orphaned_vmdks
    }

def generate_vms(count: int) -> List[Dict[str, Any]]:
    """
    Generiert eine Liste von virtuellen Maschinen für den Demo-Modus.
    
    Args:
        count: Anzahl der zu generierenden VMs
        
    Returns:
        Liste von VM-Daten
    """
    os_types = [
        "Windows Server 2022", "Windows Server 2019", "Windows Server 2016",
        "Ubuntu Server 22.04 LTS", "Ubuntu Server 20.04 LTS",
        "SUSE Linux Enterprise Server 15", "SUSE Linux Enterprise Server 12",
        "Red Hat Enterprise Linux 9", "Red Hat Enterprise Linux 8",
        "CentOS 7", "Debian 11", "Debian 10"
    ]
    
    power_states = ["poweredOn", "poweredOff", "suspended"]
    power_weights = [0.8, 0.15, 0.05]  # 80% laufend, 15% ausgeschaltet, 5% pausiert
    
    vms = []
    for i in range(count):
        vm_name = f"vm-{i+1:03d}"
        
        # VM-Namen nach Verwendungszweck benennen
        if i < 5:
            vm_name = f"db-server-{i+1:02d}"
        elif i < 10:
            vm_name = f"web-server-{i+1:02d}"
        elif i < 15:
            vm_name = f"app-server-{i+1:02d}"
        elif i < 20:
            vm_name = f"dc-server-{i+1:02d}"
        elif i < 25:
            vm_name = f"test-server-{i+1:02d}"
        
        # Zufällige Werte für jede VM
        power_state = random.choices(power_states, weights=power_weights, k=1)[0]
        vm = {
            'name': vm_name,
            'uuid': str(uuid.uuid4()),
            'power_state': power_state,
            'guest_os': random.choice(os_types),
            'num_cpu': random.choice([1, 2, 4, 8, 16]),
            'memory_mb': random.choice([1024, 2048, 4096, 8192, 16384, 32768]),
            'used_space': random.randint(10, 500) * 1024 * 1024 * 1024,  # in Bytes
            'provisioned_space': random.randint(20, 1000) * 1024 * 1024 * 1024,  # in Bytes
            'creation_date': (datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d %H:%M:%S"),
            'host': f"esx-host-{random.randint(1, 5):02d}.lab.local",
            'datastore': f"datastore-{random.randint(1, 10):02d}"
        }
        vms.append(vm)
    
    return vms

def generate_hosts(count: int) -> List[Dict[str, Any]]:
    """
    Generiert eine Liste von ESXi-Hosts für den Demo-Modus.
    
    Args:
        count: Anzahl der zu generierenden Hosts
        
    Returns:
        Liste von Host-Daten
    """
    esx_versions = ["7.0.3", "7.0.2", "7.0.1", "7.0.0", "6.7.0", "6.5.0"]
    connection_states = ["connected", "disconnected", "notResponding"]
    connection_weights = [0.9, 0.08, 0.02]  # 90% verbunden, 8% getrennt, 2% nicht ansprechbar
    
    hosts = []
    for i in range(count):
        cpu_cores = random.choice([16, 24, 32, 48, 64])
        memory_gb = random.choice([64, 128, 256, 384, 512])
        
        host = {
            'name': f"esx-host-{i+1:02d}.lab.local",
            'uuid': str(uuid.uuid4()),
            'version': random.choice(esx_versions),
            'connection_state': random.choices(connection_states, weights=connection_weights, k=1)[0],
            'cpu_model': f"Intel(R) Xeon(R) Gold {random.choice(['5218', '6230', '6248', '6258R', '6348'])} CPU @ {random.choice(['2.30', '2.40', '2.50', '2.70'])}GHz",
            'cpu_cores': cpu_cores,
            'cpu_threads': cpu_cores * 2,
            'memory_size': memory_gb * 1024 * 1024 * 1024,  # in Bytes
            'in_maintenance_mode': random.choices([True, False], weights=[0.05, 0.95], k=1)[0],
            'uptime': random.randint(1, 365) * 24 * 60 * 60  # in Sekunden
        }
        hosts.append(host)
    
    return hosts

def generate_datastores(count: int) -> List[Dict[str, Any]]:
    """
    Generiert eine Liste von Datastores für den Demo-Modus.
    
    Args:
        count: Anzahl der zu generierenden Datastores
        
    Returns:
        Liste von Datastore-Daten
    """
    datastore_types = ["VMFS", "NFS", "vVOL", "vSAN"]
    datastore_weights = [0.6, 0.2, 0.1, 0.1]  # 60% VMFS, 20% NFS, 10% vVOL, 10% vSAN
    
    datastores = []
    for i in range(count):
        capacity_gb = random.randint(500, 10000)
        free_space_percentage = random.uniform(0.05, 0.8)
        
        datastore = {
            'name': f"datastore-{i+1:02d}",
            'uuid': str(uuid.uuid4()),
            'type': random.choices(datastore_types, weights=datastore_weights, k=1)[0],
            'capacity': capacity_gb * 1024 * 1024 * 1024,  # in Bytes
            'free_space': int(capacity_gb * free_space_percentage * 1024 * 1024 * 1024),  # in Bytes
            'accessible': random.choices([True, False], weights=[0.95, 0.05], k=1)[0],
            'maintenance_mode': random.choices([None, "entering", "normal", "inMaintenance"], weights=[0.95, 0.02, 0.02, 0.01], k=1)[0]
        }
        datastores.append(datastore)
    
    return datastores

def generate_networks(count: int) -> List[Dict[str, Any]]:
    """
    Generiert eine Liste von Netzwerken für den Demo-Modus.
    
    Args:
        count: Anzahl der zu generierenden Netzwerke
        
    Returns:
        Liste von Netzwerk-Daten
    """
    network_types = ["VirtualSwitch", "DistributedVirtualSwitch"]
    
    networks = []
    for i in range(count):
        network = {
            'name': f"VLAN-{(i+1)*10}",
            'uuid': str(uuid.uuid4()),
            'type': random.choice(network_types),
            'vlan_id': (i+1) * 10,
            'host_count': random.randint(1, 5),
            'vm_count': random.randint(0, 20)
        }
        networks.append(network)
    
    return networks

def generate_vmware_tools(vms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generiert VMware Tools-Informationen für den Demo-Modus.
    
    Args:
        vms: Liste der VMs
        
    Returns:
        Liste von VMware Tools-Daten
    """
    tools_versions = [
        "12200", "12100", "12000", "11500", "11400", "11300", 
        "11200", "11100", "11000", "10500", "10400", "10300"
    ]
    tools_status = [
        "toolsOk", "toolsNotInstalled", "toolsOld", "toolsNotRunning"
    ]
    tools_weights = [0.7, 0.05, 0.2, 0.05]  # 70% OK, 5% nicht installiert, 20% veraltet, 5% nicht ausgeführt
    
    vmware_tools = []
    for i, vm in enumerate(vms):
        # Bei einigen VMs die VMware Tools absichtlich veralten lassen oder fehlen lassen
        adjusted_weights = tools_weights.copy()
        if i % 7 == 0:  # Etwa jede 7. VM hat keine Tools
            adjusted_weights = [0.05, 0.8, 0.1, 0.05]
        elif i % 5 == 0:  # Etwa jede 5. VM hat veraltete Tools
            adjusted_weights = [0.1, 0.05, 0.8, 0.05]
        
        tool = {
            'vm_name': vm['name'],
            'version': random.choice(tools_versions),
            'status': random.choices(tools_status, weights=adjusted_weights, k=1)[0],
            'upgrade_available': random.choices([True, False], weights=[0.3, 0.7], k=1)[0],
            'last_update': (datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 500))).strftime("%Y-%m-%d %H:%M:%S")
        }
        vmware_tools.append(tool)
    
    # Sortiere nach Version (älteste zuerst)
    vmware_tools.sort(key=lambda x: x['version'])
    
    return vmware_tools

def generate_snapshots(vms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generiert Snapshot-Informationen für den Demo-Modus.
    
    Args:
        vms: Liste der VMs
        
    Returns:
        Liste von Snapshot-Daten
    """
    # Nur 40% der VMs haben Snapshots
    vms_with_snapshots = random.sample(vms, k=int(len(vms) * 0.4))
    
    snapshots = []
    for vm in vms_with_snapshots:
        # 1-3 Snapshots pro VM
        num_snapshots = random.randint(1, 3)
        
        for j in range(num_snapshots):
            # Snapshots mit unterschiedlichem Alter erstellen
            if j == 0:
                # Älterer Snapshot (30-365 Tage)
                days_old = random.randint(30, 365)
            else:
                # Neuerer Snapshot (1-29 Tage)
                days_old = random.randint(1, 29)
            
            snapshot_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            snapshot_size_gb = random.uniform(0.5, 50.0)
            
            snapshot = {
                'vm_name': vm['name'],
                'name': f"Snapshot-{j+1}" if j > 0 else "Vor Update",
                'description': random.choice([
                    "Vor System-Update", 
                    "Vor Anwendungs-Installation",
                    "Backup vor Konfigurationsänderung",
                    "Testschnappschuss",
                    "Vor Patch-Installation",
                    "Sicherung vor Migration",
                    ""
                ]),
                'creation_time': snapshot_date.strftime("%Y-%m-%d %H:%M:%S"),
                'age_days': days_old,
                'size_gb': snapshot_size_gb,
                'size_bytes': int(snapshot_size_gb * 1024 * 1024 * 1024)
            }
            snapshots.append(snapshot)
    
    # Sortiere nach Alter (älteste zuerst)
    snapshots.sort(key=lambda x: x['age_days'], reverse=True)
    
    return snapshots

def generate_orphaned_vmdks(datastores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generiert Informationen über verwaiste VMDK-Dateien für den Demo-Modus.
    
    Args:
        datastores: Liste der Datastores
        
    Returns:
        Liste von verwaisten VMDK-Daten
    """
    orphaned_vmdks = []
    
    # Für jeden Datastore 0-3 verwaiste VMDKs erstellen
    for datastore in datastores:
        num_orphaned = random.randint(0, 3)
        
        for i in range(num_orphaned):
            # Zufällige Erstellungszeit (30-1000 Tage alt)
            days_old = random.randint(30, 1000)
            creation_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
            
            # Zufällige Größe (1-50 GB)
            size_gb = random.uniform(1.0, 50.0)
            
            # Verschiedene Pfadmuster
            path_pattern = random.choice([
                "{datastore}/orphaned_vm_{id}/orphaned_vm_{id}.vmdk",
                "{datastore}/orphaned_{id}.vmdk",
                "{datastore}/deleted_vms/vm_{id}/vm_{id}.vmdk",
                "{datastore}/old_vm_{id}/old_vm_{id}.vmdk",
                "{datastore}/backup_{id}/backup_{id}.vmdk"
            ])
            
            path = path_pattern.format(datastore=datastore['name'], id=random.randint(100, 999))
            
            vmdk = {
                'path': path,
                'datastore': datastore['name'],
                'size_gb': size_gb,
                'size_bytes': int(size_gb * 1024 * 1024 * 1024),
                'creation_date': creation_date.strftime("%Y-%m-%d %H:%M:%S"),
                'age_days': days_old,
                'thin_provisioned': random.choice([True, False]),
                'verification': random.choice([
                    "Keine zugehörige VM gefunden",
                    "VM gelöscht, VMDK verblieben",
                    "Datei nicht in VM-Konfiguration referenziert",
                    "Verwaiste Snapshot-Datei"
                ])
            }
            orphaned_vmdks.append(vmdk)
    
    # Sortiere nach Größe (größte zuerst)
    orphaned_vmdks.sort(key=lambda x: x['size_bytes'], reverse=True)
    
    return orphaned_vmdks