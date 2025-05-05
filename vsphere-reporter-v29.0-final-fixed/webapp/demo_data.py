#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Demo Data Generator
Copyright (c) 2025 Bechtle GmbH

Dieses Modul generiert Demo-Daten für den vSphere Reporter, wenn kein echter vCenter-Server verfügbar ist.
"""

import datetime
import random
import json
from pathlib import Path

def generate_demo_data():
    """
    Generiert Demo-Daten für den vSphere Reporter.
    
    Returns:
        dict: Ein Dictionary mit den Demo-Daten
    """
    # Basis-Zeitstempel für zufällige Datumsangaben
    now = datetime.datetime.now()
    
    # Generiere virtuelle Maschinen
    vms = _generate_vms(now)
    
    # Generiere ESXi-Hosts
    hosts = _generate_hosts(now)
    
    # Generiere Datastores
    datastores = _generate_datastores()
    
    # Generiere Netzwerke
    networks = _generate_networks()
    
    # Generiere Cluster
    clusters = _generate_clusters(hosts)
    
    # Generiere VMware Tools-Informationen
    vmware_tools = _generate_vmware_tools(vms)
    
    # Generiere Snapshot-Informationen
    snapshots = _generate_snapshots(vms, now)
    
    # Generiere verwaiste VMDK-Informationen
    orphaned_vmdks = _generate_orphaned_vmdks(datastores)
    
    # Erstelle das Ergebnis-Dictionary
    return {
        'vms': vms,
        'hosts': hosts,
        'datastores': datastores,
        'networks': networks,
        'clusters': clusters,
        'vmware_tools': vmware_tools,
        'snapshots': snapshots,
        'orphaned_vmdks': orphaned_vmdks
    }

def _generate_vms(now):
    """
    Generiert virtuelle Maschinen.
    
    Args:
        now: Aktueller Zeitstempel
        
    Returns:
        list: Liste von VM-Informationen
    """
    vm_names = [
        "APP-SERVER-01", "APP-SERVER-02", "APP-SERVER-03",
        "DB-SERVER-01", "DB-SERVER-02",
        "WEB-SERVER-01", "WEB-SERVER-02", "WEB-SERVER-03",
        "DC-SERVER-01", "DC-SERVER-02",
        "TEST-SERVER-01", "TEST-SERVER-02",
        "DEV-SERVER-01", "DEV-SERVER-02", "DEV-SERVER-03",
        "ANALYTICS-01", "ANALYTICS-02",
        "BACKUP-SERVER",
        "MONITORING-SERVER",
        "FILE-SERVER-01", "FILE-SERVER-02"
    ]
    
    guest_os_list = [
        "Windows Server 2022", "Windows Server 2019", "Windows Server 2016",
        "Ubuntu Server 22.04 LTS", "Ubuntu Server 20.04 LTS",
        "Red Hat Enterprise Linux 9", "Red Hat Enterprise Linux 8",
        "SUSE Linux Enterprise Server 15", "SUSE Linux Enterprise Server 12",
        "CentOS Stream 9", "CentOS Stream 8",
        "Debian 11", "Debian 10"
    ]
    
    power_states = ["poweredOn", "poweredOff"]
    power_state_weights = [0.9, 0.1]  # 90% an, 10% aus
    
    vms = []
    for vm_name in vm_names:
        # Zufällige Erstellungszeit zwischen 1 Jahr und 1 Woche in der Vergangenheit
        creation_days_ago = random.randint(7, 365)
        creation_time = now - datetime.timedelta(days=creation_days_ago)
        
        # Wähle Betriebssystem und CPU-/RAM-Ressourcen basierend auf Server-Typ
        if "APP" in vm_name:
            cpus = random.choice([4, 8])
            memory_gb = random.choice([8, 16])
            guest_os = random.choice(guest_os_list)
        elif "DB" in vm_name:
            cpus = random.choice([8, 16])
            memory_gb = random.choice([32, 64])
            guest_os = random.choice(["Windows Server 2022", "Windows Server 2019", "Red Hat Enterprise Linux 9"])
        elif "WEB" in vm_name:
            cpus = random.choice([2, 4])
            memory_gb = random.choice([4, 8])
            guest_os = random.choice(["Ubuntu Server 22.04 LTS", "Ubuntu Server 20.04 LTS", "Debian 11"])
        elif "DC" in vm_name:
            cpus = random.choice([4, 8])
            memory_gb = random.choice([16, 32])
            guest_os = random.choice(["Windows Server 2022", "Windows Server 2019"])
        elif "TEST" in vm_name or "DEV" in vm_name:
            cpus = random.choice([2, 4])
            memory_gb = random.choice([4, 8])
            guest_os = random.choice(guest_os_list)
        else:
            cpus = random.choice([2, 4, 8])
            memory_gb = random.choice([4, 8, 16, 32])
            guest_os = random.choice(guest_os_list)
        
        # Zugewiesener Speicherplatz
        disk_gb = random.choice([40, 80, 120, 250, 500])
        
        # Netzwerkinformationen
        ip_address = f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        # Power-Status
        power_state = random.choices(power_states, weights=power_state_weights)[0]
        
        # Erstelle VM-Eintrag
        vm = {
            'name': vm_name,
            'guest_os': guest_os,
            'power_state': power_state,
            'num_cpu': cpus,
            'memory_gb': memory_gb,
            'disk_gb': disk_gb,
            'ip_address': ip_address,
            'creation_time': creation_time.strftime("%Y-%m-%d %H:%M:%S"),
            'host': f"esxi-host-{random.randint(1, 4):02d}.demo.local",
            'datastore': f"datastore-{random.randint(1, 8):02d}"
        }
        
        vms.append(vm)
    
    return vms

def _generate_hosts(now):
    """
    Generiert ESXi-Hosts.
    
    Args:
        now: Aktueller Zeitstempel
        
    Returns:
        list: Liste von Host-Informationen
    """
    hosts = []
    
    esxi_versions = [
        {"version": "7.0.3", "build": "21930508"},
        {"version": "7.0.2", "build": "18538813"},
        {"version": "7.0.1", "build": "17325551"},
        {"version": "7.0.0", "build": "15843807"},
        {"version": "6.7.0", "build": "17700523"}
    ]
    
    maintenance_modes = [True, False]
    maintenance_mode_weights = [0.05, 0.95]  # 5% im Wartungsmodus
    
    for i in range(1, 5):
        # Hostname
        hostname = f"esxi-host-{i:02d}.demo.local"
        
        # Wähle ESXi-Version
        esxi_version = random.choice(esxi_versions)
        
        # Zufällige Installationszeit zwischen 3 Jahre und 6 Monate in der Vergangenheit
        install_days_ago = random.randint(180, 1095)
        install_time = now - datetime.timedelta(days=install_days_ago)
        
        # Hardware-Informationen
        cpu_model = random.choice([
            "Intel(R) Xeon(R) Gold 6354 CPU @ 3.00GHz",
            "Intel(R) Xeon(R) Platinum 8380 CPU @ 2.30GHz",
            "AMD EPYC 7763 64-Core Processor",
            "AMD EPYC 7542 32-Core Processor"
        ])
        
        cpu_cores = random.choice([24, 32, 48, 64])
        memory_gb = random.choice([128, 256, 384, 512])
        
        # Status
        connection_state = "connected"
        maintenance_mode = random.choices(maintenance_modes, weights=maintenance_mode_weights)[0]
        
        # Erstelle Host-Eintrag
        host = {
            'name': hostname,
            'version': esxi_version['version'],
            'build': esxi_version['build'],
            'install_time': install_time.strftime("%Y-%m-%d"),
            'cpu_model': cpu_model,
            'cpu_cores': cpu_cores,
            'memory_gb': memory_gb,
            'connection_state': connection_state,
            'maintenance_mode': maintenance_mode,
            'vms_count': random.randint(3, 15)
        }
        
        hosts.append(host)
    
    return hosts

def _generate_datastores():
    """
    Generiert Datastores.
    
    Returns:
        list: Liste von Datastore-Informationen
    """
    datastores = []
    
    for i in range(1, 9):
        # Name und Typ
        name = f"datastore-{i:02d}"
        type = random.choice(["VMFS", "NFS"])
        
        # Kapazität und freier Speicherplatz
        capacity_gb = random.choice([500, 1000, 2000, 4000])
        free_percentage = random.uniform(0.05, 0.40)  # 5% bis 40% frei
        free_gb = round(capacity_gb * free_percentage)
        
        # Status
        accessible = random.choices([True, False], weights=[0.98, 0.02])[0]  # 98% zugänglich
        
        # Erstelle Datastore-Eintrag
        datastore = {
            'name': name,
            'type': type,
            'capacity_gb': capacity_gb,
            'free_gb': free_gb,
            'used_gb': capacity_gb - free_gb,
            'accessible': accessible
        }
        
        datastores.append(datastore)
    
    return datastores

def _generate_networks():
    """
    Generiert Netzwerkinformationen.
    
    Returns:
        list: Liste von Netzwerkinformationen
    """
    networks = []
    
    # Standardnetzwerke
    networks.append({
        'name': 'VM Network',
        'type': 'Standard Switch',
        'vlan': 0,
        'used_by_vms': random.randint(10, 20)
    })
    
    networks.append({
        'name': 'Management Network',
        'type': 'Standard Switch',
        'vlan': 0,
        'used_by_vms': random.randint(1, 5)
    })
    
    # Weitere Netzwerke
    for vlan_id in [10, 20, 30, 40, 50]:
        network_name = f"VLAN {vlan_id}"
        network_type = random.choice(["Standard Switch", "Distributed Switch"])
        
        network = {
            'name': network_name,
            'type': network_type,
            'vlan': vlan_id,
            'used_by_vms': random.randint(3, 15)
        }
        
        networks.append(network)
    
    return networks

def _generate_clusters(hosts):
    """
    Generiert Cluster-Informationen.
    
    Args:
        hosts: Liste der Hosts
        
    Returns:
        list: Liste von Cluster-Informationen
    """
    clusters = []
    
    # Erstelle einen Standard-Cluster
    cluster = {
        'name': 'PROD-CLUSTER-01',
        'host_count': len(hosts),
        'hosts': [host['name'] for host in hosts],
        'ha_enabled': True,
        'drs_enabled': True,
        'vsan_enabled': random.choice([True, False]),
        'total_cpu_cores': sum(host['cpu_cores'] for host in hosts),
        'total_memory_gb': sum(host['memory_gb'] for host in hosts)
    }
    
    clusters.append(cluster)
    
    return clusters

def _generate_vmware_tools(vms):
    """
    Generiert VMware Tools-Versionsinformationen.
    
    Args:
        vms: Liste der virtuellen Maschinen
        
    Returns:
        list: Liste von VMware Tools-Informationen
    """
    tools_versions = [
        {'version': '12000', 'status': 'toolsOk'},
        {'version': '11500', 'status': 'toolsOk'},
        {'version': '11000', 'status': 'toolsOk'},
        {'version': '10500', 'status': 'toolsOld'},
        {'version': '10000', 'status': 'toolsOld'},
        {'version': '9500', 'status': 'toolsOld'},
        {'version': 'not installed', 'status': 'toolsNotInstalled'}
    ]
    
    version_weights = [0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1]  # Gewichtungen für die Versionen
    
    vmware_tools = []
    
    for vm in vms:
        # Wähle VMware Tools-Version basierend auf Gewichtung
        tools_info = random.choices(tools_versions, weights=version_weights)[0]
        
        tools_entry = {
            'vm_name': vm['name'],
            'guest_os': vm['guest_os'],
            'tools_version': tools_info['version'],
            'tools_status': tools_info['status'],
            'upgrade_available': tools_info['status'] == 'toolsOld'
        }
        
        vmware_tools.append(tools_entry)
    
    # Sortiere nach Version (älteste zuerst)
    vmware_tools.sort(key=lambda x: x['tools_version'] if x['tools_version'] != 'not installed' else '0')
    
    return vmware_tools

def _generate_snapshots(vms, now):
    """
    Generiert Snapshot-Informationen.
    
    Args:
        vms: Liste der virtuellen Maschinen
        now: Aktueller Zeitstempel
        
    Returns:
        list: Liste von Snapshot-Informationen
    """
    snapshots = []
    
    # Typen von Snapshots mit typischen Beschreibungen
    snapshot_types = [
        {'purpose': 'Backup', 'descriptions': ['Pre-backup snapshot', 'Backup']},
        {'purpose': 'Update', 'descriptions': ['Pre-Windows-Update', 'Pre-Update', 'Before-Update']},
        {'purpose': 'Patch', 'descriptions': ['Pre-Patch', 'Before-Patch', 'Security-Patch']},
        {'purpose': 'Test', 'descriptions': ['Test', 'Testing', 'Testing-Only']},
        {'purpose': 'Migration', 'descriptions': ['Pre-Migration', 'Before-Migration']},
        {'purpose': 'Maintenance', 'descriptions': ['Maintenance', 'System-Maintenance']}
    ]
    
    # Nicht alle VMs haben Snapshots
    vms_with_snapshots = random.sample(vms, k=int(len(vms) * 0.6))  # 60% der VMs haben Snapshots
    
    for vm in vms_with_snapshots:
        # Anzahl der Snapshots pro VM
        num_snapshots = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        
        for i in range(num_snapshots):
            # Wähle Snapshot-Typ
            snapshot_type = random.choice(snapshot_types)
            description = random.choice(snapshot_type['descriptions'])
            
            # Erzeugungsdatum (zwischen 1 Tag und 1 Jahr)
            days_ago = random.randint(1, 365)
            create_time = now - datetime.timedelta(days=days_ago)
            
            # Snapshot-Größe
            size_gb = round(random.uniform(0.5, 25.0), 2)
            
            snapshot = {
                'vm_name': vm['name'],
                'name': f"Snapshot {i+1}",
                'description': description,
                'create_time': create_time.strftime("%Y-%m-%d %H:%M:%S"),
                'days_old': days_ago,
                'size_gb': size_gb
            }
            
            snapshots.append(snapshot)
    
    # Sortiere nach Alter (älteste zuerst)
    snapshots.sort(key=lambda x: x['days_old'], reverse=True)
    
    return snapshots

def _generate_orphaned_vmdks(datastores):
    """
    Generiert Informationen über verwaiste VMDK-Dateien.
    
    Args:
        datastores: Liste der Datastores
        
    Returns:
        list: Liste von VMDK-Informationen
    """
    orphaned_vmdks = []
    standard_vmdks = []
    
    # Basis-Namen für VMDKs
    vmdk_base_names = [
        "app_server", "db_server", "web_server", "testvm", 
        "devvm", "fileserver", "exchange", "sql", "oracle", 
        "backup", "archive", "template"
    ]
    
    # Erstelle einige normale (nicht verwaiste) VMDKs
    for i in range(40):
        base_name = random.choice(vmdk_base_names)
        vmdk_name = f"{base_name}_{random.randint(1, 99):02d}.vmdk"
        datastore = random.choice(datastores)
        
        vmdk = {
            'name': vmdk_name,
            'datastore': datastore['name'],
            'path': f"[{datastore['name']}] {base_name.upper()}/{vmdk_name}",
            'size_gb': round(random.uniform(10, 100), 2),
            'status': 'Normal',
            'is_orphaned': False
        }
        
        standard_vmdks.append(vmdk)
    
    # Erstelle einige verwaiste VMDKs
    for i in range(5):
        base_name = random.choice(vmdk_base_names)
        vmdk_name = f"{base_name}_old_{random.randint(1, 99):02d}.vmdk"
        datastore = random.choice(datastores)
        
        vmdk = {
            'name': vmdk_name,
            'datastore': datastore['name'],
            'path': f"[{datastore['name']}] {base_name.upper()}_ARCHIVE/{vmdk_name}",
            'size_gb': round(random.uniform(10, 100), 2),
            'status': 'POTENTIALLY ORPHANED',
            'is_orphaned': True,
            'description': 'VMDK existiert ohne zugehörige VM-Konfigurationsdatei'
        }
        
        orphaned_vmdks.append(vmdk)
    
    # Weitere potentiell verwaiste VMDKs (gelöschte VMs)
    for i in range(3):
        base_name = random.choice(vmdk_base_names)
        vmdk_name = f"DELETED_{base_name}_{random.randint(1, 99):02d}.vmdk"
        datastore = random.choice(datastores)
        
        vmdk = {
            'name': vmdk_name,
            'datastore': datastore['name'],
            'path': f"[{datastore['name']}] DELETED/{vmdk_name}",
            'size_gb': round(random.uniform(10, 100), 2),
            'status': 'POTENTIALLY ORPHANED',
            'is_orphaned': True,
            'description': 'VMDK in Verzeichnis für gelöschte VMs'
        }
        
        orphaned_vmdks.append(vmdk)
    
    # Temporäre Snapshot-VMDKs
    for i in range(3):
        base_name = random.choice(vmdk_base_names)
        vmdk_name = f"{base_name}_{random.randint(1, 99):02d}-000001.vmdk"
        datastore = random.choice(datastores)
        
        vmdk = {
            'name': vmdk_name,
            'datastore': datastore['name'],
            'path': f"[{datastore['name']}] {base_name.upper()}/{vmdk_name}",
            'size_gb': round(random.uniform(5, 20), 2),
            'status': 'POTENTIALLY ORPHANED',
            'is_orphaned': True,
            'description': 'Möglicherweise temporäre Snapshot-VMDK'
        }
        
        orphaned_vmdks.append(vmdk)
    
    # Kombiniere und gib alle VMDKs zurück
    all_vmdks = standard_vmdks + orphaned_vmdks
    
    return all_vmdks