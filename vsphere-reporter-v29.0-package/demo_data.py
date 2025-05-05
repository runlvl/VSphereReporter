#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter v29.0 - Demo-Daten

Dieses Modul stellt Funktionen für die Generierung von Demo-Daten bereit,
damit die Anwendung auch ohne Verbindung zu einem vCenter getestet werden kann.

Copyright (c) 2025 Bechtle GmbH
"""

import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Globale Konstanten für die Demo-Daten
VM_NAMES = [
    "vm-prod-db01", "vm-prod-db02", "vm-prod-app01", "vm-prod-app02", "vm-prod-app03",
    "vm-prod-web01", "vm-prod-web02", "vm-prod-web03", "vm-prod-web04", "vm-dev-db01",
    "vm-dev-app01", "vm-dev-app02", "vm-dev-web01", "vm-test-db01", "vm-test-app01",
    "vm-test-web01", "vm-mgmt-dc01", "vm-mgmt-dc02", "vm-mgmt-mail01", "vm-mgmt-mail02",
    "vm-mgmt-mon01", "vm-mgmt-mon02", "vm-mgmt-backup01", "vm-mgmt-backup02", "vm-mgmt-admin",
    "vm-prod-erp01", "vm-prod-erp02", "vm-prod-erp-db01", "vm-prod-crm01", "vm-prod-crm02",
    "vm-prod-crm-db01", "vm-prod-file01", "vm-prod-file02", "vm-prod-print01", "vm-prod-print02"
]

ESXI_HOSTS = [
    "esxi-host01.bechtle.local", "esxi-host02.bechtle.local", "esxi-host03.bechtle.local",
    "esxi-host04.bechtle.local", "esxi-host05.bechtle.local", "esxi-host06.bechtle.local"
]

OPERATING_SYSTEMS = [
    "Microsoft Windows Server 2019 (64-bit)",
    "Microsoft Windows Server 2016 (64-bit)",
    "Microsoft Windows Server 2012 R2 (64-bit)",
    "Microsoft Windows 10 (64-bit)",
    "Red Hat Enterprise Linux 8 (64-bit)",
    "Red Hat Enterprise Linux 7 (64-bit)",
    "SUSE Linux Enterprise Server 15 (64-bit)",
    "SUSE Linux Enterprise Server 12 (64-bit)",
    "Ubuntu Linux (64-bit)",
    "CentOS 8 (64-bit)",
    "CentOS 7 (64-bit)",
    "Debian GNU/Linux 10 (64-bit)",
    "Debian GNU/Linux 9 (64-bit)",
    "Oracle Linux 8 (64-bit)",
    "Oracle Linux 7 (64-bit)",
    "VMware Photon OS (64-bit)"
]

DATASTORES = [
    "ds-ssd-01", "ds-ssd-02", "ds-ssd-03", "ds-sas-01", "ds-sas-02", 
    "ds-sas-03", "ds-sata-01", "ds-sata-02", "ds-archive-01"
]

SNAPSHOT_NAMES = [
    "Vor Update", "Nach Update", "Vor Konfigurationsänderung", "Nach Konfigurationsänderung",
    "Vor Patch", "Nach Patch", "Sicherung vor Migration", "Testumgebung", "Vor Softwareinstallation",
    "Vor Systemupdate", "Nach Systemupdate", "Backup", "Vor Datenbankupgrade",
    "Nach Datenbankupgrade", "Notfallsicherung", "Für Test", "Produktionssicherung", "Schneller Rollback"
]

SNAPSHOT_DESCRIPTIONS = [
    "Erstellt vor dem monatlichen Windows-Update",
    "Erstellt nach erfolgreichen Updates",
    "Sicherung vor kritischen Änderungen an der System-Konfiguration",
    "Snapshot für Rollback-Optionen",
    "Sicherung vor Installation neuer Software",
    "VM-Zustand vor Datenmigration",
    "Langzeitsicherung für Notfallwiederherstellung",
    "Temporäre Sicherung für Tests",
    "Snapshot vor der Anwendungsaktualisierung",
    "Sicherung zur Fehlerbehebung",
    "Snapshot für Leistungstests",
    "VM-Zustand vor Infrastrukturänderungen",
    "Sicherung gemäß Änderungsmanagement",
    "Snapshot für Security-Audit",
    ""  # Leere Beschreibung, kommt auch vor
]

def generate_vmware_tools_data(count=30):
    """
    Generiert realistische Demo-Daten für VMware Tools Status.
    
    Args:
        count (int): Anzahl der zu generierenden VM-Einträge
        
    Returns:
        list: Liste von Dictionaries mit VMware Tools-Informationen
    """
    logger.info(f"Generiere Demo-Daten für VMware Tools ({count} VMs)")
    result = []
    
    # Mögliche Status mit Wahrscheinlichkeiten
    tool_statuses = ['Current', 'UpdateNeeded', 'NotInstalled', 'NotRunning', 'Unmanaged']
    status_weights = [0.7, 0.15, 0.05, 0.05, 0.05]  # Wahrscheinlichkeiten
    
    # VMware Tools-Versionen (neuere Version = höhere Zahlen)
    current_version = 12000
    old_versions = [11365, 11350, 11340, 11305, 11274, 11270, 11263, 11250, 10345, 10338, 10300, 10289, 10275, 10249]
    
    # VM-Namen zufällig auswählen (ohne Wiederholung)
    selected_vms = random.sample(VM_NAMES, min(count, len(VM_NAMES)))
    
    # Falls mehr VMs benötigt werden als in der Liste, füge generierte Namen hinzu
    if count > len(VM_NAMES):
        for i in range(count - len(VM_NAMES)):
            selected_vms.append(f"vm-auto-{i+1:02d}")
    
    # VMs erstellen
    for vm_name in selected_vms:
        # Zufällige Werte auswählen
        esxi_host = random.choice(ESXI_HOSTS)
        os_type = random.choice(OPERATING_SYSTEMS)
        tools_status = random.choices(tool_statuses, weights=status_weights, k=1)[0]
        
        # Boot-Datum generieren (zufällig zwischen heute und vor 90 Tagen)
        days_ago = random.randint(0, 90)
        boot_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Tools-Version basierend auf Status zuweisen
        tools_version = "Not installed"
        if tools_status == 'Current':
            tools_version = str(current_version)
        elif tools_status == 'UpdateNeeded':
            tools_version = str(random.choice(old_versions))
        elif tools_status == 'NotRunning':
            tools_version = str(random.choice([current_version] + old_versions))
        elif tools_status == 'Unmanaged':
            tools_version = "Unknown"
        
        # Eintrag erstellen
        result.append({
            "vm_name": vm_name,
            "esxi_host": esxi_host,
            "tools_version": tools_version,
            "tools_status": tools_status,
            "os": os_type,
            "last_boot": boot_date
        })
    
    logger.info(f"{len(result)} Demo-VMs mit VMware Tools-Informationen generiert")
    return result

def generate_snapshots_data(count=20):
    """
    Generiert realistische Demo-Daten für VM-Snapshots.
    
    Args:
        count (int): Anzahl der zu generierenden Snapshot-Einträge
        
    Returns:
        list: Liste von Dictionaries mit Snapshot-Informationen
    """
    logger.info(f"Generiere Demo-Daten für Snapshots ({count} Snapshots)")
    result = []
    
    # VM-Namen zufällig auswählen (mit möglichen Wiederholungen)
    vm_count = min(15, count)  # Maximal 15 verschiedene VMs für die Snapshots
    selected_vms = random.sample(VM_NAMES, vm_count)
    
    for _ in range(count):
        # Zufällige VM auswählen
        vm_name = random.choice(selected_vms)
        esxi_host = random.choice(ESXI_HOSTS)
        
        # Snapshot-Name und Beschreibung
        snapshot_name = random.choice(SNAPSHOT_NAMES)
        description = random.choice(SNAPSHOT_DESCRIPTIONS)
        
        # Snapshot-Datum generieren (zufällig bis zu 180 Tage alt)
        days_old = random.randint(1, 180)
        date_created = (datetime.now() - timedelta(days=days_old)).strftime("%Y-%m-%d %H:%M")
        
        # Alterskategorie bestimmen
        age_category = "recent"
        if days_old > 90:
            age_category = "danger"
        elif days_old > 30:
            age_category = "warning"
        elif days_old > 7:
            age_category = "warning"
        
        # Größe schätzen
        size_gb = round(random.uniform(1, 50), 2)
        
        # Eintrag erstellen
        result.append({
            "vm_name": vm_name,
            "snapshot_name": snapshot_name,
            "description": description,
            "date_created": date_created,
            "days_old": days_old,
            "age_category": age_category,
            "size_gb": size_gb,
            "esxi_host": esxi_host
        })
    
    # Sortieren nach Alter (älteste zuerst)
    result.sort(key=lambda x: x.get("days_old", 0), reverse=True)
    
    logger.info(f"{len(result)} Demo-Snapshots generiert")
    return result

def generate_orphaned_vmdks_data(count=15):
    """
    Generiert realistische Demo-Daten für verwaiste VMDK-Dateien.
    
    Args:
        count (int): Anzahl der zu generierenden VMDK-Einträge
        
    Returns:
        list: Liste von Dictionaries mit VMDK-Informationen
    """
    logger.info(f"Generiere Demo-Daten für verwaiste VMDKs ({count} Dateien)")
    result = []
    
    for i in range(count):
        # Zufälliger Datastore
        datastore = random.choice(DATASTORES)
        
        # Zufälliger VM-Name (für den vermuteten Ursprung)
        probable_vm = random.choice(VM_NAMES)
        
        # VMDK-Pfad erstellen
        vmdk_name = f"{probable_vm}.vmdk"
        path = f"[{datastore}] {probable_vm}/{vmdk_name}"
        
        # Alter der VMDK
        days_orphaned = random.randint(1, 365)
        last_modified = (datetime.now() - timedelta(days=days_orphaned)).strftime("%Y-%m-%d %H:%M")
        
        # Größe
        size_gb = round(random.uniform(5, 500), 2)
        
        # Thin Provisioning
        thin_provisioned = random.choice([True, False])
        
        # Empfohlene Aktion basierend auf Alter
        if days_orphaned > 90:
            recovery_action = "Kann gelöscht werden"
        elif days_orphaned > 30:
            recovery_action = "Überprüfung empfohlen"
        else:
            recovery_action = "Weitere Analyse erforderlich"
        
        # Eintrag erstellen
        result.append({
            "datastore": datastore,
            "path": path,
            "size_gb": size_gb,
            "last_modified": last_modified,
            "days_orphaned": days_orphaned,
            "thin_provisioned": thin_provisioned,
            "probable_vm": f"{probable_vm} (gelöscht)",
            "recovery_action": recovery_action
        })
    
    # Sortieren nach Datastore und dann nach Größe
    result.sort(key=lambda x: (x.get("datastore", ""), -x.get("size_gb", 0)))
    
    logger.info(f"{len(result)} Demo-VMDKs generiert")
    return result

def get_dashboard_stats():
    """
    Generiert Statistik-Daten für das Dashboard.
    
    Returns:
        dict: Dictionary mit Dashboard-Statistiken
    """
    logger.info("Generiere Dashboard-Statistiken")
    
    # VMware Tools-Daten
    vmware_tools = generate_vmware_tools_data(30)
    tools_current = len([vm for vm in vmware_tools if vm.get('tools_status') == 'Current'])
    tools_update_needed = len([vm for vm in vmware_tools if vm.get('tools_status') == 'UpdateNeeded'])
    tools_not_installed = len([vm for vm in vmware_tools if vm.get('tools_status') == 'NotInstalled'])
    
    # Snapshot-Daten
    snapshots = generate_snapshots_data(20)
    total_snapshot_size = sum(snap.get('size_gb', 0) for snap in snapshots)
    old_snapshots = len([snap for snap in snapshots if snap.get('days_old', 0) > 30])
    
    # Verwaiste VMDK-Daten
    orphaned_vmdks = generate_orphaned_vmdks_data(15)
    total_vmdk_size = sum(vmdk.get('size_gb', 0) for vmdk in orphaned_vmdks)
    
    # Hosts und VMs zählen (für die Demo verwenden wir feste Werte)
    total_hosts = len(ESXI_HOSTS)
    active_hosts = total_hosts - random.randint(0, 2)  # Einige Hosts könnten im Wartungsmodus sein
    total_vms = 35 + random.randint(0, 15)
    powered_on_vms = int(total_vms * 0.85)  # 85% der VMs sind eingeschaltet
    
    # Datastores
    total_datastores = len(DATASTORES)
    datastores_low_space = random.randint(0, 2)
    
    return {
        "hosts": {
            "total": total_hosts,
            "active": active_hosts,
            "maintenance": total_hosts - active_hosts
        },
        "vms": {
            "total": total_vms,
            "powered_on": powered_on_vms,
            "powered_off": total_vms - powered_on_vms
        },
        "storage": {
            "datastores": total_datastores,
            "low_space": datastores_low_space,
            "orphaned_vmdks": len(orphaned_vmdks),
            "orphaned_space_gb": round(total_vmdk_size, 1)
        },
        "tools": {
            "current": tools_current,
            "update_needed": tools_update_needed,
            "not_installed": tools_not_installed
        },
        "snapshots": {
            "total": len(snapshots),
            "old": old_snapshots,
            "size_gb": round(total_snapshot_size, 1)
        }
    }

def get_dashboard_charts():
    """
    Generiert Chartdaten für das Dashboard.
    
    Returns:
        dict: Dictionary mit Chartdaten für das Dashboard
    """
    logger.info("Generiere Dashboard-Chartdaten")
    
    # VM-Betriebssysteme (Donut-Chart)
    os_types = {}
    vms = generate_vmware_tools_data(30)
    for vm in vms:
        os = vm.get('os', 'Unbekannt')
        # Vereinfache OS-Namen für die Anzeige
        if 'Windows' in os:
            simple_os = 'Windows'
        elif 'Linux' in os:
            simple_os = 'Linux'
        elif 'CentOS' in os:
            simple_os = 'Linux'
        elif 'Ubuntu' in os:
            simple_os = 'Linux'
        elif 'SUSE' in os:
            simple_os = 'Linux'
        elif 'Red Hat' in os:
            simple_os = 'Linux'
        elif 'Debian' in os:
            simple_os = 'Linux'
        elif 'Oracle' in os:
            simple_os = 'Linux'
        elif 'Photon' in os:
            simple_os = 'VMware Photon OS'
        else:
            simple_os = 'Andere'
        
        os_types[simple_os] = os_types.get(simple_os, 0) + 1
    
    # Snapshot-Alter (Balkendiagramm)
    snapshots = generate_snapshots_data(20)
    age_ranges = {
        '0-7 Tage': 0,
        '8-30 Tage': 0,
        '31-90 Tage': 0,
        '> 90 Tage': 0
    }
    
    for snap in snapshots:
        days_old = snap.get('days_old', 0)
        if days_old <= 7:
            age_ranges['0-7 Tage'] += 1
        elif days_old <= 30:
            age_ranges['8-30 Tage'] += 1
        elif days_old <= 90:
            age_ranges['31-90 Tage'] += 1
        else:
            age_ranges['> 90 Tage'] += 1
    
    # Host-Status (Donut-Chart)
    host_status = {
        'Normal': len(ESXI_HOSTS) - random.randint(0, 2),
        'Wartung': random.randint(0, 2)
    }
    
    # VM-Status (Donut-Chart)
    vm_status = {
        'Eingeschaltet': int(30 * 0.85),
        'Ausgeschaltet': int(30 * 0.15)
    }
    
    return {
        "os_distribution": {
            "labels": list(os_types.keys()),
            "data": list(os_types.values())
        },
        "snapshot_age": {
            "labels": list(age_ranges.keys()),
            "data": list(age_ranges.values())
        },
        "host_status": {
            "labels": list(host_status.keys()),
            "data": list(host_status.values())
        },
        "vm_status": {
            "labels": list(vm_status.keys()),
            "data": list(vm_status.values())
        }
    }

def get_all_demo_data():
    """
    Generiert einen vollständigen Satz Demo-Daten für alle Berichtstypen.
    
    Returns:
        dict: Dictionary mit Demo-Daten für alle Berichte
    """
    logger.info("Generiere vollständigen Satz Demo-Daten")
    return {
        "vmware_tools": generate_vmware_tools_data(count=30),
        "snapshots": generate_snapshots_data(count=20),
        "orphaned_vmdks": generate_orphaned_vmdks_data(count=15),
        "dashboard_stats": get_dashboard_stats(),
        "dashboard_charts": get_dashboard_charts()
    }