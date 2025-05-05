#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Demo-Daten-Generator für den Offline-/Demo-Modus

Copyright (c) 2025 Bechtle GmbH
"""

import datetime
import random
import humanize
import uuid

def generate_demo_data():
    """
    Generiert Beispieldaten für den Demo-Modus, sodass die Anwendung
    ohne tatsächliche vCenter-Verbindung getestet werden kann
    
    Returns:
        dict: Dictionary mit Beispieldaten für alle Reportbereiche
    """
    current_time = datetime.datetime.now()
    
    # Generiere 20 VMs mit zufälligen Namen
    vms = []
    for i in range(1, 21):
        vm_name = f"demo-vm-{i:02d}"
        vm_type = random.choice(["Windows Server", "Linux", "Windows Client", "FreeBSD"])
        
        if "Windows" in vm_type:
            os_name = random.choice([
                "Microsoft Windows Server 2022", 
                "Microsoft Windows Server 2019", 
                "Microsoft Windows Server 2016", 
                "Microsoft Windows 10"
            ])
        elif vm_type == "Linux":
            os_name = random.choice([
                "Red Hat Enterprise Linux 9", 
                "SUSE Linux Enterprise Server 15", 
                "Ubuntu Server 22.04 LTS", 
                "Debian GNU/Linux 11"
            ])
        else:
            os_name = "FreeBSD 13.2"
        
        # VMware Tools Version und Status
        tools_status = random.choice(["toolsOk", "toolsOld", "toolsNotRunning", "toolsNotInstalled"])
        if tools_status == "toolsOk":
            tools_version = "12000"
            tools_version_status = "Current"
        elif tools_status == "toolsOld":
            tools_version = random.choice(["10000", "9000", "8000"])
            tools_version_status = f"Outdated ({random.randint(300, 800)} days old)"
        else:
            tools_version = "Unknown"
            tools_version_status = "Not available"
        
        # Zufällige Hardware-Konfiguration
        cpu_count = random.choice([1, 2, 4, 8, 16])
        memory_mb = random.choice([1024, 2048, 4096, 8192, 16384, 32768])
        disk_gb = random.choice([40, 80, 120, 250, 500, 1000])
        
        # Power-Status
        power_state = random.choice(["poweredOn", "poweredOff"])
        
        # Hostinformationen
        host_name = f"demo-esx-{random.randint(1,4):02d}.lab.local"
        
        # Zufällige IP-Adressen
        ip_addresses = [f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"]
        
        vms.append({
            "name": vm_name,
            "moref": f"vm-{random.randint(1000, 9999)}",
            "uuid": str(uuid.uuid4()),
            "power_state": power_state,
            "os_name": os_name,
            "os_type": vm_type,
            "cpu_count": cpu_count,
            "memory_mb": memory_mb,
            "disk_gb": disk_gb,
            "tools_status": tools_status,
            "tools_version": tools_version,
            "tools_version_status": tools_version_status,
            "host": host_name,
            "ip_addresses": ip_addresses,
            "creation_date": (current_time - datetime.timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d"),
        })
    
    # Generiere ESXi-Hosts
    hosts = []
    for i in range(1, 5):
        host_name = f"demo-esx-{i:02d}.lab.local"
        cpu_model = random.choice(["Intel(R) Xeon(R) Gold 6348 CPU @ 2.60GHz", "AMD EPYC 7543 32-Core Processor"])
        cpu_count = random.choice([24, 32, 48, 64])
        memory_gb = random.choice([128, 256, 384, 512])
        
        hosts.append({
            "name": host_name,
            "moref": f"host-{random.randint(1000, 9999)}",
            "model": f"PowerEdge R{random.choice(['740', '840', '940'])}",
            "vendor": "Dell Inc.",
            "cpu_model": cpu_model,
            "cpu_cores": cpu_count,
            "memory_gb": memory_gb,
            "version": f"7.0.{random.randint(1, 3)}",
            "build": f"{random.randint(10000, 20000)}",
            "status": "Connected",
            "in_maintenance_mode": False,
            "vms_count": random.randint(4, 15)
        })
    
    # Generiere Datastores
    datastores = []
    for i in range(1, 6):
        datastore_name = f"demo-ds-{i:02d}"
        capacity_gb = random.choice([1000, 2000, 4000, 8000, 16000])
        free_percent = random.randint(10, 90)
        free_gb = int(capacity_gb * free_percent / 100)
        
        datastores.append({
            "name": datastore_name,
            "moref": f"datastore-{random.randint(1000, 9999)}",
            "type": random.choice(["VMFS", "NFS"]),
            "capacity_gb": capacity_gb,
            "free_gb": free_gb,
            "free_percent": free_percent,
            "status": "Available"
        })
    
    # Generiere Netzwerke
    networks = []
    for i in range(1, 4):
        network_name = f"VM Network {i}"
        
        networks.append({
            "name": network_name,
            "moref": f"network-{random.randint(1000, 9999)}",
            "type": random.choice(["Standard Switch", "Distributed Switch"]),
            "vlan": random.randint(1, 1000) if random.random() > 0.3 else None,
            "connected_vms": random.randint(1, 15)
        })
    
    # Generiere Snapshots (ca. 30% der VMs haben Snapshots)
    snapshots = []
    snapshot_vms = random.sample(vms, int(len(vms) * 0.3))
    
    for vm in snapshot_vms:
        # Jede VM mit Snapshots hat 1-3 Snapshots
        for j in range(random.randint(1, 3)):
            # Snapshot-Alter zwischen 1 und 365 Tagen
            snapshot_age = random.randint(1, 365)
            snapshot_date = current_time - datetime.timedelta(days=snapshot_age)
            
            # Snapshot-Größe zwischen 1 und 30 GB
            snapshot_size_gb = random.randint(1, 30)
            
            snapshots.append({
                "vm_name": vm["name"],
                "vm_moref": vm["moref"],
                "name": f"Snapshot {j+1} of {vm['name']}",
                "description": random.choice([
                    "Pre-update snapshot", 
                    "Before configuration change", 
                    "Testing purpose", 
                    "Backup"
                ]),
                "creation_date": snapshot_date.strftime("%Y-%m-%d %H:%M:%S"),
                "age_days": snapshot_age,
                "age_human": humanize.naturaltime(datetime.timedelta(days=snapshot_age)),
                "size_gb": snapshot_size_gb,
                "id": str(uuid.uuid4())
            })
    
    # Nach Alter sortieren (älteste zuerst)
    snapshots.sort(key=lambda x: x["age_days"], reverse=True)
    
    # Generiere VMware Tools-Informationen
    vmware_tools = []
    for vm in vms:
        if vm["tools_status"] != "toolsOk":
            vmware_tools.append({
                "vm_name": vm["name"],
                "vm_moref": vm["moref"],
                "status": vm["tools_status"],
                "version": vm["tools_version"],
                "version_status": vm["tools_version_status"]
            })
    
    # Generiere verwaiste VMDKs
    orphaned_vmdks = []
    for i in range(1, 8):
        datastore = random.choice(datastores)
        
        # Verwaiste VMDK-Größe zwischen 1 und 100 GB
        vmdk_size_gb = random.randint(1, 100)
        
        # Alter zwischen 30 und 500 Tagen
        vmdk_age = random.randint(30, 500)
        vmdk_date = current_time - datetime.timedelta(days=vmdk_age)
        
        orphaned_vmdks.append({
            "datastore": datastore["name"],
            "datastore_moref": datastore["moref"],
            "path": f"[{datastore['name']}] orphaned_vm_{i}/orphaned_vm_{i}.vmdk",
            "name": f"orphaned_vm_{i}.vmdk",
            "size_gb": vmdk_size_gb,
            "creation_date": vmdk_date.strftime("%Y-%m-%d"),
            "age_days": vmdk_age,
            "status": "POTENTIALLY ORPHANED",
            "description": "Diese VMDK-Datei ist nicht mit einer aktiven VM verbunden."
        })
    
    # Nach Alter sortieren (älteste zuerst)
    vmware_tools.sort(key=lambda x: x["version_status"], reverse=True)
    
    return {
        "vms": vms,
        "hosts": hosts,
        "datastores": datastores,
        "networks": networks,
        "snapshots": snapshots,
        "vmware_tools": vmware_tools,
        "orphaned_vmdks": orphaned_vmdks
    }