"""
Bechtle vSphere Reporter - Demo Data Generator
Erstellt synthetische Daten für den Demo-Modus.
"""

import random
from datetime import datetime, timedelta
from collections import namedtuple
import logging

logger = logging.getLogger('vsphere_reporter')

class DemoVSphereClient:
    """Simulierter vSphere-Client für den Demo-Modus"""
    
    def __init__(self):
        """Initialisiert den Demo-Client"""
        self.server = "demo-vcenter.bechtle.local"
        self.username = "demo-admin@bechtle.local"
        self.password = "**********"
        logger.info(f"Demo-Modus initialisiert mit Server {self.server}")
    
    def is_connected(self):
        """Simulation einer aktiven Verbindung"""
        return True
    
    def disconnect(self):
        """Simulation einer Verbindungstrennung"""
        logger.info("Demo-Verbindung getrennt")
    
    def generate_fallback_data(self, path, name):
        """
        Generiert synthetische Daten für VMDKs im Demo-Modus
        
        Args:
            path: VMDK-Pfad
            name: VMDK-Name
            
        Returns:
            dict: Generierte Fallback-Daten
        """
        # Generiere Datumswerte (30 bis 730 Tage alt)
        days_old = random.randint(30, 730)
        size_gb = random.randint(10, 110)  # 10 bis 110 GB
        
        creation_date = datetime.now() - timedelta(days=days_old)
        
        return {
            'size_gb': size_gb,
            'creation_date': creation_date.strftime('%Y-%m-%d'),
            'days_old': days_old
        }

class DemoDataCollector:
    """Datensammler mit synthetischen Demo-Daten"""
    
    def __init__(self, client):
        """
        Initialisiert den Demo-Datensammler
        
        Args:
            client: Demo vSphere-Client
        """
        self.client = client
    
    def get_environment_stats(self):
        """
        Liefert Demo-Umgebungsstatistiken
        
        Returns:
            dict: Synthetische Umgebungsstatistiken
        """
        return {
            'vms': {
                'total': 42,
                'powered_on': 35,
                'powered_off': 7
            },
            'datastores': {
                'total': 8,
                'total_space_gb': 16384,
                'free_space_gb': 8192
            },
            'snapshots': {
                'total': 15,
                'oldest_days': 45
            },
            'tools_status': {
                'up_to_date': 28,
                'out_of_date': 12,
                'not_installed': 2
            },
            'orphaned_vmdks': {
                'total': 6,
                'total_size_gb': 320
            }
        }
    
    def get_vmware_tools_status(self):
        """
        Liefert Demo-Daten für VMware Tools-Status
        
        Returns:
            list: Liste von Demo-VM-Objekten mit Tools-Status
        """
        result = []
        
        # Typische VM-Präfixe für eine realistische Demo
        vm_prefixes = ['srv', 'app', 'db', 'web', 'dev', 'test', 'prod']
        
        # Verschiedene Statuswerte
        status_options = [
            {'message': 'Aktuell', 'class': 'ok', 'version': '12345', 'detail': 'guestToolsCurrent'},
            {'message': 'Veraltet', 'class': 'warning', 'version': '10000', 'detail': 'guestToolsNeedUpgrade'},
            {'message': 'Nicht installiert', 'class': 'critical', 'version': '0', 'detail': 'guestToolsNotInstalled'}
        ]
        
        # Gewichtung für eine realistische Verteilung
        weights = [0.7, 0.25, 0.05]  # Wahrscheinlichkeiten für ok, warning, critical
        
        for i in range(42):  # 42 Demo-VMs
            prefix = random.choice(vm_prefixes)
            num = random.randint(1, 999)
            vm_name = f"{prefix}{num:03d}.bechtle.local"
            
            # Gewichtete Zufallsauswahl des Status
            status_idx = random.choices(range(len(status_options)), weights=weights, k=1)[0]
            status = status_options[status_idx]
            
            power_state = "Eingeschaltet"
            if random.random() < 0.15:  # 15% Wahrscheinlichkeit für ausgeschaltete VMs
                power_state = "Ausgeschaltet"
            
            result.append({
                'vm_name': vm_name,
                'power_state': power_state,
                'tools_status': status['message'],
                'tools_version': status['version'],
                'tools_version_detail': status['detail'],
                'status_class': status['class']
            })
        
        # Sortieren nach Status (Kritisch/Warnung zuerst) und dann nach Namen
        def sort_key(item):
            # Gewichtung für Sortierreihenfolge
            order = {"critical": 0, "warning": 1, "ok": 2, "unknown": 3}
            return (order.get(item.get('status_class', 'unknown'), 999), item.get('vm_name', ''))
        
        return sorted(result, key=sort_key)
    
    def get_snapshot_info(self):
        """
        Liefert Demo-Daten für Snapshots
        
        Returns:
            list: Liste von Demo-Snapshot-Infos
        """
        result = []
        
        # Typische VM-Präfixe für eine realistische Demo
        vm_prefixes = ['srv', 'app', 'db', 'web', 'dev', 'test', 'prod']
        
        # Typische Snapshot-Namen
        snapshot_reasons = [
            "Vor Update", "Vor Patch", "Backup", "Test", "Migration",
            "Vor Konfigurationsänderung", "Vor Softwareinstallation"
        ]
        
        # Generiere 15 Demo-Snapshots
        for i in range(15):
            prefix = random.choice(vm_prefixes)
            num = random.randint(1, 999)
            vm_name = f"{prefix}{num:03d}.bechtle.local"
            
            # Snapshot-Alter zwischen 1 und 60 Tagen
            days_old = random.randint(1, 60)
            create_time = datetime.now() - timedelta(days=days_old)
            
            # Snapshot-Name
            reason = random.choice(snapshot_reasons)
            snapshot_name = f"{reason} {create_time.strftime('%Y-%m-%d')}"
            
            # Description
            description = f"Snapshot erstellt vor {reason.lower()}"
            
            # Bestimme Status-Klasse basierend auf dem Alter
            status_class = "ok"
            if days_old > 30:
                status_class = "critical"
            elif days_old > 7:
                status_class = "warning"
            
            result.append({
                'vm_name': vm_name,
                'vm_moref': f"vm-{random.randint(1000, 9999)}",
                'name': snapshot_name,
                'description': description,
                'create_time': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'id': f"snapshot-{random.randint(1000, 9999)}",
                'snapshot_moref': f"snapshot-{random.randint(1000, 9999)}",
                'days_old': days_old,
                'status_class': status_class
            })
        
        # Sortieren nach Alter (älteste zuerst)
        return sorted(result, key=lambda x: x.get('days_old', 0), reverse=True)
    
    def get_orphaned_vmdks(self):
        """
        Liefert Demo-Daten für verwaiste VMDK-Dateien
        
        Returns:
            list: Liste von Demo-Orphaned-VMDK-Infos
        """
        result = []
        
        # Typische Datastore-Namen
        datastores = ['ds01_ssd', 'ds02_ssd', 'ds03_sas', 'ds04_sas', 'ds05_archive']
        
        # Typische VM-Präfixe
        vm_prefixes = ['srv', 'app', 'db', 'web', 'dev', 'test', 'prod']
        
        # Generiere 6 Demo-Orphaned-VMDKs
        for i in range(6):
            # Wähle einen Datastore
            datastore = random.choice(datastores)
            
            # Generiere einen VMDK-Namen
            prefix = random.choice(vm_prefixes)
            num = random.randint(1, 999)
            vm_name = f"{prefix}{num:03d}"
            
            disk_num = random.randint(1, 4)
            vmdk_name = f"{vm_name}_disk{disk_num}.vmdk"
            
            # Generiere Alter und Größe
            days_old = random.randint(30, 365)
            creation_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d')
            size_gb = random.randint(10, 200)
            
            # Bestimme Status-Klasse basierend auf dem Alter
            status_class = "ok"
            if days_old > 90:
                status_class = "critical"
            elif days_old > 30:
                status_class = "warning"
            
            result.append({
                'name': vmdk_name,
                'path': f"[{datastore}] {vm_name}/",
                'datastore': datastore,
                'size_gb': size_gb,
                'creation_date': creation_date,
                'days_old': days_old,
                'status_class': status_class
            })
        
        # Sortieren nach Alter (älteste zuerst)
        return sorted(result, key=lambda x: x.get('days_old', 0), reverse=True)

def get_demo_client():
    """
    Erstellt einen Demo-VSphereClient
    
    Returns:
        DemoVSphereClient: Client mit Demo-Daten
    """
    return DemoVSphereClient()