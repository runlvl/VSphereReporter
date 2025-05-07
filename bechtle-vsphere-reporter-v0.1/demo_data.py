"""
Demo-Daten für VMware vSphere Reporter
"""

from datetime import datetime, timedelta

def get_demo_data():
    """Generiere Demo-Daten für die Anwendung"""
    now = datetime.now()
    
    # Demo-Daten für VMware Tools
    vmware_tools_data = [
        {
            'name': 'demo-vm01',
            'tools_version': '11000',
            'tools_status': 'guestToolsNeedUpgrade',
            'tools_running_status': 'guestToolsRunning',
            'os': 'Microsoft Windows Server 2019',
            'status_class': 'warning',
            'status_text': 'Update verfügbar',
            'running_class': 'success',
            'running_text': 'Laufend',
            'last_update': (now - timedelta(days=180)).strftime('%Y-%m-%d')
        },
        {
            'name': 'demo-vm02',
            'tools_version': '12000',
            'tools_status': 'guestToolsCurrent',
            'tools_running_status': 'guestToolsRunning',
            'os': 'Microsoft Windows Server 2022',
            'status_class': 'success',
            'status_text': 'Aktuell',
            'running_class': 'success',
            'running_text': 'Laufend',
            'last_update': (now - timedelta(days=30)).strftime('%Y-%m-%d')
        },
        {
            'name': 'demo-vm03',
            'tools_version': 'Nicht installiert',
            'tools_status': 'guestToolsNotInstalled',
            'tools_running_status': 'guestToolsNotRunning',
            'os': 'Ubuntu Linux 20.04',
            'status_class': 'danger',
            'status_text': 'Nicht installiert',
            'running_class': 'danger',
            'running_text': 'Nicht laufend',
            'last_update': 'Nie'
        }
    ]
    
    # Demo-Daten für Snapshots
    snapshots_data = [
        {
            'vm_name': 'demo-vm01',
            'name': 'Pre-Update Snapshot',
            'path': 'Pre-Update Snapshot',
            'description': 'Snapshot vor Windows-Update',
            'create_time': now - timedelta(days=45),
            'days_old': 45,
            'hours_old': 4,
            'size_gb': 24.5,
            'id': 'snapshot-1001',
            'create_time_str': (now - timedelta(days=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '45 Tage, 4 Stunden',
            'size_str': '24.50 GB',
            'age_class': 'danger'
        },
        {
            'vm_name': 'demo-vm02',
            'name': 'Before App Installation',
            'path': 'Before App Installation',
            'description': 'Vor Installation neuer Software',
            'create_time': now - timedelta(days=15),
            'days_old': 15,
            'hours_old': 2,
            'size_gb': 18.2,
            'id': 'snapshot-1002',
            'create_time_str': (now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '15 Tage, 2 Stunden',
            'size_str': '18.20 GB',
            'age_class': 'warning'
        },
        {
            'vm_name': 'demo-vm03',
            'name': 'Clean State',
            'path': 'Clean State',
            'description': 'System nach frischer Installation',
            'create_time': now - timedelta(days=3),
            'days_old': 3,
            'hours_old': 6,
            'size_gb': 12.8,
            'id': 'snapshot-1003',
            'create_time_str': (now - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '3 Tage, 6 Stunden',
            'size_str': '12.80 GB',
            'age_class': 'success'
        }
    ]
    
    # Demo-Daten für VMDKs
    raw_data = {
        'vm_count': 5,
        'datastore_count': 2,
        'datastore_browser_data': [
            {
                'datastore': 'demo-datastore1',
                'folder': '[demo-datastore1] demo-vm01/',
                'file_count': 2
            },
            {
                'datastore': 'demo-datastore1',
                'folder': '[demo-datastore1] demo-vm02/',
                'file_count': 3
            },
            {
                'datastore': 'demo-datastore1',
                'folder': '[demo-datastore1] demo-vm03/',
                'file_count': 1
            },
            {
                'datastore': 'demo-datastore1',
                'folder': '[demo-datastore1] orphaned_vms/',
                'file_count': 2
            },
            {
                'datastore': 'demo-datastore2',
                'folder': '[demo-datastore2] demo-vm04/',
                'file_count': 2
            },
        ],
        'vm_disk_data': [
            {
                'vm_name': 'demo-vm01',
                'disk_path': '[demo-datastore1] demo-vm01/demo-vm01.vmdk',
                'disk_size_gb': 40.0,
                'device_key': 2000
            },
            {
                'vm_name': 'demo-vm01',
                'disk_path': '[demo-datastore1] demo-vm01/demo-vm01_1.vmdk',
                'disk_size_gb': 20.0,
                'device_key': 2001
            },
            {
                'vm_name': 'demo-vm02',
                'disk_path': '[demo-datastore1] demo-vm02/demo-vm02.vmdk',
                'disk_size_gb': 60.0,
                'device_key': 2000
            },
            {
                'vm_name': 'demo-vm03',
                'disk_path': '[demo-datastore1] demo-vm03/demo-vm03.vmdk',
                'disk_size_gb': 80.0,
                'device_key': 2000
            },
            {
                'vm_name': 'demo-vm04',
                'disk_path': '[demo-datastore2] demo-vm04/demo-vm04.vmdk',
                'disk_size_gb': 100.0,
                'device_key': 2000
            }
        ],
        'registered_vmdk_paths': [
            '[demo-datastore1] demo-vm01/demo-vm01.vmdk',
            '[demo-datastore1] demo-vm01/demo-vm01_1.vmdk',
            '[demo-datastore1] demo-vm02/demo-vm02.vmdk',
            '[demo-datastore1] demo-vm03/demo-vm03.vmdk',
            '[demo-datastore2] demo-vm04/demo-vm04.vmdk'
        ],
        'all_vmdk_paths': [
            {
                'path': '[demo-datastore1] demo-vm01/demo-vm01.vmdk',
                'size_kb': 41943040,
                'modification_time': (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'registered'
            },
            {
                'path': '[demo-datastore1] demo-vm01/demo-vm01_1.vmdk',
                'size_kb': 20971520,
                'modification_time': (now - timedelta(days=25)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'registered'
            },
            {
                'path': '[demo-datastore1] demo-vm02/demo-vm02.vmdk',
                'size_kb': 62914560,
                'modification_time': (now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'registered'
            },
            {
                'path': '[demo-datastore1] demo-vm03/demo-vm03.vmdk',
                'size_kb': 83886080,
                'modification_time': (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'registered'
            },
            {
                'path': '[demo-datastore2] demo-vm04/demo-vm04.vmdk',
                'size_kb': 104857600,
                'modification_time': (now - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'registered'
            },
            {
                'path': '[demo-datastore1] orphaned_vms/old_vm1.vmdk',
                'size_kb': 31457280,
                'modification_time': (now - timedelta(days=100)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'orphaned'
            },
            {
                'path': '[demo-datastore1] orphaned_vms/old_vm2.vmdk',
                'size_kb': 20971520,
                'modification_time': (now - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'orphaned'
            }
        ],
        'orphaned_vmdks': [
            {
                'path': '[demo-datastore1] orphaned_vms/old_vm1.vmdk',
                'size_kb': 31457280,
                'modification_time': (now - timedelta(days=100)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[demo-datastore1] orphaned_vms/old_vm2.vmdk',
                'size_kb': 20971520,
                'modification_time': (now - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    }
    
    return {
        'vmware_tools_data': vmware_tools_data,
        'snapshots_data': snapshots_data,
        'orphaned_vmdks': raw_data['orphaned_vmdks'],
        'raw_data': raw_data
    }