"""
Settings GUI for Tembie's Spaza Shop POS System
System configuration, user management, and preferences
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import get_settings_manager, SystemSettings
from config.module_registry import get_module_registry
from core.auth.authentication import get_auth_manager
from utils.helpers import hash_password

class SettingsWindow:
    """Settings and configuration interface"""
    
    def __init__(self, parent=None, user=None):
        self.parent = parent
        self.user = user or get_auth_manager().get_current_user()
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        
        # Initialize managers
        self.settings_manager = get_settings_manager()
        self.module_registry = get_module_registry()
        self.auth_manager = get_auth_manager()
        
        # Current settings
        self.current_settings = self.settings_manager.get_settings()
        
        self.setup_window()
        self.create_widgets()
        self.load_current_settings()
        
    def setup_window(self):
        """Configure window properties"""
        self.root.title("Settings - Tembie's Spaza Shop")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Configure style
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Subheader.TLabel', font=('Arial', 12, 'bold'))
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"800x700+{x}+{y}")
        
    def create_widgets(self):
        """Create and layout all widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Notebook for different settings categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        # Create tabs
        self.create_general_tab()
        self.create_business_tab()
        self.create_system_tab()
        self.create_users_tab()
        self.create_modules_tab()
        
        # Action buttons
        self.create_action_buttons(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create header with title and user info"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="System Settings", style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # User info
        user_info = f"{self.user.full_name} ({self.user.role})"
        user_label = ttk.Label(header_frame, text=user_info)
        user_label.grid(row=0, column=1, sticky="e")
        
    def create_general_tab(self):
        """Create general settings tab"""
        general_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(general_frame, text="General")
        
        # Shop Information
        shop_frame = ttk.LabelFrame(general_frame, text="Shop Information", padding="10")
        shop_frame.pack(fill=tk.X, pady=(0, 15))
        shop_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Shop name
        ttk.Label(shop_frame, text="Shop Name:").grid(row=row, column=0, sticky="w", pady=5)
        self.shop_name_var = tk.StringVar()
        ttk.Entry(shop_frame, textvariable=self.shop_name_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Shop address
        ttk.Label(shop_frame, text="Address:").grid(row=row, column=0, sticky="nw", pady=5)
        self.address_var = tk.StringVar()
        address_text = tk.Text(shop_frame, height=3, width=40)
        address_text.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        self.address_text = address_text
        row += 1
        
        # Contact info
        ttk.Label(shop_frame, text="Phone:").grid(row=row, column=0, sticky="w", pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(shop_frame, textvariable=self.phone_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        ttk.Label(shop_frame, text="Email:").grid(row=row, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(shop_frame, textvariable=self.email_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Display Settings
        display_frame = ttk.LabelFrame(general_frame, text="Display Settings", padding="10")
        display_frame.pack(fill=tk.X, pady=(0, 15))
        display_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Theme
        ttk.Label(display_frame, text="Theme:").grid(row=row, column=0, sticky="w", pady=5)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(display_frame, textvariable=self.theme_var,
                                 values=["default", "clam", "alt", "classic"], 
                                 state="readonly", width=20)
        theme_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Language
        ttk.Label(display_frame, text="Language:").grid(row=row, column=0, sticky="w", pady=5)
        self.language_var = tk.StringVar()
        language_combo = ttk.Combobox(display_frame, textvariable=self.language_var,
                                    values=["English", "Afrikaans"], 
                                    state="readonly", width=20)
        language_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Timezone
        ttk.Label(display_frame, text="Timezone:").grid(row=row, column=0, sticky="w", pady=5)
        self.timezone_var = tk.StringVar()
        timezone_combo = ttk.Combobox(display_frame, textvariable=self.timezone_var,
                                    values=["Africa/Johannesburg", "UTC"], 
                                    state="readonly", width=20)
        timezone_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
    def create_business_tab(self):
        """Create business settings tab"""
        business_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(business_frame, text="Business")
        
        # VAT Settings
        vat_frame = ttk.LabelFrame(business_frame, text="VAT Settings", padding="10")
        vat_frame.pack(fill=tk.X, pady=(0, 15))
        vat_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # VAT registered
        ttk.Label(vat_frame, text="VAT Registered:").grid(row=row, column=0, sticky="w", pady=5)
        self.vat_registered_var = tk.BooleanVar()
        ttk.Checkbutton(vat_frame, variable=self.vat_registered_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # VAT number
        ttk.Label(vat_frame, text="VAT Number:").grid(row=row, column=0, sticky="w", pady=5)
        self.vat_number_var = tk.StringVar()
        ttk.Entry(vat_frame, textvariable=self.vat_number_var, width=20).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Default VAT rate
        ttk.Label(vat_frame, text="Default VAT Rate (%):").grid(row=row, column=0, sticky="w", pady=5)
        self.vat_rate_var = tk.StringVar()
        ttk.Entry(vat_frame, textvariable=self.vat_rate_var, width=10).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # VAT inclusive by default
        ttk.Label(vat_frame, text="VAT Inclusive by Default:").grid(row=row, column=0, sticky="w", pady=5)
        self.vat_inclusive_var = tk.BooleanVar()
        ttk.Checkbutton(vat_frame, variable=self.vat_inclusive_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Currency Settings
        currency_frame = ttk.LabelFrame(business_frame, text="Currency Settings", padding="10")
        currency_frame.pack(fill=tk.X, pady=(0, 15))
        currency_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Currency code
        ttk.Label(currency_frame, text="Currency:").grid(row=row, column=0, sticky="w", pady=5)
        self.currency_var = tk.StringVar()
        currency_combo = ttk.Combobox(currency_frame, textvariable=self.currency_var,
                                    values=["ZAR", "USD", "EUR"], 
                                    state="readonly", width=10)
        currency_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Currency symbol
        ttk.Label(currency_frame, text="Symbol:").grid(row=row, column=0, sticky="w", pady=5)
        self.currency_symbol_var = tk.StringVar()
        ttk.Entry(currency_frame, textvariable=self.currency_symbol_var, width=5).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Receipt Settings
        receipt_frame = ttk.LabelFrame(business_frame, text="Receipt Settings", padding="10")
        receipt_frame.pack(fill=tk.X, pady=(0, 15))
        receipt_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Receipt header
        ttk.Label(receipt_frame, text="Receipt Header:").grid(row=row, column=0, sticky="nw", pady=5)
        self.receipt_header_text = tk.Text(receipt_frame, height=3, width=40)
        self.receipt_header_text.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Receipt footer
        ttk.Label(receipt_frame, text="Receipt Footer:").grid(row=row, column=0, sticky="nw", pady=5)
        self.receipt_footer_text = tk.Text(receipt_frame, height=2, width=40)
        self.receipt_footer_text.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        
    def create_system_tab(self):
        """Create system settings tab"""
        system_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(system_frame, text="System")
        
        # Database Settings
        db_frame = ttk.LabelFrame(system_frame, text="Database Settings", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 15))
        db_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Database file location
        ttk.Label(db_frame, text="Database File:").grid(row=row, column=0, sticky="w", pady=5)
        self.db_path_var = tk.StringVar()
        db_frame_inner = ttk.Frame(db_frame)
        db_frame_inner.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        db_frame_inner.columnconfigure(0, weight=1)
        
        ttk.Entry(db_frame_inner, textvariable=self.db_path_var, state="readonly").grid(row=0, column=0, sticky="ew")
        ttk.Button(db_frame_inner, text="Browse", command=self.browse_database).grid(row=0, column=1, padx=(5, 0))
        row += 1
        
        # Backup settings
        ttk.Label(db_frame, text="Auto Backup:").grid(row=row, column=0, sticky="w", pady=5)
        self.auto_backup_var = tk.BooleanVar()
        ttk.Checkbutton(db_frame, variable=self.auto_backup_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Backup frequency
        ttk.Label(db_frame, text="Backup Frequency:").grid(row=row, column=0, sticky="w", pady=5)
        self.backup_frequency_var = tk.StringVar()
        backup_combo = ttk.Combobox(db_frame, textvariable=self.backup_frequency_var,
                                   values=["Daily", "Weekly", "Monthly"], 
                                   state="readonly", width=15)
        backup_combo.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Security Settings
        security_frame = ttk.LabelFrame(system_frame, text="Security Settings", padding="10")
        security_frame.pack(fill=tk.X, pady=(0, 15))
        security_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Auto logout
        ttk.Label(security_frame, text="Auto Logout (minutes):").grid(row=row, column=0, sticky="w", pady=5)
        self.auto_logout_var = tk.StringVar()
        ttk.Entry(security_frame, textvariable=self.auto_logout_var, width=10).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Require login
        ttk.Label(security_frame, text="Require Login:").grid(row=row, column=0, sticky="w", pady=5)
        self.require_login_var = tk.BooleanVar()
        ttk.Checkbutton(security_frame, variable=self.require_login_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Audit logging
        ttk.Label(security_frame, text="Audit Logging:").grid(row=row, column=0, sticky="w", pady=5)
        self.audit_logging_var = tk.BooleanVar()
        ttk.Checkbutton(security_frame, variable=self.audit_logging_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Hardware Settings
        hardware_frame = ttk.LabelFrame(system_frame, text="Hardware Settings", padding="10")
        hardware_frame.pack(fill=tk.X, pady=(0, 15))
        hardware_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Barcode scanner
        ttk.Label(hardware_frame, text="Barcode Scanner:").grid(row=row, column=0, sticky="w", pady=5)
        self.barcode_scanner_var = tk.BooleanVar()
        ttk.Checkbutton(hardware_frame, variable=self.barcode_scanner_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Receipt printer
        ttk.Label(hardware_frame, text="Receipt Printer:").grid(row=row, column=0, sticky="w", pady=5)
        self.receipt_printer_var = tk.BooleanVar()
        ttk.Checkbutton(hardware_frame, variable=self.receipt_printer_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Cash drawer
        ttk.Label(hardware_frame, text="Cash Drawer:").grid(row=row, column=0, sticky="w", pady=5)
        self.cash_drawer_var = tk.BooleanVar()
        ttk.Checkbutton(hardware_frame, variable=self.cash_drawer_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        
    def create_users_tab(self):
        """Create user management tab"""
        users_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(users_frame, text="Users")
        
        # Users list
        users_list_frame = ttk.LabelFrame(users_frame, text="User Accounts", padding="10")
        users_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        users_list_frame.columnconfigure(0, weight=1)
        users_list_frame.rowconfigure(1, weight=1)
        
        # User list controls
        controls_frame = ttk.Frame(users_list_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Edit User", command=self.edit_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Reset Password", command=self.reset_password).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Deactivate", command=self.deactivate_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_users).pack(side=tk.RIGHT)
        
        # Users treeview
        columns = ("ID", "Username", "Full Name", "Role", "Status", "Last Login")
        self.users_tree = ttk.Treeview(users_list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            
        self.users_tree.column("ID", width=50)
        self.users_tree.column("Username", width=100)
        self.users_tree.column("Full Name", width=150)
        self.users_tree.column("Role", width=100)
        self.users_tree.column("Status", width=80)
        self.users_tree.column("Last Login", width=120)
        
        users_scrollbar = ttk.Scrollbar(users_list_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.grid(row=1, column=0, sticky="nsew")
        users_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Load users
        self.refresh_users()
        
    def create_modules_tab(self):
        """Create modules management tab"""
        modules_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(modules_frame, text="Modules")
        
        # Installed modules
        installed_frame = ttk.LabelFrame(modules_frame, text="Installed Modules", padding="10")
        installed_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        installed_frame.columnconfigure(0, weight=1)
        installed_frame.rowconfigure(1, weight=1)
        
        # Module controls
        module_controls_frame = ttk.Frame(installed_frame)
        module_controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(module_controls_frame, text="Install Module", command=self.install_module).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(module_controls_frame, text="Enable/Disable", command=self.toggle_module).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(module_controls_frame, text="Module Info", command=self.show_module_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(module_controls_frame, text="Refresh", command=self.refresh_modules).pack(side=tk.RIGHT)
        
        # Modules treeview
        module_columns = ("Name", "Version", "Tier", "Status", "Description")
        self.modules_tree = ttk.Treeview(installed_frame, columns=module_columns, show="headings")
        
        for col in module_columns:
            self.modules_tree.heading(col, text=col)
            
        self.modules_tree.column("Name", width=150)
        self.modules_tree.column("Version", width=80)
        self.modules_tree.column("Tier", width=50)
        self.modules_tree.column("Status", width=80)
        self.modules_tree.column("Description", width=200)
        
        modules_scrollbar = ttk.Scrollbar(installed_frame, orient="vertical", command=self.modules_tree.yview)
        self.modules_tree.configure(yscrollcommand=modules_scrollbar.set)
        
        self.modules_tree.grid(row=1, column=0, sticky="nsew")
        modules_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Load modules
        self.refresh_modules()
        
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_to_defaults).pack(side=tk.LEFT)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        time_label = ttk.Label(status_frame, text=datetime.now().strftime("%Y-%m-%d %H:%M"))
        time_label.grid(row=0, column=1, sticky="e")
        
    def load_current_settings(self):
        """Load current settings into the form"""
        settings = self.current_settings
        
        # General tab
        self.shop_name_var.set(settings.shop_name)
        if settings.shop_address:
            self.address_text.delete(1.0, tk.END)
            self.address_text.insert(1.0, settings.shop_address)
        self.phone_var.set(settings.shop_phone or "")
        self.email_var.set(settings.shop_email or "")
        self.theme_var.set(settings.theme)
        self.language_var.set(settings.language)
        self.timezone_var.set(settings.timezone)
        
        # Business tab
        self.vat_registered_var.set(settings.vat_registered)
        self.vat_number_var.set(settings.vat_number or "")
        self.vat_rate_var.set(str(settings.default_vat_rate))
        self.vat_inclusive_var.set(settings.vat_inclusive_default)
        self.currency_var.set(settings.currency)
        self.currency_symbol_var.set(settings.currency_symbol)
        
        if settings.receipt_header:
            self.receipt_header_text.delete(1.0, tk.END)
            self.receipt_header_text.insert(1.0, settings.receipt_header)
        if settings.receipt_footer:
            self.receipt_footer_text.delete(1.0, tk.END)
            self.receipt_footer_text.insert(1.0, settings.receipt_footer)
            
        # System tab
        self.db_path_var.set(settings.database_path or "spaza_shop.db")
        self.auto_backup_var.set(settings.auto_backup)
        self.backup_frequency_var.set(settings.backup_frequency)
        self.auto_logout_var.set(str(settings.auto_logout_minutes))
        self.require_login_var.set(settings.require_login)
        self.audit_logging_var.set(settings.audit_logging)
        self.barcode_scanner_var.set(settings.barcode_scanner_enabled)
        self.receipt_printer_var.set(settings.receipt_printer_enabled)
        self.cash_drawer_var.set(settings.cash_drawer_enabled)
        
    def save_settings(self):
        """Save settings and close window"""
        if self.apply_settings():
            self.root.destroy()
            
    def apply_settings(self):
        """Apply settings without closing window"""
        try:
            # Create new settings object
            new_settings = SystemSettings(
                # General
                shop_name=self.shop_name_var.get().strip(),
                shop_address=self.address_text.get(1.0, tk.END).strip(),
                shop_phone=self.phone_var.get().strip() or None,
                shop_email=self.email_var.get().strip() or None,
                theme=self.theme_var.get(),
                language=self.language_var.get(),
                timezone=self.timezone_var.get(),
                
                # Business
                vat_registered=self.vat_registered_var.get(),
                vat_number=self.vat_number_var.get().strip() or None,
                default_vat_rate=float(self.vat_rate_var.get() or 15.0),
                vat_inclusive_default=self.vat_inclusive_var.get(),
                currency=self.currency_var.get(),
                currency_symbol=self.currency_symbol_var.get(),
                receipt_header=self.receipt_header_text.get(1.0, tk.END).strip() or None,
                receipt_footer=self.receipt_footer_text.get(1.0, tk.END).strip() or None,
                
                # System
                database_path=self.db_path_var.get().strip() or None,
                auto_backup=self.auto_backup_var.get(),
                backup_frequency=self.backup_frequency_var.get(),
                auto_logout_minutes=int(self.auto_logout_var.get() or 30),
                require_login=self.require_login_var.get(),
                audit_logging=self.audit_logging_var.get(),
                barcode_scanner_enabled=self.barcode_scanner_var.get(),
                receipt_printer_enabled=self.receipt_printer_var.get(),
                cash_drawer_enabled=self.cash_drawer_var.get()
            )
            
            # Validate settings
            if not new_settings.shop_name:
                messagebox.showerror("Validation Error", "Shop name is required")
                return False
                
            if new_settings.default_vat_rate < 0 or new_settings.default_vat_rate > 100:
                messagebox.showerror("Validation Error", "VAT rate must be between 0 and 100")
                return False
                
            if new_settings.auto_logout_minutes < 1:
                messagebox.showerror("Validation Error", "Auto logout time must be at least 1 minute")
                return False
                
            # Save settings
            success = self.settings_manager.save_settings(new_settings)
            if success:
                self.current_settings = new_settings
                self.status_label.config(text="Settings saved successfully")
                messagebox.showinfo("Success", "Settings saved successfully")
                return True
            else:
                messagebox.showerror("Error", "Failed to save settings")
                return False
                
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid value: {str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            return False
            
    def cancel(self):
        """Cancel changes and close window"""
        self.root.destroy()
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Confirm Reset", 
                             "Are you sure you want to reset all settings to defaults?\n"
                             "This will overwrite all current settings."):
            try:
                # Reset to default settings
                default_settings = SystemSettings()
                self.settings_manager.save_settings(default_settings)
                self.current_settings = default_settings
                
                # Reload form
                self.load_current_settings()
                
                self.status_label.config(text="Settings reset to defaults")
                messagebox.showinfo("Reset Complete", "All settings have been reset to defaults")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
                
    def browse_database(self):
        """Browse for database file"""
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.db_path_var.get() or ".")
        )
        
        if file_path:
            self.db_path_var.set(file_path)
            
    def refresh_users(self):
        """Refresh users list"""
        try:
            from core.database.connection import get_db_manager
            
            db = get_db_manager()
            users_query = """
                SELECT id, username, full_name, role, active, last_login
                FROM users
                ORDER BY username
            """
            
            users = db.execute_query(users_query)
            
            # Clear existing items
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
                
            # Add users
            for user in users:
                status = "Active" if user['active'] else "Inactive"
                last_login = user['last_login'] or "Never"
                if last_login != "Never":
                    # Format datetime
                    last_login = last_login.split(' ')[0]  # Just date part
                    
                self.users_tree.insert("", "end", values=(
                    user['id'],
                    user['username'],
                    user['full_name'],
                    user['role'].title(),
                    status,
                    last_login
                ))
                
            # Update status if status bar exists
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Loaded {len(users)} users")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")
            
    def refresh_modules(self):
        """Refresh modules list"""
        try:
            available_modules = self.module_registry.get_available_modules()
            
            # Clear existing items
            for item in self.modules_tree.get_children():
                self.modules_tree.delete(item)
                
            # Add modules
            for module_id, module_info in available_modules.items():
                status = "Enabled" if module_info.enabled else "Disabled"
                
                self.modules_tree.insert("", "end", values=(
                    module_info.name,
                    module_info.version,
                    f"Tier {module_info.tier}",
                    status,
                    module_info.description
                ))
                
            # Update status if status bar exists
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Loaded {len(available_modules)} modules")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load modules: {str(e)}")
            
    def add_user(self):
        """Add new user"""
        dialog = UserEditDialog(self.root, self.auth_manager)
        if dialog.result:
            self.refresh_users()
            
    def edit_user(self):
        """Edit selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to edit")
            return
            
        user_values = self.users_tree.item(selection[0])['values']
        user_id = user_values[0]
        
        dialog = UserEditDialog(self.root, self.auth_manager, user_id)
        if dialog.result:
            self.refresh_users()
            
    def reset_password(self):
        """Reset user password"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to reset password")
            return
            
        user_values = self.users_tree.item(selection[0])['values']
        username = user_values[1]
        
        dialog = PasswordResetDialog(self.root, self.auth_manager, username)
        if dialog.result:
            messagebox.showinfo("Success", f"Password reset for user '{username}'")
            
    def deactivate_user(self):
        """Deactivate/activate selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to deactivate/activate")
            return
            
        user_values = self.users_tree.item(selection[0])['values']
        user_id = user_values[0]
        username = user_values[1]
        current_status = user_values[4]
        
        action = "activate" if current_status == "Inactive" else "deactivate"
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to {action} user '{username}'?"):
            try:
                from core.database.connection import get_db_manager
                
                db = get_db_manager()
                new_status = 1 if current_status == "Inactive" else 0
                
                query = "UPDATE users SET active = ? WHERE id = ?"
                if db.execute_update(query, (new_status, user_id)) > 0:
                    self.refresh_users()
                    self.status_label.config(text=f"User {action}d successfully")
                else:
                    messagebox.showerror("Error", f"Failed to {action} user")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to {action} user: {str(e)}")
                
    def install_module(self):
        """Install new module"""
        messagebox.showinfo("Coming Soon", "Module installation interface coming in next update")
        
    def toggle_module(self):
        """Enable/disable selected module"""
        selection = self.modules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a module to toggle")
            return
            
        messagebox.showinfo("Coming Soon", "Module enable/disable coming in next update")
        
    def show_module_info(self):
        """Show detailed module information"""
        selection = self.modules_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a module to view info")
            return
            
        module_values = self.modules_tree.item(selection[0])['values']
        module_name = module_values[0]
        
        info = f"""Module: {module_values[0]}
Version: {module_values[1]}
Tier: {module_values[2]}
Status: {module_values[3]}
Description: {module_values[4]}

Dependencies: (Feature coming soon)
Installation Date: (Feature coming soon)
"""
        
        messagebox.showinfo(f"Module Info - {module_name}", info)

class UserEditDialog:
    """Dialog for adding/editing users"""
    
    def __init__(self, parent, auth_manager, user_id=None):
        self.parent = parent
        self.auth_manager = auth_manager
        self.user_id = user_id
        self.result = None
        
        # Get user data if editing
        self.user_data = None
        if user_id:
            self.load_user_data()
            
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        
        if self.user_data:
            self.load_form_data()
            
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def setup_dialog(self):
        """Configure dialog window"""
        title = "Edit User" if self.user_id else "Add User"
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"400x350+{x}+{y}")
        
    def load_user_data(self):
        """Load existing user data"""
        try:
            from core.database.connection import get_db_manager
            
            db = get_db_manager()
            query = "SELECT * FROM users WHERE id = ?"
            result = db.execute_query(query, (self.user_id,))
            
            if result:
                self.user_data = result[0]
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user data: {str(e)}")
            
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = "Edit User" if self.user_id else "Add New User"
        title_label = ttk.Label(main_frame, text=title, font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # User form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        form_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Username
        ttk.Label(form_frame, text="Username *:").grid(row=row, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var)
        username_entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Full name
        ttk.Label(form_frame, text="Full Name *:").grid(row=row, column=0, sticky="w", pady=5)
        self.full_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.full_name_var).grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Role
        ttk.Label(form_frame, text="Role *:").grid(row=row, column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(form_frame, textvariable=self.role_var,
                                values=["admin", "pos_operator", "stock_manager"],
                                state="readonly")
        role_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
        row += 1
        
        # Password (only for new users)
        if not self.user_id:
            ttk.Label(form_frame, text="Password *:").grid(row=row, column=0, sticky="w", pady=5)
            self.password_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.password_var, show="*").grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
            row += 1
            
            ttk.Label(form_frame, text="Confirm Password *:").grid(row=row, column=0, sticky="w", pady=5)
            self.confirm_password_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=self.confirm_password_var, show="*").grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=5)
            row += 1
            
        # Active status
        ttk.Label(form_frame, text="Active:").grid(row=row, column=0, sticky="w", pady=5)
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, variable=self.active_var).grid(row=row, column=1, sticky="w", padx=(10, 0), pady=5)
        row += 1
        
        # Required fields note
        note_label = ttk.Label(form_frame, text="* Required fields", font=('Arial', 9), foreground='red')
        note_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        save_text = "Update" if self.user_id else "Create"
        ttk.Button(button_frame, text=save_text, command=self.save).pack(side=tk.RIGHT)
        
        # Focus on username
        username_entry.focus()
        
    def load_form_data(self):
        """Load user data into form"""
        if not self.user_data:
            return
            
        self.username_var.set(self.user_data['username'])
        self.full_name_var.set(self.user_data['full_name'])
        self.role_var.set(self.user_data['role'])
        self.active_var.set(bool(self.user_data['active']))
        
    def save(self):
        """Save user data"""
        try:
            username = self.username_var.get().strip()
            full_name = self.full_name_var.get().strip()
            role = self.role_var.get()
            active = self.active_var.get()
            
            # Validation
            if not username or not full_name or not role:
                messagebox.showerror("Validation Error", "All required fields must be filled")
                return
                
            if not self.user_id:  # New user
                password = self.password_var.get()
                confirm_password = self.confirm_password_var.get()
                
                if not password:
                    messagebox.showerror("Validation Error", "Password is required")
                    return
                    
                if password != confirm_password:
                    messagebox.showerror("Validation Error", "Passwords do not match")
                    return
                    
                if len(password) < 6:
                    messagebox.showerror("Validation Error", "Password must be at least 6 characters")
                    return
                    
            from core.database.connection import get_db_manager
            
            db = get_db_manager()
            
            if self.user_id:
                # Update existing user
                query = """
                    UPDATE users 
                    SET username = ?, full_name = ?, role = ?, active = ?
                    WHERE id = ?
                """
                params = (username, full_name, role, active, self.user_id)
            else:
                # Create new user
                password_hash = hash_password(password)
                query = """
                    INSERT INTO users (username, password_hash, full_name, role, active)
                    VALUES (?, ?, ?, ?, ?)
                """
                params = (username, password_hash, full_name, role, active)
                
            if db.execute_update(query, params) > 0:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save user")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {str(e)}")
            
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()

class PasswordResetDialog:
    """Dialog for resetting user password"""
    
    def __init__(self, parent, auth_manager, username):
        self.parent = parent
        self.auth_manager = auth_manager
        self.username = username
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        
        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
        
    def setup_dialog(self):
        """Configure dialog window"""
        self.dialog.title("Reset Password")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"350x200+{x}+{y}")
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Reset Password", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # User info
        user_label = ttk.Label(main_frame, text=f"User: {self.username}")
        user_label.pack(pady=(0, 20))
        
        # New password
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="New Password:").grid(row=0, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Label(form_frame, text="Confirm:").grid(row=1, column=0, sticky="w", pady=5)
        self.confirm_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.confirm_var, show="*").grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset", command=self.reset_password).pack(side=tk.RIGHT)
        
        # Focus on password
        password_entry.focus()
        
    def reset_password(self):
        """Reset the password"""
        try:
            password = self.password_var.get()
            confirm = self.confirm_var.get()
            
            if not password:
                messagebox.showerror("Error", "Password is required")
                return
                
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
                
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters")
                return
                
            from core.database.connection import get_db_manager
            
            db = get_db_manager()
            password_hash = hash_password(password)
            
            query = "UPDATE users SET password_hash = ? WHERE username = ?"
            if db.execute_update(query, (password_hash, self.username)) > 0:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to reset password")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset password: {str(e)}")
            
    def cancel(self):
        """Cancel dialog"""
        self.result = False
        self.dialog.destroy()

def main():
    """Main entry point for settings"""
    try:
        # Check if running standalone
        root = tk.Tk()
        root.withdraw()  # Hide root window
        
        # Initialize auth for testing
        from core.auth.authentication import ensure_demo_user, get_auth_manager
        ensure_demo_user()
        
        auth_manager = get_auth_manager()
        demo_user = auth_manager.authenticate_user("demo", "demo123")
        
        if demo_user:
            auth_manager.start_session(demo_user)
            app = SettingsWindow(user=demo_user)
            app.root.mainloop()
        else:
            messagebox.showerror("Error", "Failed to authenticate demo user")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start settings: {str(e)}")

if __name__ == "__main__":
    main()
