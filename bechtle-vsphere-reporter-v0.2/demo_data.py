"""
Bechtle vSphere Reporter v0.2 - Demo Daten
Stellt Beispieldaten für die Demo-Version bereit

Da die Anwendung auch ohne Verbindung zu einem vCenter getestet werden soll,
werden hier realistische Beispieldaten bereitgestellt, die die Struktur und
den Umfang realer Daten simulieren. Dies ermöglicht die Demonstration aller
Funktionen ohne echte vCenter-Verbindung.

© 2025 Bechtle GmbH - Alle Rechte vorbehalten
"""

from datetime import datetime, timedelta

def get_demo_data():
    """
    Erzeugt strukturierte Beispieldaten für die Demonstration

    Returns:
        dict: Dictionary mit simulierten Daten für VMware Tools, Snapshots und VMDKs
    """
    # Aktuelles Datum für die relativen Zeitangaben
    now = datetime.now()

    # VMware Tools Daten
    vmware_tools_data = [
        {
            'name': 'Windows-App-Server01',
            'tools_version': '12000',
            'tools_status': 'guestToolsCurrent',
            'tools_running_status': 'guestToolsRunning',
            'last_update': (now - timedelta(days=30)).strftime('%Y-%m-%d'),
            'os': 'Microsoft Windows Server 2019 (64-bit)',
            'status_class': 'success',
            'status_text': 'Aktuell',
            'running_class': 'success',
            'running_text': 'Laufend'
        },
        {
            'name': 'Linux-DB-Server01',
            'tools_version': '11000',
            'tools_status': 'guestToolsNeedUpgrade',
            'tools_running_status': 'guestToolsRunning',
            'last_update': (now - timedelta(days=180)).strftime('%Y-%m-%d'),
            'os': 'Ubuntu Linux (64-bit)',
            'status_class': 'warning',
            'status_text': 'Update verfügbar',
            'running_class': 'success',
            'running_text': 'Laufend'
        },
        {
            'name': 'Windows-Test-VM01',
            'tools_version': 'Nicht installiert',
            'tools_status': 'guestToolsNotInstalled',
            'tools_running_status': 'guestToolsNotRunning',
            'last_update': '',
            'os': 'Microsoft Windows 10 (64-bit)',
            'status_class': 'danger',
            'status_text': 'Nicht installiert',
            'running_class': 'danger',
            'running_text': 'Nicht laufend'
        },
        {
            'name': 'Linux-Web-Server01',
            'tools_version': '12000',
            'tools_status': 'guestToolsCurrent',
            'tools_running_status': 'guestToolsRunning',
            'last_update': (now - timedelta(days=5)).strftime('%Y-%m-%d'),
            'os': 'CentOS Linux (64-bit)',
            'status_class': 'success',
            'status_text': 'Aktuell',
            'running_class': 'success',
            'running_text': 'Laufend'
        },
        {
            'name': 'Windows-DC01',
            'tools_version': '11000',
            'tools_status': 'guestToolsNeedUpgrade',
            'tools_running_status': 'guestToolsRunning',
            'last_update': (now - timedelta(days=120)).strftime('%Y-%m-%d'),
            'os': 'Microsoft Windows Server 2016 (64-bit)',
            'status_class': 'warning',
            'status_text': 'Update verfügbar',
            'running_class': 'success',
            'running_text': 'Laufend'
        }
    ]

    # Snapshot Daten
    snapshots_data = [
        {
            'vm_name': 'Windows-App-Server01',
            'name': 'Vor Update 1.2',
            'path': 'Vor Update 1.2',
            'description': 'Erstellung vor dem Windows Update',
            'create_time': now - timedelta(days=45),
            'days_old': 45,
            'hours_old': 45 * 24,
            'size_gb': 24.5,
            'id': 'snapshot-1001',
            'create_time_str': (now - timedelta(days=45)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '45 Tage, 0 Stunden',
            'size_str': '24.50 GB',
            'age_class': 'danger'
        },
        {
            'vm_name': 'Linux-DB-Server01',
            'name': 'Backup-22-04-2025',
            'path': 'Backup-22-04-2025',
            'description': 'Monatliche Sicherung',
            'create_time': now - timedelta(days=17),
            'days_old': 17,
            'hours_old': 17 * 24,
            'size_gb': 18.2,
            'id': 'snapshot-1002',
            'create_time_str': (now - timedelta(days=17)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '17 Tage, 0 Stunden',
            'size_str': '18.20 GB',
            'age_class': 'warning'
        },
        {
            'vm_name': 'Windows-Test-VM01',
            'name': 'Vor Installation',
            'path': 'Vor Installation',
            'description': 'Zustand vor Softwareinstallation',
            'create_time': now - timedelta(days=3),
            'days_old': 3,
            'hours_old': 3 * 24,
            'size_gb': 12.8,
            'id': 'snapshot-1003',
            'create_time_str': (now - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '3 Tage, 0 Stunden',
            'size_str': '12.80 GB',
            'age_class': 'success'
        },
        {
            'vm_name': 'Windows-DC01',
            'name': 'Vor Konfigurationsänderung',
            'path': 'Vor Konfigurationsänderung',
            'description': 'Sicherung vor AD-Änderungen',
            'create_time': now - timedelta(days=35),
            'days_old': 35,
            'hours_old': 35 * 24,
            'size_gb': 29.7,
            'id': 'snapshot-1004',
            'create_time_str': (now - timedelta(days=35)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '35 Tage, 0 Stunden',
            'size_str': '29.70 GB',
            'age_class': 'danger'
        },
        {
            'vm_name': 'Linux-Web-Server01',
            'name': 'Post-Update',
            'path': 'Post-Update',
            'description': 'Nach System-Updates',
            'create_time': now - timedelta(days=10),
            'days_old': 10,
            'hours_old': 10 * 24,
            'size_gb': 15.3,
            'id': 'snapshot-1005',
            'create_time_str': (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            'age_str': '10 Tage, 0 Stunden',
            'size_str': '15.30 GB',
            'age_class': 'warning'
        }
    ]

    # Verwaiste VMDK Daten
    modification_times = [
        now - timedelta(days=180),
        now - timedelta(days=95),
        now - timedelta(days=60),
        now - timedelta(days=45),
        now - timedelta(days=30)
    ]

    orphaned_vmdks = [
        {
            'path': '[DataStore1] old_vm01/old_vm01.vmdk',
            'datastore': 'DataStore1',
            'size_kb': 42949672,  # 40 GB in KB
            'modification_time': modification_times[0].strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'path': '[DataStore2] db_backup/db_backup.vmdk',
            'datastore': 'DataStore2',
            'size_kb': 21474836,  # 20 GB in KB
            'modification_time': modification_times[1].strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'path': '[DataStore1] old_test/old_test.vmdk',
            'datastore': 'DataStore1',
            'size_kb': 10737418,  # 10 GB in KB
            'modification_time': modification_times[2].strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'path': '[DataStore3] temp_web/temp_web.vmdk',
            'datastore': 'DataStore3',
            'size_kb': 16106127,  # 15 GB in KB
            'modification_time': modification_times[3].strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'path': '[DataStore2] deleted_app/deleted_app.vmdk',
            'datastore': 'DataStore2',
            'size_kb': 32212254,  # 30 GB in KB
            'modification_time': modification_times[4].strftime('%Y-%m-%d %H:%M:%S')
        }
    ]

    # Raw data für das Debugging
    raw_data = {
        'datastore_browser_data': [
            {'datastore': 'DataStore1', 'vm_count': 15, 'total_capacity_gb': 1000, 'free_space_gb': 450},
            {'datastore': 'DataStore2', 'vm_count': 10, 'total_capacity_gb': 800, 'free_space_gb': 320},
            {'datastore': 'DataStore3', 'vm_count': 5, 'total_capacity_gb': 500, 'free_space_gb': 200}
        ],
        'vm_disk_data': [
            # Daten über registrierte VMs und deren Festplatten
            {'vm_name': 'Windows-App-Server01', 'disk_path': '[DataStore1] Windows-App-Server01/Windows-App-Server01.vmdk', 'size_gb': 80},
            {'vm_name': 'Linux-DB-Server01', 'disk_path': '[DataStore2] Linux-DB-Server01/Linux-DB-Server01.vmdk', 'size_gb': 120},
            {'vm_name': 'Windows-Test-VM01', 'disk_path': '[DataStore1] Windows-Test-VM01/Windows-Test-VM01.vmdk', 'size_gb': 60},
            {'vm_name': 'Linux-Web-Server01', 'disk_path': '[DataStore3] Linux-Web-Server01/Linux-Web-Server01.vmdk', 'size_gb': 40},
            {'vm_name': 'Windows-DC01', 'disk_path': '[DataStore2] Windows-DC01/Windows-DC01.vmdk', 'size_gb': 100}
        ],
        'all_vmdk_paths': [
            # Alle gefundenen VMDK-Dateien
            {'path': '[DataStore1] Windows-App-Server01/Windows-App-Server01.vmdk', 'size_kb': 85899345, 'modification_time': (now - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore2] Linux-DB-Server01/Linux-DB-Server01.vmdk', 'size_kb': 128849018, 'modification_time': (now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore1] Windows-Test-VM01/Windows-Test-VM01.vmdk', 'size_kb': 64424509, 'modification_time': (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore3] Linux-Web-Server01/Linux-Web-Server01.vmdk', 'size_kb': 42949672, 'modification_time': (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore2] Windows-DC01/Windows-DC01.vmdk', 'size_kb': 107374182, 'modification_time': (now - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S')},
            # Verwaiste VMDKs
            {'path': '[DataStore1] old_vm01/old_vm01.vmdk', 'size_kb': 42949672, 'modification_time': modification_times[0].strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore2] db_backup/db_backup.vmdk', 'size_kb': 21474836, 'modification_time': modification_times[1].strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore1] old_test/old_test.vmdk', 'size_kb': 10737418, 'modification_time': modification_times[2].strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore3] temp_web/temp_web.vmdk', 'size_kb': 16106127, 'modification_time': modification_times[3].strftime('%Y-%m-%d %H:%M:%S')},
            {'path': '[DataStore2] deleted_app/deleted_app.vmdk', 'size_kb': 32212254, 'modification_time': modification_times[4].strftime('%Y-%m-%d %H:%M:%S')}
        ],
        'registered_vmdk_paths': [
            '[DataStore1] Windows-App-Server01/Windows-App-Server01.vmdk',
            '[DataStore2] Linux-DB-Server01/Linux-DB-Server01.vmdk',
            '[DataStore1] Windows-Test-VM01/Windows-Test-VM01.vmdk',
            '[DataStore3] Linux-Web-Server01/Linux-Web-Server01.vmdk',
            '[DataStore2] Windows-DC01/Windows-DC01.vmdk'
        ],
        'orphaned_vmdks': orphaned_vmdks,
        'vm_count': 5,
        'datastore_count': 3
    }

    # Ergebnis zusammenstellen
    return {
        'vmware_tools_data': vmware_tools_data,
        'snapshots_data': snapshots_data,
        'orphaned_vmdks': orphaned_vmdks,
        'raw_data': raw_data
    }