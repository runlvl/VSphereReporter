#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VMware vSphere Reporter - Linux GUI Version
A comprehensive reporting tool for VMware vSphere environments

This is the Linux-compatible GUI version using Tkinter.
"""

import sys
import os
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from utils.logger import setup_logger
from core.vsphere_client import VSphereClient
from core.data_collector import DataCollector
from core.report_generator import ReportGenerator

class VSphereReporterGUI:
    """Main application window for Linux using Tkinter"""
    
    def __init__(self, root):
        """Initialize the main application window"""
        self.root = root
        self.root.title("VMware vSphere Reporter")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Configure the application
        self.configure_app()
        
        # Create the menu bar
        self.create_menu_bar()
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the connection frame
        self.create_connection_frame()
        
        # Create report options frame
        self.create_report_options_frame()
        
        # Create export options frame
        self.create_export_options_frame()
        
        # Create log frame
        self.create_log_frame()
        
        # Initialize variables
        self.vsphere_client = None
        self.is_connected = False
        
        # Display disconnected status
        self.update_connection_status(False)
        
    def configure_app(self):
        """Configure the application style"""
        style = ttk.Style()
        style.theme_use('clam')  # Use a platform-neutral theme
        
        # Configure colors
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TCheckbutton', background='#f0f0f0')
        style.configure('TRadiobutton', background='#f0f0f0')
        
        # Configure headers
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Configure buttons
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        
        # Configure status
        style.configure('Connected.TLabel', foreground='green')
        style.configure('Disconnected.TLabel', foreground='red')
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Connect to vCenter", command=self.show_connection_dialog)
        file_menu.add_command(label="Disconnect", command=self.disconnect, state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        self.file_menu = file_menu
        
    def create_connection_frame(self):
        """Create the connection status frame"""
        connection_frame = ttk.LabelFrame(self.main_frame, text="Connection Status", padding=(10, 5, 10, 5))
        connection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connection status
        status_frame = ttk.Frame(connection_frame)
        status_frame.pack(fill=tk.X)
        
        status_label = ttk.Label(status_frame, text="Status: ")
        status_label.pack(side=tk.LEFT)
        
        self.status_value = ttk.Label(status_frame, text="Disconnected")
        self.status_value.pack(side=tk.LEFT)
        
        # Server info
        server_frame = ttk.Frame(connection_frame)
        server_frame.pack(fill=tk.X)
        
        server_label = ttk.Label(server_frame, text="Server: ")
        server_label.pack(side=tk.LEFT)
        
        self.server_value = ttk.Label(server_frame, text="Not connected")
        self.server_value.pack(side=tk.LEFT)
        
        # Username info
        user_frame = ttk.Frame(connection_frame)
        user_frame.pack(fill=tk.X)
        
        user_label = ttk.Label(user_frame, text="Username: ")
        user_label.pack(side=tk.LEFT)
        
        self.user_value = ttk.Label(user_frame, text="Not connected")
        self.user_value.pack(side=tk.LEFT)
        
        # Connect button
        connect_button = ttk.Button(
            connection_frame, 
            text="Connect to vCenter", 
            command=self.show_connection_dialog,
            style="Primary.TButton"
        )
        connect_button.pack(side=tk.RIGHT, pady=(5, 0))
        
    def create_report_options_frame(self):
        """Create the report options frame"""
        options_frame = ttk.LabelFrame(self.main_frame, text="Report Options", padding=(10, 5, 10, 5))
        options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(
            options_frame, 
            text="Select the sections to include in the report. Required sections cannot be deselected.",
            wraplength=750
        )
        desc_label.pack(fill=tk.X, pady=(0, 10))
        
        # Options container
        options_container = ttk.Frame(options_frame)
        options_container.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Required sections
        left_frame = ttk.Frame(options_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        required_label = ttk.Label(left_frame, text="Required Sections:", style="Header.TLabel")
        required_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Required checkboxes (always checked and disabled)
        self.vmware_tools_var = tk.BooleanVar(value=True)
        vmware_tools_cb = ttk.Checkbutton(
            left_frame, 
            text="VMware Tools Versions (oldest first)", 
            variable=self.vmware_tools_var,
            state=tk.DISABLED
        )
        vmware_tools_cb.pack(anchor=tk.W, pady=2)
        
        self.snapshots_var = tk.BooleanVar(value=True)
        snapshots_cb = ttk.Checkbutton(
            left_frame, 
            text="VM Snapshots (oldest first)", 
            variable=self.snapshots_var,
            state=tk.DISABLED
        )
        snapshots_cb.pack(anchor=tk.W, pady=2)
        
        self.orphaned_vmdks_var = tk.BooleanVar(value=True)
        orphaned_vmdks_cb = ttk.Checkbutton(
            left_frame, 
            text="Orphaned VMDK Files", 
            variable=self.orphaned_vmdks_var,
            state=tk.DISABLED
        )
        orphaned_vmdks_cb.pack(anchor=tk.W, pady=2)
        
        # Right column - Optional sections
        right_frame = ttk.Frame(options_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        optional_label = ttk.Label(right_frame, text="Optional Sections:", style="Header.TLabel")
        optional_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Optional checkboxes
        self.vms_var = tk.BooleanVar(value=True)
        vms_cb = ttk.Checkbutton(right_frame, text="Virtual Machines", variable=self.vms_var)
        vms_cb.pack(anchor=tk.W, pady=2)
        
        self.hosts_var = tk.BooleanVar(value=True)
        hosts_cb = ttk.Checkbutton(right_frame, text="ESXi Hosts", variable=self.hosts_var)
        hosts_cb.pack(anchor=tk.W, pady=2)
        
        self.datastores_var = tk.BooleanVar(value=True)
        datastores_cb = ttk.Checkbutton(right_frame, text="Datastores", variable=self.datastores_var)
        datastores_cb.pack(anchor=tk.W, pady=2)
        
        self.clusters_var = tk.BooleanVar(value=True)
        clusters_cb = ttk.Checkbutton(right_frame, text="Clusters", variable=self.clusters_var)
        clusters_cb.pack(anchor=tk.W, pady=2)
        
        self.resource_pools_var = tk.BooleanVar(value=True)
        resource_pools_cb = ttk.Checkbutton(right_frame, text="Resource Pools", variable=self.resource_pools_var)
        resource_pools_cb.pack(anchor=tk.W, pady=2)
        
        self.networks_var = tk.BooleanVar(value=True)
        networks_cb = ttk.Checkbutton(right_frame, text="Networks", variable=self.networks_var)
        networks_cb.pack(anchor=tk.W, pady=2)
        
        # Select/Deselect All button for optional sections
        select_all_button = ttk.Button(
            right_frame, 
            text="Select All", 
            command=self.select_all_options
        )
        select_all_button.pack(anchor=tk.W, pady=(5, 0))
        
        deselect_all_button = ttk.Button(
            right_frame, 
            text="Deselect All", 
            command=self.deselect_all_options
        )
        deselect_all_button.pack(anchor=tk.W, pady=(5, 0))
        
    def create_export_options_frame(self):
        """Create the export options frame"""
        export_frame = ttk.LabelFrame(self.main_frame, text="Export Options", padding=(10, 5, 10, 5))
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Container frame
        container = ttk.Frame(export_frame)
        container.pack(fill=tk.X)
        
        # Left side - Export format
        format_frame = ttk.Frame(container)
        format_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        format_label = ttk.Label(format_frame, text="Export Format:", style="Header.TLabel")
        format_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.export_format = tk.StringVar(value="all")
        
        html_rb = ttk.Radiobutton(
            format_frame, 
            text="HTML", 
            variable=self.export_format, 
            value="html"
        )
        html_rb.pack(anchor=tk.W, pady=2)
        
        docx_rb = ttk.Radiobutton(
            format_frame, 
            text="DOCX (Microsoft Word)", 
            variable=self.export_format, 
            value="docx"
        )
        docx_rb.pack(anchor=tk.W, pady=2)
        
        pdf_rb = ttk.Radiobutton(
            format_frame, 
            text="PDF", 
            variable=self.export_format, 
            value="pdf"
        )
        pdf_rb.pack(anchor=tk.W, pady=2)
        
        all_rb = ttk.Radiobutton(
            format_frame, 
            text="All Formats", 
            variable=self.export_format, 
            value="all"
        )
        all_rb.pack(anchor=tk.W, pady=2)
        
        # Right side - Output directory & Generate button
        button_frame = ttk.Frame(container)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=(20, 0))
        
        self.generate_button = ttk.Button(
            button_frame, 
            text="Generate Report", 
            command=self.generate_report,
            style="Primary.TButton",
            state=tk.DISABLED
        )
        self.generate_button.pack(side=tk.BOTTOM, pady=(5, 0))
        
    def create_log_frame(self):
        """Create the log output frame"""
        log_frame = ttk.LabelFrame(self.main_frame, text="Log", padding=(10, 5, 10, 5))
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrolled text widget for log output
        self.log_text = ScrolledText(log_frame, height=10, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Create a custom handler for logging to the text widget
        self.setup_log_handler()
        
    def setup_log_handler(self):
        """Setup logging to the text widget"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record) + '\n'
                def append():
                    self.text_widget.config(state=tk.NORMAL)
                    self.text_widget.insert(tk.END, msg)
                    self.text_widget.see(tk.END)
                    self.text_widget.config(state=tk.DISABLED)
                self.text_widget.after(0, append)
                
        # Get logger
        logger = logging.getLogger()
        
        # Create handler
        text_handler = TextHandler(self.log_text)
        text_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        
        # Add handler
        logger.addHandler(text_handler)
        
    def show_connection_dialog(self):
        """Show the connection dialog to connect to vCenter"""
        # Create connection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Connect to vCenter")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make dialog modal
        dialog.focus_set()
        dialog.resizable(False, False)
        
        # Setup dialog content
        content_frame = ttk.Frame(dialog, padding=(20, 10, 20, 10))
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            content_frame, 
            text="Enter vCenter Connection Information", 
            style="Header.TLabel"
        )
        header_label.pack(pady=(0, 10))
        
        # Server
        server_frame = ttk.Frame(content_frame)
        server_frame.pack(fill=tk.X, pady=5)
        
        server_label = ttk.Label(server_frame, text="vCenter Server:", width=15, anchor=tk.W)
        server_label.pack(side=tk.LEFT)
        
        server_entry = ttk.Entry(server_frame)
        server_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Username
        username_frame = ttk.Frame(content_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="Username:", width=15, anchor=tk.W)
        username_label.pack(side=tk.LEFT)
        
        username_entry = ttk.Entry(username_frame)
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Password
        password_frame = ttk.Frame(content_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        password_label = ttk.Label(password_frame, text="Password:", width=15, anchor=tk.W)
        password_label.pack(side=tk.LEFT)
        
        password_entry = ttk.Entry(password_frame, show="*")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Ignore SSL
        ignore_ssl_var = tk.BooleanVar(value=True)
        ignore_ssl_cb = ttk.Checkbutton(
            content_frame, 
            text="Ignore SSL certificate verification", 
            variable=ignore_ssl_var
        )
        ignore_ssl_cb.pack(anchor=tk.W, pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        connect_button = ttk.Button(
            button_frame, 
            text="Connect", 
            command=lambda: self.connect_to_vcenter(
                server_entry.get(), 
                username_entry.get(), 
                password_entry.get(), 
                ignore_ssl_var.get(),
                dialog
            ),
            style="Primary.TButton"
        )
        connect_button.pack(side=tk.RIGHT)
        
        # Set focus
        server_entry.focus_set()
        
    def connect_to_vcenter(self, server, username, password, ignore_ssl, dialog):
        """Connect to vCenter with the provided credentials"""
        # Validate inputs
        if not server or not username or not password:
            messagebox.showerror("Connection Error", "Please fill in all fields.")
            return
        
        # Update log
        logging.info(f"Connecting to vCenter server: {server}")
        
        try:
            # Create client
            self.vsphere_client = VSphereClient(server, username, password, ignore_ssl)
            
            # Connect in a separate thread
            def connect_thread():
                try:
                    self.vsphere_client.connect()
                    
                    # Update UI on success
                    self.root.after(0, lambda: self.connection_finished(True, server, username, dialog))
                    
                except Exception as e:
                    # Update UI on error
                    error_msg = str(e)
                    self.root.after(0, lambda: self.connection_finished(False, None, None, dialog, error_msg))
            
            # Show progress
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "Connecting to vCenter...\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
            
            # Start thread
            thread = threading.Thread(target=connect_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Error connecting to vCenter: {str(e)}")
            logging.error(f"Connection error: {str(e)}")
            
    def connection_finished(self, success, server, username, dialog, error_message=None):
        """Handle connection completion"""
        if success:
            # Close the dialog
            dialog.destroy()
            
            # Update status
            self.update_connection_status(True, server, username)
            
            # Update menu
            self.file_menu.entryconfig("Disconnect", state=tk.NORMAL)
            
            # Enable generate button
            self.generate_button.config(state=tk.NORMAL)
            
            # Show success message
            messagebox.showinfo("Connection Success", f"Successfully connected to vCenter server: {server}")
            logging.info("Connected successfully")
            
        else:
            # Show error message
            messagebox.showerror("Connection Error", f"Error connecting to vCenter: {error_message}")
            logging.error(f"Connection error: {error_message}")
            
    def update_connection_status(self, is_connected, server=None, username=None):
        """Update the connection status display"""
        self.is_connected = is_connected
        
        if is_connected:
            self.status_value.config(text="Connected", style="Connected.TLabel")
            self.server_value.config(text=server)
            self.user_value.config(text=username)
        else:
            self.status_value.config(text="Disconnected", style="Disconnected.TLabel")
            self.server_value.config(text="Not connected")
            self.user_value.config(text="Not connected")
            
    def disconnect(self):
        """Disconnect from vCenter"""
        if self.vsphere_client:
            try:
                self.vsphere_client.disconnect()
                self.vsphere_client = None
                
                # Update status
                self.update_connection_status(False)
                
                # Update menu
                self.file_menu.entryconfig("Disconnect", state=tk.DISABLED)
                
                # Disable generate button
                self.generate_button.config(state=tk.DISABLED)
                
                # Log
                logging.info("Disconnected from vCenter")
                
            except Exception as e:
                messagebox.showerror("Disconnect Error", f"Error disconnecting from vCenter: {str(e)}")
                logging.error(f"Disconnect error: {str(e)}")
                
    def select_all_options(self):
        """Select all optional report sections"""
        self.vms_var.set(True)
        self.hosts_var.set(True)
        self.datastores_var.set(True)
        self.clusters_var.set(True)
        self.resource_pools_var.set(True)
        self.networks_var.set(True)
        
    def deselect_all_options(self):
        """Deselect all optional report sections"""
        self.vms_var.set(False)
        self.hosts_var.set(False)
        self.datastores_var.set(False)
        self.clusters_var.set(False)
        self.resource_pools_var.set(False)
        self.networks_var.set(False)
        
    def generate_report(self):
        """Generate the vSphere report"""
        if not self.is_connected or not self.vsphere_client:
            messagebox.showerror("Error", "Not connected to vCenter. Please connect first.")
            return
            
        # Ask for save directory
        save_dir = filedialog.askdirectory(
            title="Select Directory to Save Reports",
            initialdir=os.path.expanduser("~")
        )
        
        if not save_dir:
            return  # User canceled
            
        # Get selected options
        options = self.get_selected_options()
        
        # Get export format
        export_format = self.export_format.get()
        
        # Show progress dialog
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("Generating Report")
        progress_dialog.geometry("400x150")
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
        progress_dialog.resizable(False, False)
        
        # Progress dialog content
        dialog_frame = ttk.Frame(progress_dialog, padding=(20, 10, 20, 10))
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        status_label = ttk.Label(
            dialog_frame, 
            text="Collecting data from vCenter...",
            wraplength=360
        )
        status_label.pack(pady=(0, 10))
        
        progress_bar = ttk.Progressbar(dialog_frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X)
        progress_bar.start()
        
        # Generate in a separate thread
        def generate_thread():
            try:
                # Start data collection
                collector = DataCollector(self.vsphere_client)
                
                # Update progress information
                def update_status(text):
                    status_label.config(text=text)
                
                # Collect data
                data = {}
                
                # Required sections
                update_status("Collecting VMware Tools information...")
                data['vmware_tools'] = collector.collect_vmware_tools_info()
                
                update_status("Collecting snapshot information...")
                data['snapshots'] = collector.collect_snapshot_info()
                
                update_status("Collecting orphaned VMDK information...")
                data['orphaned_vmdks'] = collector.collect_orphaned_vmdks()
                
                # Optional sections
                if options.get('vms', False):
                    update_status("Collecting VM information...")
                    data['vms'] = collector.collect_vm_info()
                    
                if options.get('hosts', False):
                    update_status("Collecting host information...")
                    data['hosts'] = collector.collect_host_info()
                    
                if options.get('datastores', False):
                    update_status("Collecting datastore information...")
                    data['datastores'] = collector.collect_datastore_info()
                    
                if options.get('clusters', False):
                    update_status("Collecting cluster information...")
                    data['clusters'] = collector.collect_cluster_info()
                    
                if options.get('resource_pools', False):
                    update_status("Collecting resource pool information...")
                    data['resource_pools'] = collector.collect_resource_pool_info()
                    
                if options.get('networks', False):
                    update_status("Collecting network information...")
                    data['networks'] = collector.collect_network_info()
                
                # Generate reports
                update_status("Generating reports...")
                report_generator = ReportGenerator(data)
                output_files = []
                
                if export_format == 'html' or export_format == 'all':
                    update_status("Generating HTML report...")
                    html_file = report_generator.export_to_html(save_dir)
                    output_files.append(html_file)
                    
                if export_format == 'docx' or export_format == 'all':
                    update_status("Generating DOCX report...")
                    docx_file = report_generator.export_to_docx(save_dir)
                    output_files.append(docx_file)
                    
                if export_format == 'pdf' or export_format == 'all':
                    update_status("Generating PDF report...")
                    pdf_file = report_generator.export_to_pdf(save_dir)
                    output_files.append(pdf_file)
                
                # Close dialog and show success
                self.root.after(0, lambda: self.report_finished(True, output_files, progress_dialog))
                
            except Exception as e:
                # Show error
                error_msg = str(e)
                self.root.after(0, lambda: self.report_finished(False, None, progress_dialog, error_msg))
        
        # Start thread
        thread = threading.Thread(target=generate_thread)
        thread.daemon = True
        thread.start()
        
    def report_finished(self, success, output_files, dialog, error_message=None):
        """Handle report generation completion"""
        # Close the progress dialog
        dialog.destroy()
        
        if success:
            # Format the output files as a list
            files_list = "\n".join([f"- {os.path.basename(f)}" for f in output_files])
            
            # Show success message
            messagebox.showinfo(
                "Report Generation Complete", 
                f"Reports generated successfully and saved to:\n\n{os.path.dirname(output_files[0])}\n\nFiles:\n{files_list}"
            )
            logging.info(f"Reports generated successfully: {', '.join([os.path.basename(f) for f in output_files])}")
            
        else:
            # Show error message
            messagebox.showerror("Report Generation Error", f"Error generating report: {error_message}")
            logging.error(f"Report generation error: {error_message}")
            
    def get_selected_options(self):
        """Get the selected report options"""
        return {
            'vms': self.vms_var.get(),
            'hosts': self.hosts_var.get(),
            'datastores': self.datastores_var.get(),
            'clusters': self.clusters_var.get(),
            'resource_pools': self.resource_pools_var.get(),
            'networks': self.networks_var.get()
        }
        
    def show_about_dialog(self):
        """Show the about dialog"""
        messagebox.showinfo(
            "About VMware vSphere Reporter",
            "VMware vSphere Reporter 1.0.0\n\n"
            "A comprehensive reporting tool for VMware vSphere environments\n\n"
            "This application generates detailed reports about VMware vSphere environments, "
            "including VMware Tools versions, snapshot age, orphaned VMDK files, and more.\n\n"
            "© 2025 All rights reserved."
        )

def main():
    """Main entry point for the application"""
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting VMware vSphere Reporter Linux GUI")
    
    # Replit environment detection
    import os
    is_replit = os.environ.get('REPL_ID', '') != ''
    if is_replit:
        logger.warning("Running in Replit environment - GUI might not be available")
        print("Running in Replit environment - GUI mode is not available")
        print("Please use the CLI version or download the application to run locally")
        
        # Display the CLI usage as fallback
        import subprocess
        print("\nAvailable CLI options:")
        subprocess.run(["python", "vsphere_reporter_cli.py", "--help"])
        return
    
    # Check if running in headless mode
    try:
        # Tkinter needs a display to work
        display = os.environ.get('DISPLAY', '')
        if not display:
            logger.error("No display detected (DISPLAY environment variable not set)")
            raise Exception("No display detected. Running in headless mode.")
        
        # Create Tkinter root window
        root = tk.Tk()
        
        # Create application
        app = VSphereReporterGUI(root)
        
        # Run the application
        root.mainloop()
    except Exception as e:
        logger.error(f"Error starting Linux GUI: {str(e)}")
        print(f"Error starting Linux GUI: {str(e)}")
        print("Falling back to CLI mode. Run 'python vsphere_reporter_cli.py --help' for usage information.")
        
        # Show clear message about GUI not available
        print("\nTkinter GUI could not be initialized. This might be due to:")
        print("1. Missing Tkinter package on your system")
        print("2. No display server available (running in headless mode)")
        print("3. Display server configuration issues")
        print("\nPlease ensure Tkinter is properly installed:")
        print("- For Debian/Ubuntu: sudo apt install python3-tk")
        print("- For RedHat/CentOS: sudo dnf install python3-tkinter")
        print("- For OpenSUSE: sudo zypper install python3-tk")
        
        # Display the CLI usage as fallback
        import subprocess
        print("\nAvailable CLI options:")
        subprocess.run(["python", "vsphere_reporter_cli.py", "--help"])

if __name__ == "__main__":
    main()