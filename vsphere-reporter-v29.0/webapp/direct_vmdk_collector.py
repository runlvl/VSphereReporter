#!/usr/bin/env python3
"""
DirectVMDKCollector Module for VMware vSphere Reporter Web Edition
Specialized module for collecting and analyzing VMDK files
"""

import logging
import re
from pyVmomi import vim

# Configure logger
logger = logging.getLogger(__name__)

class DirectVMDKCollector:
    """Collector for VMDK file information with enhanced orphaned VMDK detection"""
    
    def __init__(self, vsphere_client):
        """
        Initialize the VMDK collector
        
        Args:
            vsphere_client: Connected VSphereClient instance
        """
        self.client = vsphere_client
        self.logger = logging.getLogger(__name__)
    
    def collect_all_vmdks(self):
        """
        Collect information about all VMDK files in the environment
        
        Returns:
            list: List of VMDK information dictionaries with improved status detection
        """
        if not self.client.is_connected():
            raise Exception("Not connected to vCenter Server")
        
        self.logger.info("Collecting VMDK file information")
        
        # Step 1: Get all datastores
        datastores = self.client.get_all_datastores()
        
        # Step 2: Get all virtual machines with their disk information
        vms = self.client.get_all_vms()
        
        # Step 3: Create a mapping of known VM disks for faster lookup
        vm_disks = self._get_vm_disk_map(vms)
        
        # Step 4: Collect all VMDKs from datastores
        all_vmdks = []
        for ds in datastores:
            try:
                # Skip datastores that are not accessible
                if not ds.summary.accessible:
                    self.logger.warning(f"Skipping inaccessible datastore: {ds.name}")
                    continue
                
                # Browse datastore
                datastore_browser = ds.browser
                datastorepath = f"[{ds.name}]"
                
                # Search for VMDKs
                search_spec = vim.HostDatastoreBrowserSearchSpec()
                search_spec.matchPattern = ["*.vmdk"]
                
                # Execute search
                task = datastore_browser.SearchDatastoreSubFolders_Task(datastorePath=datastorepath, searchSpec=search_spec)
                self.client.wait_for_task(task)
                
                # Process search results
                for result in task.info.result:
                    for file_info in result.file:
                        file_path = f"{result.folderPath}{file_info.path}"
                        
                        # Skip -flat, -delta, and -ctk files as they are helper files
                        if re.search(r'-(flat|delta|ctk|rdm|rdmp)\.vmdk$', file_info.path):
                            all_vmdks.append({
                                'path': file_path,
                                'datastore': ds.name,
                                'filename': file_info.path,
                                'size_kb': file_info.fileSize / 1024 if hasattr(file_info, 'fileSize') else 0,
                                'status': 'HELPER',
                                'is_template': False,
                                'vm_name': None,
                                'is_orphaned': False
                            })
                            continue
                        
                        # Check if this VMDK is attached to a VM
                        vmdk_status = self._determine_vmdk_status(file_path, vm_disks)
                        
                        # Status will be one of: 'AKTIV', 'TEMPLATE', 'POTENTIALLY ORPHANED'
                        all_vmdks.append({
                            'path': file_path,
                            'datastore': ds.name,
                            'filename': file_info.path,
                            'size_kb': file_info.fileSize / 1024 if hasattr(file_info, 'fileSize') else 0,
                            'status': vmdk_status['status'],
                            'is_template': vmdk_status['is_template'],
                            'vm_name': vmdk_status['vm_name'],
                            'is_orphaned': vmdk_status['status'] == 'POTENTIALLY ORPHANED'
                        })
            
            except Exception as e:
                self.logger.error(f"Error processing datastore {ds.name}: {str(e)}")
        
        # Sort by status (POTENTIALLY ORPHANED first) and then by size (largest first)
        all_vmdks.sort(key=lambda x: (0 if x['status'] == 'POTENTIALLY ORPHANED' else 
                                      1 if x['status'] == 'AKTIV' else 
                                      2 if x['status'] == 'TEMPLATE' else 3, 
                                      -x['size_kb']))
        
        self.logger.info(f"Collected information for {len(all_vmdks)} VMDK files")
        return all_vmdks
    
    def collect_orphaned_vmdks(self):
        """
        Collect information about potentially orphaned VMDK files
        
        Returns:
            list: List of potentially orphaned VMDK information dictionaries
        """
        all_vmdks = self.collect_all_vmdks()
        return [vmdk for vmdk in all_vmdks if vmdk['status'] == 'POTENTIALLY ORPHANED']
    
    def _get_vm_disk_map(self, vms):
        """
        Create a mapping of known VM disks for faster lookup
        
        Args:
            vms: List of VirtualMachine objects
            
        Returns:
            dict: Mapping of disk paths to VM information
        """
        disk_map = {}
        
        for vm in vms:
            try:
                is_template = vm.config.template
                
                # Get all disks for this VM
                for device in vm.config.hardware.device:
                    if isinstance(device, vim.vm.device.VirtualDisk):
                        if hasattr(device.backing, 'fileName'):
                            disk_path = device.backing.fileName
                            
                            # Store multiple versions of the path for more robust matching
                            disk_map[disk_path] = {
                                'vm_name': vm.name,
                                'is_template': is_template
                            }
                            
                            # Also store path without datastore prefix
                            if '] ' in disk_path:
                                simple_path = disk_path.split('] ', 1)[1]
                                disk_map[simple_path] = {
                                    'vm_name': vm.name,
                                    'is_template': is_template
                                }
                            
                            # Also store just the filename
                            filename = disk_path.split('/')[-1]
                            disk_map[filename] = {
                                'vm_name': vm.name,
                                'is_template': is_template
                            }
            
            except Exception as e:
                self.logger.warning(f"Error processing VM {vm.name}: {str(e)}")
        
        return disk_map
    
    def _determine_vmdk_status(self, vmdk_path, vm_disk_map):
        """
        Determine the status of a VMDK file
        
        Args:
            vmdk_path: Path to the VMDK file
            vm_disk_map: Mapping of known VM disks
            
        Returns:
            dict: Status information including status, is_template, and vm_name
        """
        result = {
            'status': 'POTENTIALLY ORPHANED',
            'is_template': False,
            'vm_name': None
        }
        
        # Check if this exact path is in the map
        if vmdk_path in vm_disk_map:
            result['vm_name'] = vm_disk_map[vmdk_path]['vm_name']
            result['is_template'] = vm_disk_map[vmdk_path]['is_template']
            result['status'] = 'TEMPLATE' if result['is_template'] else 'AKTIV'
            return result
        
        # Check path without datastore prefix
        if '] ' in vmdk_path:
            simple_path = vmdk_path.split('] ', 1)[1]
            if simple_path in vm_disk_map:
                result['vm_name'] = vm_disk_map[simple_path]['vm_name']
                result['is_template'] = vm_disk_map[simple_path]['is_template']
                result['status'] = 'TEMPLATE' if result['is_template'] else 'AKTIV'
                return result
        
        # Check just the filename
        filename = vmdk_path.split('/')[-1]
        if filename in vm_disk_map:
            result['vm_name'] = vm_disk_map[filename]['vm_name']
            result['is_template'] = vm_disk_map[filename]['is_template']
            result['status'] = 'TEMPLATE' if result['is_template'] else 'AKTIV'
            return result
        
        # Try case-insensitive matching for additional robustness
        for path in vm_disk_map:
            if vmdk_path.lower() == path.lower():
                result['vm_name'] = vm_disk_map[path]['vm_name']
                result['is_template'] = vm_disk_map[path]['is_template']
                result['status'] = 'TEMPLATE' if result['is_template'] else 'AKTIV'
                return result
        
        # If we get here, the VMDK is potentially orphaned
        return result