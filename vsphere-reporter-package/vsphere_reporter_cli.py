#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Command Line Interface
A comprehensive reporting tool for VMware vSphere environments

This is the CLI version for Linux environments where GUI may not be available.
"""

import sys
import os
import logging
import argparse
import getpass
from utils.logger import setup_logger
from core.vsphere_client import VSphereClient
from core.data_collector import DataCollector
from core.report_generator import ReportGenerator

def main():
    """Main entry point for the CLI application"""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting VMware vSphere Reporter CLI")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='VMware vSphere Reporter CLI')
    parser.add_argument('--server', '-s', required=True, help='vCenter server address')
    parser.add_argument('--username', '-u', required=True, help='vCenter username')
    parser.add_argument('--password', '-p', help='vCenter password (omit for secure prompt)')
    parser.add_argument('--ignore-ssl', '-k', action='store_true', help='Ignore SSL certificate validation')
    parser.add_argument('--output-dir', '-o', default=os.getcwd(), help='Output directory for reports')
    parser.add_argument('--format', '-f', choices=['html', 'docx', 'pdf', 'all'], default='all', 
                        help='Report format (html, docx, pdf, or all)')
    parser.add_argument('--include-all', '-a', action='store_true', 
                        help='Include all optional sections in the report')
    
    # Optional report sections
    parser.add_argument('--vms', action='store_true', help='Include virtual machines section')
    parser.add_argument('--hosts', action='store_true', help='Include hosts section')
    parser.add_argument('--datastores', action='store_true', help='Include datastores section')
    parser.add_argument('--clusters', action='store_true', help='Include clusters section')
    parser.add_argument('--resource-pools', action='store_true', help='Include resource pools section')
    parser.add_argument('--networks', action='store_true', help='Include networks section')
    
    args = parser.parse_args()
    
    # Get password if not provided
    password = args.password
    if not password:
        password = getpass.getpass(f"Enter password for {args.username}@{args.server}: ")
    
    try:
        # Connect to vCenter
        print(f"Connecting to vCenter server: {args.server}")
        client = VSphereClient(args.server, args.username, password, args.ignore_ssl)
        client.connect()
        print("Connected successfully")
        
        # Initialize data collector
        collector = DataCollector(client)
        
        # Collect data with progress indication
        print("\nCollecting data from vCenter (this may take a while)...")
        data = {}
        
        # Required sections
        print("- Collecting VMware Tools information...")
        data['vmware_tools'] = collector.collect_vmware_tools_info()
        
        print("- Collecting snapshot information...")
        data['snapshots'] = collector.collect_snapshot_info()
        
        print("- Collecting orphaned VMDK information...")
        data['orphaned_vmdks'] = collector.collect_orphaned_vmdks()
        
        # Optional sections
        if args.include_all or args.vms:
            print("- Collecting VM information...")
            data['vms'] = collector.collect_vm_info()
            
        if args.include_all or args.hosts:
            print("- Collecting host information...")
            data['hosts'] = collector.collect_host_info()
            
        if args.include_all or args.datastores:
            print("- Collecting datastore information...")
            data['datastores'] = collector.collect_datastore_info()
            
        if args.include_all or args.clusters:
            print("- Collecting cluster information...")
            data['clusters'] = collector.collect_cluster_info()
            
        if args.include_all or args.resource_pools:
            print("- Collecting resource pool information...")
            data['resource_pools'] = collector.collect_resource_pool_info()
            
        if args.include_all or args.networks:
            print("- Collecting network information...")
            data['networks'] = collector.collect_network_info()
        
        # Generate reports
        print("\nGenerating reports...")
        report_generator = ReportGenerator(data)
        output_files = []
        
        if args.format == 'html' or args.format == 'all':
            print("- Generating HTML report...")
            html_file = report_generator.export_to_html(args.output_dir)
            output_files.append(html_file)
            
        if args.format == 'docx' or args.format == 'all':
            print("- Generating DOCX report...")
            docx_file = report_generator.export_to_docx(args.output_dir)
            output_files.append(docx_file)
            
        if args.format == 'pdf' or args.format == 'all':
            print("- Generating PDF report...")
            pdf_file = report_generator.export_to_pdf(args.output_dir)
            output_files.append(pdf_file)
        
        # Disconnect from vCenter
        client.disconnect()
        
        # Show success message
        print("\nReport generation completed successfully!")
        print("Report files:")
        for file in output_files:
            print(f"- {file}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())