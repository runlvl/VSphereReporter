"""
Bechtle vSphere Reporter - History Manager

Verwaltet das Speichern und Laden historischer Berichte für Vergleichsanalysen.
Ermöglicht das Tracking von Änderungen in der vSphere-Umgebung über Zeit.
"""

import os
import json
import logging
from datetime import datetime
import hashlib

logger = logging.getLogger('vsphere_reporter')

class HistoryManager:
    """Manager für historische Berichte und Vergleichsfunktionalität"""
    
    def __init__(self, base_dir=None):
        """
        Initialisiert den History Manager
        
        Args:
            base_dir: Basisverzeichnis für die Speicherung historischer Berichte
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports', 'history')
        
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"Historische Berichte werden in {self.base_dir} gespeichert")
    
    def save_report(self, report_data, report_type, server_name, description=None):
        """
        Speichert einen Bericht für spätere Vergleiche
        
        Args:
            report_data: Die zu speichernden Berichtsdaten
            report_type: Typ des Berichts (vmware_tools, snapshots, orphaned_vmdks)
            server_name: Name des vCenter-Servers
            description: Optionale Beschreibung des Berichts
            
        Returns:
            dict: Metadaten des gespeicherten Berichts
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Erstelle sicheren Dateinamen mit Server und Zeitstempel
        safe_server_name = "".join(c if c.isalnum() else "_" for c in server_name)
        filename = f"{safe_server_name}_{report_type}_{date_str}.json"
        
        # Erstelle Unterverzeichnis für den Berichtstyp
        report_dir = os.path.join(self.base_dir, report_type)
        os.makedirs(report_dir, exist_ok=True)
        
        # Speichere Metadaten mit dem Bericht
        metadata = {
            "timestamp": timestamp.isoformat(),
            "server": server_name,
            "report_type": report_type,
            "description": description or f"Automatisch gespeicherter {report_type}-Bericht",
            "item_count": len(report_data) if isinstance(report_data, list) else 0,
            "filename": filename
        }
        
        # Erstelle komplettes Speicherobjekt
        storage_obj = {
            "metadata": metadata,
            "data": report_data
        }
        
        # Speichere den Bericht als JSON
        filepath = os.path.join(report_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(storage_obj, f, indent=2, ensure_ascii=False)
            logger.info(f"Bericht erfolgreich gespeichert: {filepath}")
            return metadata
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Berichts {filepath}: {str(e)}")
            return None
    
    def get_report_history(self, report_type=None, server_name=None, limit=10):
        """
        Ruft die Berichtshistorie ab, optional gefiltert nach Typ und Server
        
        Args:
            report_type: Optional, filtert nach Berichtstyp
            server_name: Optional, filtert nach Server
            limit: Maximale Anzahl von Berichten, die zurückgegeben werden
            
        Returns:
            list: Liste von Berichtsmetadaten, sortiert nach Datum (neueste zuerst)
        """
        reports = []
        
        # Wenn ein bestimmter Berichtstyp angegeben wurde, nur in diesem Verzeichnis suchen
        if report_type:
            report_dirs = [os.path.join(self.base_dir, report_type)]
        else:
            # Andernfalls in allen Berichtstypen suchen
            try:
                report_dirs = [os.path.join(self.base_dir, d) for d in os.listdir(self.base_dir) 
                              if os.path.isdir(os.path.join(self.base_dir, d))]
            except FileNotFoundError:
                return []
        
        # Durchsuche alle relevanten Verzeichnisse
        for report_dir in report_dirs:
            if not os.path.exists(report_dir):
                continue
                
            for filename in os.listdir(report_dir):
                if not filename.endswith('.json'):
                    continue
                    
                filepath = os.path.join(report_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        
                    if not isinstance(report, dict) or 'metadata' not in report:
                        continue
                        
                    metadata = report['metadata']
                    
                    # Filtere nach Server, falls angegeben
                    if server_name and metadata.get('server') != server_name:
                        continue
                        
                    # Füge vollständigen Pfad hinzu für späteren Zugriff
                    metadata['filepath'] = filepath
                    reports.append(metadata)
                    
                except Exception as e:
                    logger.error(f"Fehler beim Laden des Berichts {filepath}: {str(e)}")
        
        # Sortiere nach Zeitstempel, neueste zuerst
        reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Begrenze die Anzahl der Ergebnisse
        return reports[:limit] if limit else reports
    
    def load_report(self, report_id=None, filepath=None):
        """
        Lädt einen Bericht basierend auf ID oder Dateipfad
        
        Args:
            report_id: ID des Berichts (Dateiname ohne Erweiterung)
            filepath: Direkter Pfad zur Berichtsdatei
            
        Returns:
            dict: Der vollständige Bericht mit Metadaten und Daten
        """
        if not filepath and report_id:
            # Suche die Datei basierend auf der ID
            for root, _, files in os.walk(self.base_dir):
                for filename in files:
                    if filename.startswith(report_id) and filename.endswith('.json'):
                        filepath = os.path.join(root, filename)
                        break
        
        if not filepath:
            logger.error(f"Bericht mit ID {report_id} wurde nicht gefunden")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                report = json.load(f)
            logger.info(f"Bericht erfolgreich geladen: {filepath}")
            return report
        except Exception as e:
            logger.error(f"Fehler beim Laden des Berichts {filepath}: {str(e)}")
            return None
    
    def compare_reports(self, current_data, historical_data, report_type):
        """
        Vergleicht aktuelle Daten mit einem historischen Bericht
        
        Args:
            current_data: Aktuelle Berichtsdaten
            historical_data: Historische Berichtsdaten zum Vergleich
            report_type: Typ des Berichts (bestimmt die Vergleichslogik)
            
        Returns:
            dict: Vergleichsergebnisse mit Statistiken und detaillierten Änderungen
        """
        if not current_data or not historical_data:
            return {"error": "Keine Daten für Vergleich verfügbar"}
            
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "report_type": report_type,
            "summary": {},
            "changes": {
                "added": [],
                "removed": [],
                "changed": []
            }
        }
        
        # Wähle die passende Vergleichsmethode basierend auf dem Berichtstyp
        if report_type == "vmware_tools":
            self._compare_vmware_tools(current_data, historical_data, comparison)
        elif report_type == "snapshots":
            self._compare_snapshots(current_data, historical_data, comparison)
        elif report_type == "orphaned_vmdks":
            self._compare_orphaned_vmdks(current_data, historical_data, comparison)
        else:
            return {"error": f"Unbekannter Berichtstyp: {report_type}"}
            
        return comparison
    
    def _compare_vmware_tools(self, current_data, historical_data, comparison):
        """
        Vergleicht VMware Tools-Statusberichte
        
        Args:
            current_data: Aktuelle VMware Tools-Daten
            historical_data: Historische VMware Tools-Daten
            comparison: Vergleichsobjekt zum Befüllen
        """
        # Umwandeln der Listen in Dictionaries mit VM-Namen als Schlüssel für schnelleren Vergleich
        current_dict = {item['vm_name']: item for item in current_data}
        historical_dict = {item['vm_name']: item for item in historical_data}
        
        # Identifiziere hinzugefügte, entfernte und geänderte VMs
        current_vms = set(current_dict.keys())
        historical_vms = set(historical_dict.keys())
        
        added_vms = current_vms - historical_vms
        removed_vms = historical_vms - current_vms
        common_vms = current_vms.intersection(historical_vms)
        
        # Füge hinzugefügte VMs zur Ergebnisliste hinzu
        for vm_name in added_vms:
            comparison["changes"]["added"].append({
                "vm_name": vm_name,
                "current": current_dict[vm_name]
            })
        
        # Füge entfernte VMs zur Ergebnisliste hinzu
        for vm_name in removed_vms:
            comparison["changes"]["removed"].append({
                "vm_name": vm_name,
                "historical": historical_dict[vm_name]
            })
        
        # Prüfe auf Änderungen bei bestehenden VMs
        for vm_name in common_vms:
            current = current_dict[vm_name]
            historical = historical_dict[vm_name]
            
            # Prüfe auf relevante Änderungen
            if (current.get('tools_version') != historical.get('tools_version') or
                current.get('tools_status') != historical.get('tools_status')):
                
                comparison["changes"]["changed"].append({
                    "vm_name": vm_name,
                    "current": current,
                    "historical": historical,
                    "changes": {
                        "tools_version": {
                            "from": historical.get('tools_version'),
                            "to": current.get('tools_version')
                        },
                        "tools_status": {
                            "from": historical.get('tools_status'),
                            "to": current.get('tools_status')
                        }
                    }
                })
        
        # Erstelle Zusammenfassung
        comparison["summary"] = {
            "total_current": len(current_vms),
            "total_historical": len(historical_vms),
            "added": len(added_vms),
            "removed": len(removed_vms),
            "changed": len(comparison["changes"]["changed"]),
            "unchanged": len(common_vms) - len(comparison["changes"]["changed"])
        }
    
    def _compare_snapshots(self, current_data, historical_data, comparison):
        """
        Vergleicht Snapshot-Berichte
        
        Args:
            current_data: Aktuelle Snapshot-Daten
            historical_data: Historische Snapshot-Daten
            comparison: Vergleichsobjekt zum Befüllen
        """
        # Erstelle eindeutige IDs für jeden Snapshot basierend auf VM-Name und Snapshot-Name
        def create_snapshot_id(snapshot):
            return f"{snapshot['vm_name']}:{snapshot['name']}:{snapshot.get('creation_time', '')}"
        
        # Umwandeln der Listen in Dictionaries mit Snapshot-IDs als Schlüssel
        current_dict = {create_snapshot_id(item): item for item in current_data}
        historical_dict = {create_snapshot_id(item): item for item in historical_data}
        
        # Identifiziere hinzugefügte, entfernte und gemeinsame Snapshots
        current_ids = set(current_dict.keys())
        historical_ids = set(historical_dict.keys())
        
        added_ids = current_ids - historical_ids
        removed_ids = historical_ids - current_ids
        
        # Füge neue Snapshots hinzu
        for snapshot_id in added_ids:
            comparison["changes"]["added"].append({
                "snapshot_id": snapshot_id,
                "current": current_dict[snapshot_id]
            })
        
        # Füge entfernte Snapshots hinzu
        for snapshot_id in removed_ids:
            comparison["changes"]["removed"].append({
                "snapshot_id": snapshot_id,
                "historical": historical_dict[snapshot_id]
            })
        
        # Bei Snapshots sind Änderungen weniger relevant, da sie typischerweise entweder
        # neu erstellt oder gelöscht werden, aber selten "geändert" im eigentlichen Sinne
        
        # Erstelle Zusammenfassung
        comparison["summary"] = {
            "total_current": len(current_ids),
            "total_historical": len(historical_ids),
            "added": len(added_ids),
            "removed": len(removed_ids),
            "changed": 0,  # Bei Snapshots nicht relevant
            "unchanged": len(current_ids.intersection(historical_ids))
        }
    
    def _compare_orphaned_vmdks(self, current_data, historical_data, comparison):
        """
        Vergleicht Berichte über verwaiste VMDK-Dateien
        
        Args:
            current_data: Aktuelle VMDK-Daten
            historical_data: Historische VMDK-Daten
            comparison: Vergleichsobjekt zum Befüllen
        """
        # Erstelle eindeutige IDs für jede VMDK-Datei basierend auf Pfad
        def create_vmdk_id(vmdk):
            # Verwende den vollständigen Pfad als eindeutige ID
            return vmdk.get('path', '') + vmdk.get('name', '')
        
        # Umwandeln der Listen in Dictionaries mit VMDK-IDs als Schlüssel
        current_dict = {create_vmdk_id(item): item for item in current_data}
        historical_dict = {create_vmdk_id(item): item for item in historical_data}
        
        # Identifiziere hinzugefügte, entfernte und gemeinsame VMDKs
        current_ids = set(current_dict.keys())
        historical_ids = set(historical_dict.keys())
        
        added_ids = current_ids - historical_ids
        removed_ids = historical_ids - current_ids
        common_ids = current_ids.intersection(historical_ids)
        
        # Füge neue VMDKs hinzu
        for vmdk_id in added_ids:
            comparison["changes"]["added"].append({
                "vmdk_id": vmdk_id,
                "current": current_dict[vmdk_id]
            })
        
        # Füge entfernte VMDKs hinzu
        for vmdk_id in removed_ids:
            comparison["changes"]["removed"].append({
                "vmdk_id": vmdk_id,
                "historical": historical_dict[vmdk_id]
            })
        
        # Prüfe auf Änderungen bei bestehenden VMDKs
        for vmdk_id in common_ids:
            current = current_dict[vmdk_id]
            historical = historical_dict[vmdk_id]
            
            # Prüfe auf relevante Änderungen (z.B. Größe)
            if current.get('size_gb') != historical.get('size_gb'):
                comparison["changes"]["changed"].append({
                    "vmdk_id": vmdk_id,
                    "current": current,
                    "historical": historical,
                    "changes": {
                        "size_gb": {
                            "from": historical.get('size_gb'),
                            "to": current.get('size_gb')
                        }
                    }
                })
        
        # Erstelle Zusammenfassung
        comparison["summary"] = {
            "total_current": len(current_ids),
            "total_historical": len(historical_ids),
            "added": len(added_ids),
            "removed": len(removed_ids),
            "changed": len(comparison["changes"]["changed"]),
            "unchanged": len(common_ids) - len(comparison["changes"]["changed"])
        }