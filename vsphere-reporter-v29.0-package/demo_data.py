#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Web Edition
Copyright (c) 2025 Bechtle GmbH

Modul zur Generierung von Demo-Daten für den vSphere Reporter.
Erzeugt realistische Beispieldaten für die Verwendung im Demo-Modus.
"""

import random
import datetime
from typing import Dict, List, Any, Optional

# Konstanten für die Demo-Daten
VM_NAMES = [
    "web-server-01", "web-server-02", "app-server-01", "app-server-02",
    "db-server-01", "db-server-02", "file-server-01", "file-server-02",
    "mail-server-01", "mail-server-02", "backup-server-01", "backup-server-02",
    "dc-server-01", "dc-server-02", "gateway-01", "gateway-02",
    "monitoring-01", "monitoring-02", "erp-server-01", "erp-server-02",
    "test-vm-01", "test-vm-02", "dev-vm-01", "dev-vm-02", "prod-vm-01", "prod-vm-02"
]

HOST_NAMES = [
    "esx01.example.com", "esx02.example.com", "esx03.example.com", "esx04.example.com",
    "esx05.example.com", "esx06.example.com", "esx07.example.com", "esx08.example.com",
]

DATASTORE_NAMES = [
    "datastore-ssd-01", "datastore-ssd-02", "datastore-hdd-01", "datastore-hdd-02",
    "datastore-nas-01", "datastore-nas-02", "datastore-backup-01", "datastore-backup-02",
]

DATASTORE_TYPES = ["VMFS", "NFS", "vSAN", "vVOL"]

NETWORK_NAMES = [
    "VM Network", "Management Network", "Backup Network", "DMZ Network",
    "Internal Network", "Production Network", "Test Network", "Development Network"
]

NETWORK_TYPES = ["VDS", "VSS", "NSX"]

GUEST_FULL_NAMES = [
    "Microsoft Windows Server 2022", "Microsoft Windows Server 2019", "Microsoft Windows Server 2016",
    "Microsoft Windows 11 (64-bit)", "Microsoft Windows 10 (64-bit)",
    "Red Hat Enterprise Linux 9 (64-bit)", "Red Hat Enterprise Linux 8 (64-bit)",
    "Ubuntu Linux (64-bit)", "Debian GNU/Linux (64-bit)", "SUSE Linux Enterprise Server 15",
    "CentOS Linux 9 (64-bit)", "Oracle Linux 9 (64-bit)", "Other Linux (64-bit)"
]

VMWARE_TOOLS_STATUSES = ["toolsOk", "toolsOld", "toolsNotRunning", "toolsNotInstalled"]
VMWARE_TOOLS_VERSION_STATUSES = ["current", "outOfDate", "notInstalled"]
POWER_STATES = ["poweredOn", "poweredOff"]
CONNECTION_STATES = ["connected", "disconnected"]

VMDK_FILE_TYPES = ["-flat.vmdk", "-000001.vmdk", "-ctk.vmdk", "-delta.vmdk"]

SNAPSHOT_NAMES = [
    "Pre-Update", "Post-Update", "Clean State", "Testing", "Backup",
    "Before Changes", "After Changes", "Restore Point", "Migration Point",
    "Configuration Change", "OS Patch", "Software Installation", "Security Update",
    "Troubleshooting", "Maintenance"
]

SNAPSHOT_DESCRIPTIONS = [
    "Snapshot vor dem Windows Update", "Snapshot nach dem Windows Update",
    "Snapshot vor der Installation von Software", "Snapshot nach der Installation von Software",
    "Snapshot vor der Konfigurationsänderung", "Snapshot nach der Konfigurationsänderung",
    "Snapshot für Backup-Zwecke", "Snapshot für Wiederherstellungspunkt",
    "Snapshot vor der Migration", "Snapshot für Testumgebung",
    "Snapshot vor der Datenbankmigration", "Snapshot nach der Datenbankmigration",
    "Saubere Installation", "", "Arbeitsstand gesichert", "Tägliches Backup",
    "Wöchentliches Backup", "Monatliches Backup", "Quartalssicherung"
]

# Hilfsfunktionen für die Generierung von zufälligen Datums- und Zeitwerten
def random_date(start: datetime.datetime, end: datetime.datetime) -> datetime.datetime:
    """
    Generiert ein zufälliges Datum zwischen start und end.
    
    Args:
        start: Startdatum
        end: Enddatum
        
    Returns:
        Ein zufälliges Datum zwischen start und end
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

def now() -> datetime.datetime:
    """
    Gibt das aktuelle Datum und die aktuelle Zeit zurück.
    
    Returns:
        Aktuelles Datum und aktuelle Zeit
    """
    return datetime.datetime.now()

def days_ago(days: int) -> datetime.datetime:
    """
    Berechnet ein Datum, das eine bestimmte Anzahl von Tagen in der Vergangenheit liegt.
    
    Args:
        days: Anzahl der Tage
        
    Returns:
        Datum vor der angegebenen Anzahl von Tagen
    """
    return now() - datetime.timedelta(days=days)

# Funktionen zur Generierung von Demo-Daten
def get_demo_vms(count: int = 20) -> List[Dict[str, Any]]:
    """
    Generiert Demo-Daten für virtuelle Maschinen.
    
    Args:
        count: Anzahl der zu generierenden VMs
        
    Returns:
        Eine Liste von VM-Dictionaries
    """
    vms = []
    for i in range(min(count, len(VM_NAMES))):
        vm_name = VM_NAMES[i]
        ip_address = f"192.168.1.{10 + i}" if random.random() > 0.2 else None
        
        vm = {
            "name": vm_name,
            "guest_full_name": random.choice(GUEST_FULL_NAMES),
            "power_state": random.choices(POWER_STATES, weights=[0.8, 0.2])[0],
            "cpu_count": random.choice([1, 2, 4, 8, 16]),
            "memory_mb": random.choice([1024, 2048, 4096, 8192, 16384, 32768]),
            "ip_address": ip_address,
            "tools_status": random.choices(VMWARE_TOOLS_STATUSES, weights=[0.6, 0.2, 0.1, 0.1])[0],
            "version_status": random.choices(VMWARE_TOOLS_VERSION_STATUSES, weights=[0.7, 0.2, 0.1])[0],
            "version": f"12.0.0 build-1922552" if random.random() > 0.1 else None,
            "datastores": random.sample(DATASTORE_NAMES, random.randint(1, 3)),
            "host": random.choice(HOST_NAMES),
            "networks": random.sample(NETWORK_NAMES, random.randint(1, 3)),
            "created": random_date(days_ago(365*2), days_ago(30)).isoformat(),
            "last_boot": random_date(days_ago(90), days_ago(1)).isoformat() if random.random() > 0.2 else None,
        }
        vms.append(vm)
    
    return vms

def get_demo_hosts(count: int = 8) -> List[Dict[str, Any]]:
    """
    Generiert Demo-Daten für ESXi-Hosts.
    
    Args:
        count: Anzahl der zu generierenden Hosts
        
    Returns:
        Eine Liste von Host-Dictionaries
    """
    hosts = []
    for i in range(min(count, len(HOST_NAMES))):
        host_name = HOST_NAMES[i]
        
        host = {
            "name": host_name,
            "connection_state": random.choices(CONNECTION_STATES, weights=[0.95, 0.05])[0],
            "maintenance_mode": random.random() < 0.1,  # 10% Wahrscheinlichkeit für Wartungsmodus
            "version": f"VMware ESXi {random.choice(['7.0.3', '7.0.2', '7.0.1', '7.0.0', '6.7.0', '6.5.0'])}-{random.randint(10000, 99999)}",
            "cpu_cores": random.choice([16, 24, 32, 64]),
            "memory_size": random.choice([137438953472, 274877906944, 549755813888, 1099511627776]),  # 128, 256, 512, 1024 GB
            "datastores": random.sample(DATASTORE_NAMES, random.randint(2, len(DATASTORE_NAMES))),
            "networks": random.sample(NETWORK_NAMES, random.randint(2, len(NETWORK_NAMES))),
            "vm_count": random.randint(5, 20),
        }
        hosts.append(host)
    
    return hosts

def get_demo_datastores(count: int = 8) -> List[Dict[str, Any]]:
    """
    Generiert Demo-Daten für Datastores.
    
    Args:
        count: Anzahl der zu generierenden Datastores
        
    Returns:
        Eine Liste von Datastore-Dictionaries
    """
    datastores = []
    for i in range(min(count, len(DATASTORE_NAMES))):
        datastore_name = DATASTORE_NAMES[i]
        
        # Zufällige Kapazität je nach Typ (SSD größer als HDD)
        if "ssd" in datastore_name.lower():
            capacity = random.randint(5, 20) * 1099511627776  # 5-20 TB
        else:
            capacity = random.randint(1, 5) * 1099511627776  # 1-5 TB
        
        # Zufällige Belegung (50-90%)
        free_space_ratio = random.uniform(0.1, 0.5)
        free_space = int(capacity * free_space_ratio)
        
        datastore = {
            "name": datastore_name,
            "type": random.choice(DATASTORE_TYPES),
            "capacity": capacity,
            "free_space": free_space,
            "hosts": random.sample(HOST_NAMES, random.randint(2, len(HOST_NAMES))),
            "vm_count": random.randint(5, 15),
        }
        datastores.append(datastore)
    
    return datastores

def get_demo_networks(count: int = 8) -> List[Dict[str, Any]]:
    """
    Generiert Demo-Daten für Netzwerke.
    
    Args:
        count: Anzahl der zu generierenden Netzwerke
        
    Returns:
        Eine Liste von Netzwerk-Dictionaries
    """
    networks = []
    for i in range(min(count, len(NETWORK_NAMES))):
        network_name = NETWORK_NAMES[i]
        
        # VLAN-ID, abhängig vom Netzwerktyp
        vlan_id = None
        if random.random() > 0.2:  # 80% Wahrscheinlichkeit für ein VLAN
            vlan_id = random.randint(1, 4094)
        
        network = {
            "name": network_name,
            "type": random.choice(NETWORK_TYPES),
            "vlan_id": vlan_id,
            "hosts": random.sample(HOST_NAMES, random.randint(2, len(HOST_NAMES))),
            "vm_count": random.randint(3, 12),
        }
        networks.append(network)
    
    return networks

def get_demo_vmware_tools(count: int = 20) -> List[Dict[str, Any]]:
    """
    Generiert Demo-Daten für VMware Tools Status.
    
    Args:
        count: Anzahl der zu generierenden VMs
        
    Returns:
        Eine Liste von VMware Tools Status-Dictionaries
    """
    # Generiere virtuelle Maschinen als Basis
    vms = get_demo_vms(count)
    
    # Gewichte für die Status-Verteilung
    tools_weights = {
        "toolsOk": 0.6,
        "toolsOld": 0.2,
        "toolsNotRunning": 0.1,
        "toolsNotInstalled": 0.1
    }
    
    version_weights = {
        "current": 0.7,
        "outOfDate": 0.2,
        "notInstalled": 0.1
    }
    
    # Aktualisiere die VMware Tools-Status nach den Gewichten
    for vm in vms:
        vm["tools_status"] = random.choices(
            list(tools_weights.keys()),
            weights=list(tools_weights.values())
        )[0]
        
        vm["version_status"] = random.choices(
            list(version_weights.keys()),
            weights=list(version_weights.values())
        )[0]
        
        # Version basierend auf Status
        if vm["version_status"] == "current":
            vm["version"] = "12.0.0 build-1922552"
        elif vm["version_status"] == "outOfDate":
            vm["version"] = random.choice(["11.3.5 build-1823152", "11.0.1 build-1743428", "10.3.25 build-1679270"])
        else:
            vm["version"] = None
    
    return vms

def get_demo_snapshots(count: int = 15) -> List[Dict[str, Any]]:
    """
    Generiert Demo-Daten für Snapshots.
    
    Args:
        count: Anzahl der zu generierenden Snapshots
        
    Returns:
        Eine Liste von Snapshot-Dictionaries
    """
    snapshots = []
    
    # Wir wollen eine Mischung aus aktuellen, alten und sehr alten Snapshots
    age_distribution = [
        # (min_days, max_days, weight)
        (1, 7, 0.3),      # aktuelle Snapshots (1-7 Tage)
        (8, 30, 0.4),     # mittelalte Snapshots (8-30 Tage)
        (31, 90, 0.2),    # alte Snapshots (31-90 Tage)
        (91, 365, 0.1)    # sehr alte Snapshots (91-365 Tage)
    ]
    
    # Snapshots dynamisch auf VMs verteilen
    vms = get_demo_vms(count)
    
    for i in range(count):
        # Wähle zufällig eine VM aus
        vm = random.choice(vms)
        
        # Bestimme das Alter des Snapshots basierend auf der Verteilung
        age_choice = random.choices(
            age_distribution,
            weights=[weight for _, _, weight in age_distribution]
        )[0]
        
        min_days, max_days, _ = age_choice
        create_time = random_date(days_ago(max_days), days_ago(min_days))
        
        # Berechne zufällige Größe (50MB - 50GB)
        size_bytes = random.randint(50 * 1024 * 1024, 50 * 1024 * 1024 * 1024)
        
        snapshot = {
            "name": random.choice(SNAPSHOT_NAMES),
            "vm_name": vm["name"],
            "create_time": create_time,
            "size_bytes": size_bytes,
            "description": random.choice(SNAPSHOT_DESCRIPTIONS),
            "state": vm["power_state"],
            "quiesced": random.random() < 0.3,  # 30% Wahrscheinlichkeit für "quiesced"
        }
        snapshots.append(snapshot)
    
    # Sortiere Snapshots nach Alter (älteste zuerst)
    snapshots.sort(key=lambda x: x["create_time"])
    
    return snapshots

def get_demo_orphaned_vmdks(count: int = 12) -> List[Dict[str, Any]]:
    """
    Generiert Demo-Daten für verwaiste VMDKs.
    
    Args:
        count: Anzahl der zu generierenden verwaisten VMDKs
        
    Returns:
        Eine Liste von verwaisten VMDK-Dictionaries
    """
    orphaned_vmdks = []
    
    # Wir wollen eine Mischung aus verschiedenen VMDK-Typen und Erklärungen
    explanations = [
        "VMDK ist keiner VM zugeordnet",
        "Verwaiste Snapshot-VMDK nach fehlgeschlagenem Snapshot-Löschvorgang",
        "Festplattendatei ohne zugehörige VM-Konfiguration gefunden",
        "Temporäre VMDK von abgebrochener Storage vMotion",
        "Mögliches Überbleibsel nach unvollständiger VM-Löschung",
        "VMDK ohne Zuordnung in der VM-Konfiguration"
    ]
    
    # Verteile verwaiste VMDKs auf verschiedene Datastores
    for i in range(count):
        datastore = random.choice(DATASTORE_NAMES)
        
        # Generiere zufälligen Dateinamen basierend auf VM-Namen
        vm_name = random.choice(VM_NAMES)
        file_type = random.choice(VMDK_FILE_TYPES)
        name = f"{vm_name}{file_type}"
        
        # Zufälliger Pfad im Datastore
        path = f"[{datastore}] vm_folder_{random.randint(1, 10)}/{vm_name}/{name}"
        
        # Berechne zufällige Größe (1GB - 500GB)
        size_bytes = random.randint(1 * 1024 * 1024 * 1024, 500 * 1024 * 1024 * 1024)
        
        # Modifikationsdatum (bis zu 2 Jahre alt)
        modification_time = random_date(days_ago(365*2), days_ago(1))
        
        orphaned_vmdk = {
            "name": name,
            "datastore": datastore,
            "path": path,
            "size_bytes": size_bytes,
            "modification_time": modification_time,
            "explanation": random.choice(explanations)
        }
        orphaned_vmdks.append(orphaned_vmdk)
    
    return orphaned_vmdks

# Hauptfunktion, die alle Demo-Daten generiert
def generate_all_demo_data() -> Dict[str, Any]:
    """
    Generiert alle Demo-Daten für den vSphere Reporter.
    
    Returns:
        Ein Dictionary mit allen Demo-Daten
    """
    return {
        "vms": get_demo_vms(),
        "hosts": get_demo_hosts(),
        "datastores": get_demo_datastores(),
        "networks": get_demo_networks(),
        "vmware_tools": get_demo_vmware_tools(),
        "snapshots": get_demo_snapshots(),
        "orphaned_vmdks": get_demo_orphaned_vmdks(),
        "now": now(),
        "demo_mode": True
    }