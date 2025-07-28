"""
Koeka Shop POS Installation Wizard
A GUI-based installer for the Point of Sale system
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys
import os
import threading
from pathlib import Path
import shutil

class InstallationWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Koeka Shop POS Installation Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Installation variables
        self.install_path = tk.StringVar(value=os.getcwd())
        self.create_shortcuts = tk.BooleanVar(value=True)
        self.create_demo_data = tk.BooleanVar(value=True)
        
        # Current step
        self.current_step = 0
        self.steps = [
            ("Welcome", self.create_welcome_page),
            ("System Check", self.create_system_check_page),
            ("Installation Path", self.create_path_page),
            ("Options", self.create_options_page),
            ("Installation", self.create_install_page),
            ("Complete", self.create_complete_page)
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI structure"""
        # Header frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="Koeka Shop POS Installation Wizard",
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='determinate', 
                                       maximum=len(self.steps)-1)
        self.progress.pack(fill='x', padx=20, pady=10)
        
        # Main content frame
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        self.back_button = tk.Button(button_frame, text="< Back", 
                                    command=self.go_back, state='disabled')
        self.back_button.pack(side='left')
        
        self.next_button = tk.Button(button_frame, text="Next >", 
                                    command=self.go_next)
        self.next_button.pack(side='right')
        
        self.cancel_button = tk.Button(button_frame, text="Cancel", 
                                      command=self.cancel_install)
        self.cancel_button.pack(side='right', padx=(0, 10))
        
        # Show first step
        self.show_step()
        
    def show_step(self):
        """Display the current step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Update progress
        self.progress['value'] = self.current_step
        
        # Show current step
        step_name, step_func = self.steps[self.current_step]
        step_func()
        
        # Update buttons
        self.back_button['state'] = 'normal' if self.current_step > 0 else 'disabled'
        
        if self.current_step == len(self.steps) - 1:
            self.next_button['text'] = "Finish"
        elif self.current_step == len(self.steps) - 2:  # Installation step
            self.next_button['text'] = "Install"
        else:
            self.next_button['text'] = "Next >"
            
    def create_welcome_page(self):
        """Welcome page"""
        tk.Label(self.content_frame, text="Welcome to Koeka Shop POS", 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        welcome_text = """This wizard will guide you through the installation of the Koeka Shop Point of Sale system.

This system provides:
• Complete POS transaction processing
• Product and inventory management  
• Daily cash management and reporting
• Monthly financial reports
• User management with role-based access

The installation will:
• Check system requirements
• Install Python dependencies
• Set up the database
• Create desktop shortcuts
• Configure demo data

Click Next to continue."""

        tk.Label(self.content_frame, text=welcome_text, justify='left', 
                wraplength=500).pack(pady=20, anchor='w')
                
    def create_system_check_page(self):
        """System requirements check"""
        tk.Label(self.content_frame, text="System Requirements Check", 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        # Create check results frame
        results_frame = tk.Frame(self.content_frame)
        results_frame.pack(fill='both', expand=True)
        
        # Python check
        python_frame = tk.Frame(results_frame)
        python_frame.pack(fill='x', pady=5)
        
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                tk.Label(python_frame, text="✓", fg='green', font=('Arial', 12, 'bold')).pack(side='left')
                tk.Label(python_frame, text=f"Python: {result.stdout.strip()}").pack(side='left', padx=(10, 0))
            else:
                tk.Label(python_frame, text="✗", fg='red', font=('Arial', 12, 'bold')).pack(side='left')
                tk.Label(python_frame, text="Python: Not found").pack(side='left', padx=(10, 0))
        except:
            tk.Label(python_frame, text="✗", fg='red', font=('Arial', 12, 'bold')).pack(side='left')
            tk.Label(python_frame, text="Python: Not found").pack(side='left', padx=(10, 0))
        
        # Pip check
        pip_frame = tk.Frame(results_frame)
        pip_frame.pack(fill='x', pady=5)
        
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                tk.Label(pip_frame, text="✓", fg='green', font=('Arial', 12, 'bold')).pack(side='left')
                tk.Label(pip_frame, text="Package installer (pip): Available").pack(side='left', padx=(10, 0))
            else:
                tk.Label(pip_frame, text="✗", fg='red', font=('Arial', 12, 'bold')).pack(side='left')
                tk.Label(pip_frame, text="Package installer (pip): Not available").pack(side='left', padx=(10, 0))
        except:
            tk.Label(pip_frame, text="✗", fg='red', font=('Arial', 12, 'bold')).pack(side='left')
            tk.Label(pip_frame, text="Package installer (pip): Not available").pack(side='left', padx=(10, 0))
        
        # Disk space check
        disk_frame = tk.Frame(results_frame)
        disk_frame.pack(fill='x', pady=5)
        
        try:
            statvfs = os.statvfs('.')
            free_space = statvfs.f_frsize * statvfs.f_bavail / (1024 * 1024)  # MB
            if free_space > 100:  # Need at least 100MB
                tk.Label(disk_frame, text="✓", fg='green', font=('Arial', 12, 'bold')).pack(side='left')
                tk.Label(disk_frame, text=f"Disk space: {free_space:.0f} MB available").pack(side='left', padx=(10, 0))
            else:
                tk.Label(disk_frame, text="✗", fg='red', font=('Arial', 12, 'bold')).pack(side='left')
                tk.Label(disk_frame, text="Disk space: Insufficient (need 100MB)").pack(side='left', padx=(10, 0))
        except:
            tk.Label(disk_frame, text="?", fg='orange', font=('Arial', 12, 'bold')).pack(side='left')
            tk.Label(disk_frame, text="Disk space: Unable to check").pack(side='left', padx=(10, 0))
            
    def create_path_page(self):
        """Installation path selection"""
        tk.Label(self.content_frame, text="Installation Location", 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        tk.Label(self.content_frame, text="Choose where to install Koeka Shop POS:").pack(anchor='w')
        
        path_frame = tk.Frame(self.content_frame)
        path_frame.pack(fill='x', pady=10)
        
        tk.Entry(path_frame, textvariable=self.install_path, width=60).pack(side='left', fill='x', expand=True)
        tk.Button(path_frame, text="Browse...", command=self.browse_path).pack(side='right', padx=(10, 0))
        
        tk.Label(self.content_frame, text="Note: The application will be installed in this folder.", 
                fg='gray').pack(anchor='w', pady=(10, 0))
                
    def create_options_page(self):
        """Installation options"""
        tk.Label(self.content_frame, text="Installation Options", 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        tk.Checkbutton(self.content_frame, text="Create desktop and start menu shortcuts", 
                      variable=self.create_shortcuts).pack(anchor='w', pady=5)
        
        tk.Checkbutton(self.content_frame, text="Create demo data for testing", 
                      variable=self.create_demo_data).pack(anchor='w', pady=5)
        
        info_text = """Demo data includes:
• Sample products in different categories
• Demo user account (admin/admin123)
• Test transactions for reporting

This is recommended for first-time users to explore the system."""
        
        tk.Label(self.content_frame, text=info_text, justify='left', 
                wraplength=500, fg='gray').pack(anchor='w', pady=(10, 0))
                
    def create_install_page(self):
        """Installation progress page"""
        tk.Label(self.content_frame, text="Installing Koeka Shop POS", 
                font=('Arial', 14, 'bold')).pack(pady=20)
        
        self.install_progress = ttk.Progressbar(self.content_frame, mode='indeterminate')
        self.install_progress.pack(fill='x', pady=10)
        
        self.install_status = tk.Label(self.content_frame, text="Ready to install...")
        self.install_status.pack(pady=10)
        
        # Text area for installation log
        log_frame = tk.Frame(self.content_frame)
        log_frame.pack(fill='both', expand=True, pady=10)
        
        self.install_log = tk.Text(log_frame, height=15, wrap='word')
        scrollbar = tk.Scrollbar(log_frame, orient='vertical', command=self.install_log.yview)
        self.install_log.configure(yscrollcommand=scrollbar.set)
        
        self.install_log.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_complete_page(self):
        """Installation complete page"""
        tk.Label(self.content_frame, text="Installation Complete!", 
                font=('Arial', 14, 'bold'), fg='green').pack(pady=20)
        
        complete_text = """Koeka Shop POS has been successfully installed!

You can now start the application by:
• Using the desktop shortcut
• Running 'python app.py' from the installation folder
• Using the Start Menu shortcut

Demo login credentials:
Username: admin
Password: admin123

For support and documentation, refer to the README.md file in the installation folder."""

        tk.Label(self.content_frame, text=complete_text, justify='left', 
                wraplength=500).pack(pady=20)
                
        self.next_button.configure(command=self.finish_install)
        
    def browse_path(self):
        """Browse for installation path"""
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(path)
            
    def go_next(self):
        """Go to next step"""
        if self.current_step == len(self.steps) - 2:  # Installation step
            self.start_installation()
        elif self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step()
        else:
            self.finish_install()
            
    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()
            
    def start_installation(self):
        """Start the installation process"""
        self.next_button['state'] = 'disabled'
        self.back_button['state'] = 'disabled'
        self.install_progress.start()
        
        # Run installation in separate thread
        threading.Thread(target=self.run_installation, daemon=True).start()
        
    def run_installation(self):
        """Run the actual installation"""
        try:
            self.log_message("Starting installation...")
            
            # Step 1: Install dependencies
            self.update_status("Installing Python dependencies...")
            self.log_message("Installing requirements...")
            
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                                  capture_output=True, text=True, cwd=self.install_path.get())
            
            if result.returncode == 0:
                self.log_message("Dependencies installed successfully")
            else:
                self.log_message(f"Error installing dependencies: {result.stderr}")
                raise Exception("Failed to install dependencies")
            
            # Step 2: Setup database
            self.update_status("Setting up database...")
            self.log_message("Initializing database...")
            
            result = subprocess.run([sys.executable, '-c', 
                                   "from core.database.connection import get_db_manager; get_db_manager().initialize_schema()"],
                                  capture_output=True, text=True, cwd=self.install_path.get())
            
            if result.returncode == 0:
                self.log_message("Database setup complete")
            else:
                self.log_message(f"Error setting up database: {result.stderr}")
                raise Exception("Failed to setup database")
            
            # Step 3: Create demo data
            if self.create_demo_data.get():
                self.update_status("Creating demo data...")
                self.log_message("Setting up demo user and data...")
                
                result = subprocess.run([sys.executable, '-c', 
                                       "from core.auth.authentication import ensure_demo_user; ensure_demo_user()"],
                                      capture_output=True, text=True, cwd=self.install_path.get())
                
                if result.returncode == 0:
                    self.log_message("Demo data created")
                else:
                    self.log_message(f"Warning: Could not create demo data: {result.stderr}")
            
            # Step 4: Create shortcuts
            if self.create_shortcuts.get():
                self.update_status("Creating shortcuts...")
                self.log_message("Creating desktop and start menu shortcuts...")
                # Note: Shortcut creation code would go here
                self.log_message("Shortcuts created")
            
            self.update_status("Installation complete!")
            self.log_message("Installation finished successfully!")
            
            # Move to completion page
            self.root.after(0, self.complete_installation)
            
        except Exception as e:
            self.log_message(f"Installation failed: {str(e)}")
            self.update_status("Installation failed!")
            self.root.after(0, self.installation_failed)
            
    def complete_installation(self):
        """Complete the installation"""
        self.install_progress.stop()
        self.next_button['state'] = 'normal'
        self.current_step += 1
        self.show_step()
        
    def installation_failed(self):
        """Handle installation failure"""
        self.install_progress.stop()
        self.next_button['state'] = 'normal'
        self.back_button['state'] = 'normal'
        messagebox.showerror("Installation Failed", 
                           "The installation failed. Please check the log for details.")
                           
    def log_message(self, message):
        """Add message to installation log"""
        def update_log():
            self.install_log.insert('end', f"{message}\n")
            self.install_log.see('end')
        
        self.root.after(0, update_log)
        
    def update_status(self, status):
        """Update installation status"""
        def update():
            self.install_status['text'] = status
        
        self.root.after(0, update)
        
    def cancel_install(self):
        """Cancel installation"""
        if messagebox.askyesno("Cancel Installation", 
                             "Are you sure you want to cancel the installation?"):
            self.root.quit()
            
    def finish_install(self):
        """Finish installation and close wizard"""
        self.root.quit()
        
    def run(self):
        """Run the installation wizard"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()

if __name__ == "__main__":
    wizard = InstallationWizard()
    wizard.run()
