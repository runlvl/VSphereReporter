"""
Demo-Daten für VMware vSphere Reporter
"""

from datetime import datetime, timedelta

def get_demo_data():
    """
    Demo-Daten generieren
    
    Returns:
        dict: Demo-Daten für die Anwendung
    """
    now = datetime.now()
    
    # Demo-Daten für VMDKs
    raw_data = {
        'vm_count': 5,
        'datastore_count': 2,
        'datastore_browser_data': [
            {
                'datastore': 'datastore1',
                'folder': '[datastore1] vm1/',
                'file_count': 2
            },
            {
                'datastore': 'datastore1',
                'folder': '[datastore1] vm2/',
                'file_count': 3
            },
            {
                'datastore': 'datastore1',
                'folder': '[datastore1] vm3/',
                'file_count': 1
            },
            {
                'datastore': 'datastore1',
                'folder': '[datastore1] orphaned_vms/',
                'file_count': 2
            },
            {
                'datastore': 'datastore2',
                'folder': '[datastore2] vm4/',
                'file_count': 2
            },
            {
                'datastore': 'datastore2',
                'folder': '[datastore2] vm5/',
                'file_count': 1
            },
        ],
        'vm_disk_data': [
            {
                'vm_name': 'vm1',
                'disk_path': '[datastore1] vm1/vm1.vmdk',
                'disk_size_gb': 40.0,
                'device_key': 2000
            },
            {
                'vm_name': 'vm1',
                'disk_path': '[datastore1] vm1/vm1_1.vmdk',
                'disk_size_gb': 20.0,
                'device_key': 2001
            },
            {
                'vm_name': 'vm2',
                'disk_path': '[datastore1] vm2/vm2.vmdk',
                'disk_size_gb': 60.0,
                'device_key': 2000
            },
            {
                'vm_name': 'vm3',
                'disk_path': '[datastore1] vm3/vm3.vmdk',
                'disk_size_gb': 80.0,
                'device_key': 2000
            },
            {
                'vm_name': 'vm4',
                'disk_path': '[datastore2] vm4/vm4.vmdk',
                'disk_size_gb': 100.0,
                'device_key': 2000
            },
            {
                'vm_name': 'vm4',
                'disk_path': '[datastore2] vm4/vm4_1.vmdk',
                'disk_size_gb': 200.0,
                'device_key': 2001
            },
            {
                'vm_name': 'vm5',
                'disk_path': '[datastore2] vm5/vm5.vmdk',
                'disk_size_gb': 50.0,
                'device_key': 2000
            }
        ],
        'registered_vmdk_paths': [
            '[datastore1] vm1/vm1.vmdk',
            '[datastore1] vm1/vm1_1.vmdk',
            '[datastore1] vm2/vm2.vmdk',
            '[datastore1] vm3/vm3.vmdk',
            '[datastore2] vm4/vm4.vmdk',
            '[datastore2] vm4/vm4_1.vmdk',
            '[datastore2] vm5/vm5.vmdk'
        ],
        'all_vmdk_paths': [
            {
                'path': '[datastore1] vm1/vm1.vmdk',
                'size_kb': 41943040,
                'modification_time': (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore1] vm1/vm1_1.vmdk',
                'size_kb': 20971520,
                'modification_time': (now - timedelta(days=25)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore1] vm2/vm2.vmdk',
                'size_kb': 62914560,
                'modification_time': (now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore1] vm3/vm3.vmdk',
                'size_kb': 83886080,
                'modification_time': (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore2] vm4/vm4.vmdk',
                'size_kb': 104857600,
                'modification_time': (now - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore2] vm4/vm4_1.vmdk',
                'size_kb': 209715200,
                'modification_time': (now - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore2] vm5/vm5.vmdk',
                'size_kb': 52428800,
                'modification_time': (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore1] orphaned_vms/old_vm1.vmdk',
                'size_kb': 31457280,
                'modification_time': (now - timedelta(days=100)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore1] orphaned_vms/old_vm2.vmdk',
                'size_kb': 20971520,
                'modification_time': (now - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
            }
        ],
        'orphaned_vmdks': [
            {
                'path': '[datastore1] orphaned_vms/old_vm1.vmdk',
                'size_kb': 31457280,
                'modification_time': (now - timedelta(days=100)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'path': '[datastore1] orphaned_vms/old_vm2.vmdk',
                'size_kb': 20971520,
                'modification_time': (now - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
    }
    
    return raw_data