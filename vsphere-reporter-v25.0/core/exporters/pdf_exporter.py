#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF report exporter
"""

import os
import logging
import datetime
import humanize
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, ListFlowable, ListItem
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
from reportlab.platypus.frames import Frame
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

class PDFExporter:
    """Exporter for PDF reports"""
    
    def __init__(self, data, timestamp):
        """
        Initialize the PDF exporter
        
        Args:
            data (dict): Dictionary containing collected vSphere data
            timestamp (datetime): Report generation timestamp
        """
        self.data = data
        self.timestamp = timestamp
        self.styles = getSampleStyleSheet()
        
        # Add custom styles
        self._add_custom_styles()
        
    def export(self, output_path):
        """
        Export data to PDF file
        
        Args:
            output_path (str): Path to save the PDF file
            
        Returns:
            bool: True if export was successful
        """
        try:
            # Create PDF document
            document = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Create content elements
            elements = []
            
            # Add title page
            self._add_title_page(elements)
            
            # Add table of contents
            self._add_table_of_contents(elements)
            
            # Add executive summary
            self._add_executive_summary(elements)
            
            # Add report sections
            self._add_report_sections(elements)
            
            # Build the document
            document.build(elements)
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to PDF: {str(e)}")
            raise
            
    def _add_custom_styles(self):
        """Add custom styles to the document"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Title'],
            fontSize=24,
            leading=28,
            alignment=1,  # Center
            spaceAfter=24
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            leading=16,
            alignment=1,  # Center
            spaceAfter=12
        ))
        
        # Heading1 style
        self.styles.add(ParagraphStyle(
            name='Heading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            leading=22,
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # Heading2 style
        self.styles.add(ParagraphStyle(
            name='Heading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            leading=20,
            spaceBefore=10,
            spaceAfter=4
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=1,  # Center
            spaceAfter=6
        ))
        
        # Table Header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            fontName='Helvetica-Bold'
        ))
        
        # Recommendation style
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
            spaceBefore=6,
            spaceAfter=6,
            backColor=colors.lightgrey,
            borderPadding=5
        ))
        
    def _add_title_page(self, elements):
        """Add title page to document"""
        # Title
        elements.append(Paragraph("VMware vSphere Environment Report", self.styles['Title']))
        
        # Subtitle
        elements.append(Paragraph(
            f"Generated on: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Subtitle']
        ))
        
        # Add page break
        elements.append(PageBreak())
        
    def _add_table_of_contents(self, elements):
        """Add table of contents to document"""
        elements.append(Paragraph("Table of Contents", self.styles['Heading1']))
        
        # Create and add TOC
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(name='TOCHeading1', fontSize=12, leading=16, leftIndent=20),
            ParagraphStyle(name='TOCHeading2', fontSize=10, leading=14, leftIndent=40)
        ]
        elements.append(toc)
        
        # Add page break
        elements.append(PageBreak())
        
    def _add_executive_summary(self, elements):
        """Add executive summary to document"""
        elements.append(Paragraph("Executive Summary", self.styles['Heading1']))
        
        elements.append(Paragraph(
            "This report contains information about the VMware vSphere environment. "
            "It includes details about VMware Tools versions, VM snapshots, orphaned VMDK files, "
            "and other important aspects of the environment.",
            self.styles['Normal']
        ))
        
        # Add summary statistics
        elements.append(Paragraph("Summary Statistics", self.styles['Heading2']))
        
        # Create statistics table
        data = [["Item", "Count"]]
        
        # Add data rows
        data.extend([
            ["VMware Tools versions needing upgrade", self._count_tools_needing_upgrade()],
            ["VMs with snapshots", self._count_vms_with_snapshots()],
            ["Orphaned VMDK files", self._count_orphaned_vmdks()],
            ["Total virtual machines", self._count_total_vms()],
            ["Total ESXi hosts", self._count_total_hosts()],
            ["Total datastores", self._count_total_datastores()]
        ])
        
        # Create table
        table = Table(data, colWidths=[4*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
        # Add page break
        elements.append(PageBreak())
        
    def _add_report_sections(self, elements):
        """Add report sections to document"""
        # VMware Tools section (required)
        if 'vmware_tools' in self.data:
            self._add_vmware_tools_section(elements)
            
        # Snapshots section (required)
        if 'snapshots' in self.data:
            self._add_snapshots_section(elements)
            
        # Orphaned VMDKs section (required)
        if 'orphaned_vmdks' in self.data:
            self._add_orphaned_vmdks_section(elements)
            
        # Additional sections
        if 'vms' in self.data:
            self._add_vms_section(elements)
            
        if 'hosts' in self.data:
            self._add_hosts_section(elements)
            
        if 'datastores' in self.data:
            self._add_datastores_section(elements)
            
        if 'clusters' in self.data:
            self._add_clusters_section(elements)
            
        if 'resource_pools' in self.data:
            self._add_resource_pools_section(elements)
            
        if 'networks' in self.data:
            self._add_networks_section(elements)
            
    def _add_vmware_tools_section(self, elements):
        """Add VMware Tools section to document"""
        elements.append(Paragraph("VMware Tools Versions", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows VMware Tools versions for all virtual machines, "
            "ordered by oldest version first.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [["VM Name", "Power State", "Tools Status", "Tools Version"]]
        
        # Add data rows
        for vm in self.data['vmware_tools']:
            data.append([
                vm['name'],
                vm['power_state'],
                vm['vmware_tools_status'],
                vm['vmware_tools_version']
            ])
        
        # Create table
        table = Table(data, colWidths=[2.5*inch, 1.25*inch, 1.75*inch, 1.75*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
        # Add recommendation paragraph if needed
        if self._count_tools_needing_upgrade() > 0:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                f"<b>Recommendation:</b> There are {self._count_tools_needing_upgrade()} virtual machines with outdated VMware Tools. "
                "It is recommended to update VMware Tools to the latest version to ensure optimal performance and compatibility.",
                self.styles['Recommendation']
            ))
            
        # Add page break
        elements.append(PageBreak())
        
    def _add_snapshots_section(self, elements):
        """Add Snapshots section to document"""
        elements.append(Paragraph("VM Snapshots", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows virtual machine snapshots, ordered by oldest first. "
            "Snapshots are not intended for long-term use and can impact performance if kept for extended periods.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        if not self.data['snapshots']:
            elements.append(Paragraph("No snapshots found in the environment.", self.styles['Normal']))
        else:
            # Create table data
            data = [["VM Name", "Snapshot Name", "Description", "Create Time", "Age (Days)"]]
            
            # Add data rows
            for snapshot in self.data['snapshots']:
                # Format create time
                create_time = self._format_datetime(snapshot['create_time'])
                
                data.append([
                    snapshot['vm_name'],
                    snapshot['name'],
                    snapshot['description'],
                    create_time,
                    str(snapshot['age_days'])
                ])
            
            # Create table
            table = Table(data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch, 0.75*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (4, 1), (4, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
            ]))
            
            elements.append(table)
            
            # Add recommendation paragraph
            old_snapshots = [s for s in self.data['snapshots'] if s['age_days'] > 7]
            if old_snapshots:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(
                    f"<b>Recommendation:</b> There are {len(old_snapshots)} snapshots older than 7 days. "
                    "It is recommended to consolidate or remove old snapshots to maintain optimal performance.",
                    self.styles['Recommendation']
                ))
                
        # Add page break
        elements.append(PageBreak())
        
    def _add_orphaned_vmdks_section(self, elements):
        """Add Orphaned VMDKs section to document"""
        elements.append(Paragraph("Orphaned VMDK Files", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows VMDK files that appear to be orphaned or not associated with any registered virtual machine. "
            "These files may be consuming unnecessary storage space.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        if not self.data['orphaned_vmdks']:
            elements.append(Paragraph("No orphaned VMDK files found in the environment.", self.styles['Normal']))
        else:
            # Create table data
            data = [["Path", "Datastore", "Size", "Reason"]]
            
            # Add data rows
            for vmdk in self.data['orphaned_vmdks']:
                data.append([
                    vmdk['path'],
                    vmdk['datastore'],
                    self._format_size(vmdk['size']),
                    vmdk['reason']
                ])
            
            # Create table
            table = Table(data, colWidths=[3*inch, 1*inch, 1*inch, 2.25*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
            ]))
            
            elements.append(table)
            
            # Add recommendation paragraph
            if self.data['orphaned_vmdks']:
                total_size = sum(vmdk['size'] for vmdk in self.data['orphaned_vmdks'])
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph(
                    f"<b>Recommendation:</b> There are {len(self.data['orphaned_vmdks'])} orphaned VMDK files consuming approximately {self._format_size(total_size)} of storage. "
                    "It is recommended to verify and remove these files to reclaim storage space.",
                    self.styles['Recommendation']
                ))
                
        # Add page break
        elements.append(PageBreak())
        
    def _add_vms_section(self, elements):
        """Add VMs section to document"""
        elements.append(Paragraph("Virtual Machines", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows an overview of all virtual machines in the environment.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [["VM Name", "Power State", "Guest OS", "CPU", "Memory (MB)", "Used Space"]]
        
        # Add data rows
        for vm in self.data['vms']:
            data.append([
                vm['name'],
                vm['power_state'],
                vm['guest_full_name'],
                str(vm['num_cpu']),
                str(vm['memory_mb']),
                self._format_size(vm['used_space'])
            ])
        
        # Create table
        table = Table(data, colWidths=[1.75*inch, 1*inch, 2*inch, 0.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (3, 1), (4, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
        # Add page break
        elements.append(PageBreak())
        
    def _add_hosts_section(self, elements):
        """Add Hosts section to document"""
        elements.append(Paragraph("ESXi Hosts", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows an overview of all ESXi hosts in the environment.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [["Host Name", "Cluster", "Connection State", "CPU Model", "CPU Cores", "Memory (GB)"]]
        
        # Add data rows
        for host in self.data['hosts']:
            data.append([
                host['name'],
                host['cluster'],
                host['connection_state'],
                host['cpu_model'],
                str(host['cpu_cores']),
                str(round(host['memory_size'], 2))
            ])
        
        # Create table
        table = Table(data, colWidths=[1.75*inch, 1*inch, 1*inch, 2.25*inch, 0.75*inch, 0.75*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (4, 1), (5, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
        # Add page break
        elements.append(PageBreak())
        
    def _add_datastores_section(self, elements):
        """Add Datastores section to document"""
        elements.append(Paragraph("Datastores", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows an overview of all datastores in the environment.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [["Datastore Name", "Type", "Capacity", "Free Space", "Usage (%)"]]
        
        # Add data rows
        for datastore in self.data['datastores']:
            data.append([
                datastore['name'],
                datastore['type'],
                self._format_size(datastore['capacity']),
                self._format_size(datastore['free_space']),
                self._format_percent(datastore['usage_percent'])
            ])
        
        # Create table
        table = Table(data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (2, 1), (4, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
        # Add recommendation paragraph
        high_usage_datastores = [ds for ds in self.data['datastores'] if ds['usage_percent'] > 85]
        if high_usage_datastores:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                f"<b>Recommendation:</b> There are {len(high_usage_datastores)} datastores with usage above 85%. "
                "Consider adding more storage capacity or migrating VMs to balance usage.",
                self.styles['Recommendation']
            ))
            
        # Add page break
        elements.append(PageBreak())
        
    def _add_clusters_section(self, elements):
        """Add Clusters section to document"""
        elements.append(Paragraph("Clusters", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows an overview of all clusters in the environment.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [["Cluster Name", "Hosts", "DRS Enabled", "HA Enabled", "Total Memory (GB)"]]
        
        # Add data rows
        for cluster in self.data['clusters']:
            data.append([
                cluster['name'],
                str(cluster['hosts']),
                str(cluster['drs_enabled']),
                str(cluster['ha_enabled']),
                str(round(cluster['total_memory'] / (1024 * 1024 * 1024), 2)) if cluster['total_memory'] else "0"
            ])
        
        # Create table
        table = Table(data, colWidths=[2.5*inch, 0.75*inch, 1*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (4, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
        # Add page break
        elements.append(PageBreak())
        
    def _add_resource_pools_section(self, elements):
        """Add Resource Pools section to document"""
        elements.append(Paragraph("Resource Pools", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows an overview of all resource pools in the environment.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [["Resource Pool Name", "Parent", "CPU Shares", "CPU Limit", "Memory Limit"]]
        
        # Add data rows
        for pool in self.data['resource_pools']:
            data.append([
                pool['name'],
                f"{pool['parent_type']}: {pool['parent_name']}",
                str(pool['cpu_shares']),
                str(pool['cpu_limit']) if pool['cpu_limit'] != -1 else "Unlimited",
                str(pool['memory_limit']) if pool['memory_limit'] != -1 else "Unlimited"
            ])
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 1*inch, 1.25*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (2, 1), (4, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
        # Add page break
        elements.append(PageBreak())
        
    def _add_networks_section(self, elements):
        """Add Networks section to document"""
        elements.append(Paragraph("Networks", self.styles['Heading1']))
        
        # Add description
        elements.append(Paragraph(
            "The following table shows an overview of all networks in the environment.",
            self.styles['Normal']
        ))
        
        # Add spacer
        elements.append(Spacer(1, 0.2*inch))
        
        # Create table data
        data = [["Network Name", "Type", "Accessible", "Additional Info"]]
        
        # Add data rows
        for network in self.data['networks']:
            # Prepare additional info
            additional_info = "Standard Network"
            if network['type'] == 'DistributedVirtualPortgroup':
                if 'dvs_name' in network and 'vlan_id' in network:
                    additional_info = f"DVS: {network['dvs_name']}, VLAN: {network['vlan_id']}"
                else:
                    additional_info = "Distributed Virtual Portgroup"
                
            data.append([
                network['name'],
                network['type'],
                str(network['accessible']),
                additional_info
            ])
        
        # Create table
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
        ]))
        
        elements.append(table)
        
    def _count_tools_needing_upgrade(self):
        """Count VMs with VMware Tools needing upgrade"""
        if 'vmware_tools' not in self.data:
            return 0
            
        return sum(1 for vm in self.data['vmware_tools'] 
                  if vm['vmware_tools_version'] == 'guestToolsNeedUpgrade')
                  
    def _count_vms_with_snapshots(self):
        """Count VMs with snapshots"""
        if 'snapshots' not in self.data:
            return 0
            
        # Get unique VM names
        vm_names = set(snapshot['vm_name'] for snapshot in self.data['snapshots'])
        return len(vm_names)
        
    def _count_orphaned_vmdks(self):
        """Count orphaned VMDKs"""
        if 'orphaned_vmdks' not in self.data:
            return 0
            
        return len(self.data['orphaned_vmdks'])
        
    def _count_total_vms(self):
        """Count total VMs"""
        if 'vms' in self.data:
            return len(self.data['vms'])
        return 0
        
    def _count_total_hosts(self):
        """Count total hosts"""
        if 'hosts' in self.data:
            return len(self.data['hosts'])
        return 0
        
    def _count_total_datastores(self):
        """Count total datastores"""
        if 'datastores' in self.data:
            return len(self.data['datastores'])
        return 0
        
    @staticmethod
    def _format_datetime(value):
        """Format datetime value for display"""
        if isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value)
        
    @staticmethod
    def _format_size(value):
        """Format byte size value for display"""
        try:
            return humanize.naturalsize(value, binary=True)
        except:
            return str(value)
            
    @staticmethod
    def _format_percent(value):
        """Format percentage value for display"""
        try:
            return f"{value:.2f}%"
        except:
            return str(value)
