#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMware vSphere Reporter v29.0
Demo Data Module

Final Fixed Version 10 - Simplified Structure
Copyright (c) 2025 Bechtle GmbH
"""

import datetime
import random

def get_total_vms():
    """Get total number of VMs for demo mode
    
    Returns:
        int: Demo VM count
    """
    return 125

def get_total_hosts():
    """Get total number of hosts for demo mode
    
    Returns:
        int: Demo host count
    """
    return 8

def get_total_datastores():
    """Get total number of datastores for demo mode
    
    Returns:
        int: Demo datastore count
    """
    return 12

def get_total_clusters():
    """Get total number of clusters for demo mode
    
    Returns:
        int: Demo cluster count
    """
    return 3

def get_vms_by_power_state():
    """Get VMs by power state for demo mode
    
    Returns:
        dict: Dictionary with power states as keys and counts as values
    """
    return {
        'poweredOn': 92,
        'poweredOff': 27,
        'suspended': 6
    }

def get_outdated_tools_count():
    """Get count of VMs with outdated VMware Tools for demo mode
    
    Returns:
        int: Demo count of VMs with outdated VMware Tools
    """
    return 23

def get_snapshots_count():
    """Get total number of snapshots for demo mode
    
    Returns:
        int: Demo snapshot count
    """
    return 17

def get_orphaned_vmdks_count():
    """Get count of orphaned VMDK files for demo mode
    
    Returns:
        int: Demo orphaned VMDK count
    """
    return 8

def get_vmware_tools_data():
    """Get demo VMware Tools data
    
    Returns:
        list: List of dictionaries with VMware Tools information
    """
    vm_prefixes = ['web', 'db', 'app', 'ad', 'file', 'print', 'mail', 'backup', 'test', 'dev']
    os_types = [
        'Microsoft Windows Server 2019 (64-bit)',
        'Microsoft Windows Server 2016 (64-bit)',
        'Microsoft Windows Server 2012 R2 (64-bit)',
        'Red Hat Enterprise Linux 8 (64-bit)',
        'Red Hat Enterprise Linux 7 (64-bit)',
        'Ubuntu Linux (64-bit)',
        'SUSE Linux Enterprise 15 (64-bit)',
        'CentOS 7 (64-bit)',
        'Debian GNU/Linux 10 (64-bit)',
        'Oracle Linux 8 (64-bit)'
    ]
    
    tools_versions = [
        '10336', '10338', '10341', '10346', '11356', '11357', '12020'
    ]
    
    tools_data = []
    
    # Generate a set of VMs with different combinations
    for i in range(1, 51):
        prefix = random.choice(vm_prefixes)
        vm_name = f"{prefix}-{str(i).zfill(2)}"
        os_name = random.choice(os_types)
        
        # Determine VMware Tools status
        status_roll = random.random()
        if status_roll < 0.20:  # 20% not installed
            status = "Not installed"
            version = "Not installed"
        elif status_roll < 0.40:  # 20% outdated
            status = "Outdated"
            version = tools_versions[0]  # Use oldest version
        else:  # 60% up-to-date
            status = "Up-to-date"
            version = tools_versions[-1]  # Use newest version
        
        # Determine power state
        power_roll = random.random()
        if power_roll < 0.75:  # 75% powered on
            power_state = "poweredOn"
        elif power_roll < 0.95:  # 20% powered off
            power_state = "poweredOff"
        else:  # 5% suspended
            power_state = "suspended"
        
        tools_data.append({
            'vm_name': vm_name,
            'status': status,
            'version': version,
            'os': os_name,
            'power_state': power_state
        })
    
    return tools_data

def get_snapshots_data():
    """Get demo snapshot data
    
    Returns:
        list: List of dictionaries with snapshot information
    """
    vm_prefixes = ['web', 'db', 'app', 'ad', 'file', 'print', 'mail', 'backup', 'test', 'dev']
    snapshot_purposes = [
        'Before update', 'After update', 'Before patch', 'Config backup', 
        'Pre-migration', 'Testing', 'Backup', 'Recovery point', 'Weekly backup'
    ]
    
    snapshots = []
    now = datetime.datetime.now()
    
    # Generate a set of snapshots with different ages
    for i in range(1, 18):  # 17 snapshots (matching the count from get_snapshots_count)
        prefix = random.choice(vm_prefixes)
        vm_name = f"{prefix}-{random.randint(1, 30):02d}"
        name = f"{random.choice(snapshot_purposes)}"
        
        # Determine age - bias towards older snapshots for reporting
        age_roll = random.random()
        if age_roll < 0.3:  # 30% very old (30-90 days)
            days_old = random.randint(30, 90)
        elif age_roll < 0.6:  # 30% old (10-30 days)
            days_old = random.randint(10, 29)
        elif age_roll < 0.9:  # 30% recent (1-10 days)
            days_old = random.randint(1, 9)
        else:  # 10% very recent (0-24 hours)
            days_old = random.random()
        
        creation_time = now - datetime.timedelta(days=days_old)
        
        # Size between 1GB and 40GB
        size_mb = random.randint(1024, 40960)
        
        snapshots.append({
            'vm_name': vm_name,
            'name': name,
            'description': f"{name} - created by system",
            'creation_time': creation_time,
            'size_mb': size_mb,
            'path': f"{vm_name}/{name}",
            'state': 'ready'
        })
    
    return snapshots

def get_orphaned_vmdks_data():
    """Get demo orphaned VMDK data
    
    Returns:
        list: List of dictionaries with orphaned VMDK information
    """
    datastores = ['datastore1', 'datastore2', 'datastore3', 'SAN01', 'SAN02', 'NAS01']
    vm_prefixes = ['web', 'db', 'app', 'ad', 'file', 'print', 'mail', 'backup', 'test', 'dev']
    
    orphaned_vmdks = []
    
    # Generate a set of orphaned VMDKs
    for i in range(1, 9):  # 8 orphaned VMDKs (matching the count from get_orphaned_vmdks_count)
        prefix = random.choice(vm_prefixes)
        vm_name = f"{prefix}-{random.randint(1, 30):02d}"
        datastore = random.choice(datastores)
        
        # Generate a realistic VMDK path
        vmdk_name = f"{vm_name}/{vm_name}.vmdk"
        path = f"[{datastore}] {vmdk_name}"
        
        # Size between 1GB and 400GB
        size_bytes = random.randint(1, 400) * 1024 * 1024 * 1024
        
        # Recommended action
        actions = [
            "Manuelle Überprüfung erforderlich",
            "Sichern und löschen",
            "Zu VM zuordnen",
            "Löschen nach Überprüfung",
            "In Storage vMotion einbeziehen"
        ]
        
        orphaned_vmdks.append({
            'name': vmdk_name,
            'datastore': datastore,
            'path': path,
            'size_bytes': size_bytes,
            'recommended_action': random.choice(actions)
        })
    
    return orphaned_vmdks