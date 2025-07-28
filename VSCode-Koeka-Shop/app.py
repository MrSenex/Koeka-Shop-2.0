"""
Main Application Entry Point with Authentication
Proper application launcher for Tembie's Spaza Shop POS System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.auth.authentication import AuthenticationManager, get_auth_manager
from core.ui.main_window import MainWindow
from config.settings import get_settings_manager

class LoginScreen:
    """Login screen for user authentication"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.auth_manager = get_auth_manager()
        self.settings_manager = get_settings_manager()
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure login window"""
        settings = self.settings_manager.get_settings()
        self.root.title(f"{settings.shop_name} - Login")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        self.root.geometry(f"500x450+{x}+{y}")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12))
        style.configure('Login.TButton', font=('Arial', 12, 'bold'), padding=10)
        
    def create_widgets(self):
        """Create and layout login widgets"""
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Shop logo/header
        settings = self.settings_manager.get_settings()
        title_label = ttk.Label(main_frame, text="", font=('Arial', 52))
        title_label.pack(pady=(0, 15))
        
        shop_label = ttk.Label(main_frame, text=settings.shop_name, style='Title.TLabel')
        shop_label.pack(pady=(0, 8))
        
        subtitle_label = ttk.Label(main_frame, text="Point of Sale System", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 35))
        
        # Login form
        login_frame = ttk.Frame(main_frame)
        login_frame.pack(fill=tk.X)
        
        # Username
        ttk.Label(login_frame, text="Username:", font=('Arial', 11)).pack(anchor='w', pady=(0, 8))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(login_frame, textvariable=self.username_var, font=('Arial', 12))
        self.username_entry.pack(fill=tk.X, pady=(0, 18), ipady=5)
        
        # Password
        ttk.Label(login_frame, text="Password:", font=('Arial', 11)).pack(anchor='w', pady=(0, 8))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_frame, textvariable=self.password_var, 
                                      show="*", font=('Arial', 12))
        self.password_entry.pack(fill=tk.X, pady=(0, 25), ipady=5)
        
        # Login button
        login_btn = ttk.Button(login_frame, text="Login", command=self.login, style='Login.TButton')
        login_btn.pack(fill=tk.X, pady=(0, 18))
        
        # Status label
        self.status_label = ttk.Label(login_frame, text="", foreground='red', font=('Arial', 10))
        self.status_label.pack()
        
        # Demo credentials info
        demo_frame = ttk.Frame(main_frame)
        demo_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(demo_frame, text="Demo Credentials:", font=('Arial', 10, 'bold')).pack()
        ttk.Label(demo_frame, text="Username: admin | Password: admin123", 
                 font=('Arial', 9), foreground='gray').pack()
        ttk.Label(demo_frame, text="Username: demo | Password: demo123", 
                 font=('Arial', 9), foreground='gray').pack()
        
        # Bind Enter key to login
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Focus on username
        self.username_entry.focus()
        
    def login(self):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password")
            return
        
        try:
            # Attempt authentication
            user = self.auth_manager.authenticate_user(username, password)
            
            if user:
                # Successful login
                self.status_label.config(text="Login successful...", foreground='green')
                self.root.update()
                
                # Start user session
                self.auth_manager.start_session(user)
                
                # Close login window and open main application
                self.root.destroy()
                self.open_main_application(user)
            else:
                self.status_label.config(text="Invalid username or password", foreground='red')
                self.password_var.set("")  # Clear password
                
        except Exception as e:
            self.status_label.config(text=f"Login error: {str(e)}", foreground='red')
            print(f"Login error: {e}")
            
    def open_main_application(self, user):
        """Open main application window"""
        try:
            main_app = MainWindow(user)
            main_app.run()
        except Exception as e:
            messagebox.showerror("Application Error", 
                               f"Failed to start main application: {str(e)}")
            print(f"Main app error: {e}")
            
    def run(self):
        """Start the login screen"""
        self.root.mainloop()

def initialize_demo_users():
    """Ensure demo users exist for testing"""
    try:
        from core.auth.authentication import ensure_demo_user, create_default_admin
        
        # Create default admin if not exists
        create_default_admin()
        
        # Create demo user if not exists  
        ensure_demo_user()
        
        print(" Demo users initialized")
        return True
    except Exception as e:
        print(f" Failed to initialize demo users: {e}")
        return False

def check_system_requirements():
    """Check if system is properly initialized"""
    try:
        from core.database.connection import get_db_manager
        
        # Test database connection
        db = get_db_manager()
        
        # Test basic tables exist
        result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in result]
        
        required_tables = ['users', 'products', 'sales', 'sale_items', 'stock_movements', 'daily_cash']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f" Missing database tables: {missing_tables}")
            return False
            
        print(" Database system ready")
        return True
        
    except Exception as e:
        print(f" System check failed: {e}")
        return False

def main():
    """Main application entry point with proper authentication flow"""
    print(" Starting Tembie's Spaza Shop POS System...")
    
    # Check system requirements
    if not check_system_requirements():
        print(" System requirements not met. Please run 'python main.py' first to initialize.")
        input("Press Enter to exit...")
        return
    
    # Initialize demo users
    if not initialize_demo_users():
        print("️ Warning: Demo users could not be created. Manual user creation may be required.")
    
    try:
        # Start login screen
        login_app = LoginScreen()
        login_app.run()
        
    except KeyboardInterrupt:
        print("\n Application closed by user")
    except Exception as e:
        print(f" Application error: {e}")
        messagebox.showerror("System Error", 
                           f"Failed to start application: {str(e)}\n\n"
                           f"Please check the console for more details.")

if __name__ == "__main__":
    main()
