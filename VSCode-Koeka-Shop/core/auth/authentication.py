"""
User Authentication System for Tembie's Spaza Shop POS
Implementation of login, role-based access control, and session management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database.connection import get_db_manager
from utils.helpers import verify_password, hash_password
from utils.validation import validate_username, validate_password

class User:
    """User data class"""
    def __init__(self, user_id: int, username: str, full_name: str, role: str, active: bool = True):
        self.id = user_id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.active = active

class AuthenticationManager:
    """Manages user authentication and sessions"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.current_user: Optional[User] = None
        self.session_start_time: Optional[datetime] = None
        self.auto_logout_minutes = 30  # Default timeout
        
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        if not username or not password:
            return None
            
        # Get user from database
        query = """
            SELECT id, username, password_hash, full_name, role, active, last_login
            FROM users 
            WHERE username = ? AND active = 1
        """
        
        results = self.db.execute_query(query, (username,))
        
        if not results:
            return None
            
        user_data = results[0]
        
        # Verify password
        if not verify_password(password, user_data['password_hash']):
            return None
            
        # Update last login
        self._update_last_login(user_data['id'])
        
        # Create user object
        user = User(
            user_id=user_data['id'],
            username=user_data['username'],
            full_name=user_data['full_name'],
            role=user_data['role'],
            active=bool(user_data['active'])
        )
        
        return user
    
    def login(self, username: str, password: str) -> bool:
        """Login user and start session"""
        user = self.authenticate_user(username, password)
        
        if user:
            self.current_user = user
            self.session_start_time = datetime.now()
            self._log_login_attempt(username, True)
            return True
        else:
            self._log_login_attempt(username, False)
            return False
    
    def logout(self):
        """Logout current user and end session"""
        if self.current_user:
            self._log_logout()
            self.current_user = None
            self.session_start_time = None
    
    def start_session(self, user: User):
        """Start a new session for the authenticated user"""
        self.current_user = user
        self.session_start_time = datetime.now()
        self._log_login_attempt(user.username, True)
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in and session is valid"""
        if not self.current_user or not self.session_start_time:
            return False
            
        # Check session timeout
        session_duration = datetime.now() - self.session_start_time
        if session_duration.total_seconds() > (self.auto_logout_minutes * 60):
            self.logout()
            return False
            
        return True
    
    def refresh_session(self):
        """Refresh session timestamp"""
        if self.is_logged_in():
            self.session_start_time = datetime.now()
    
    def has_permission(self, required_role: str) -> bool:
        """Check if current user has required role permission"""
        if not self.is_logged_in():
            return False
            
        role_hierarchy = {
            'admin': 3,
            'stock_manager': 2,
            'pos_operator': 1
        }
        
        user_level = role_hierarchy.get(self.current_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def can_access_function(self, function_name: str) -> bool:
        """Check if user can access specific function"""
        if not self.is_logged_in():
            return False
            
        permissions = {
            'sales': ['admin', 'pos_operator', 'stock_manager'],
            'product_management': ['admin', 'stock_manager'],
            'stock_adjustment': ['admin', 'stock_manager'],
            'reports': ['admin'],
            'settings': ['admin'],
            'user_management': ['admin'],
            'void_transaction': ['admin'],
            'cash_management': ['admin', 'pos_operator']
        }
        
        allowed_roles = permissions.get(function_name, [])
        return self.current_user.role in allowed_roles
    
    def get_current_user(self) -> Optional[User]:
        """Get current logged in user"""
        if self.is_logged_in():
            return self.current_user
        return None
    
    def create_user(self, username: str, password: str, full_name: str, 
                   role: str, created_by: int) -> Optional[int]:
        """Create new user account"""
        # Validate inputs
        if not validate_username(username):
            raise ValueError("Invalid username format")
            
        if not validate_password(password):
            raise ValueError("Password must be at least 6 characters with letters and numbers")
            
        if role not in ['admin', 'pos_operator', 'stock_manager']:
            raise ValueError("Invalid role")
        
        # Check if username exists
        existing = self.db.execute_query("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            raise ValueError("Username already exists")
        
        # Hash password and create user
        password_hash = hash_password(password)
        
        query = """
            INSERT INTO users (username, password_hash, full_name, role, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        return self.db.get_last_insert_id(query, (username, password_hash, full_name, role))
    
    def change_password(self, user_id: int, current_password: str, 
                       new_password: str) -> bool:
        """Change user password"""
        # Get current user data
        user_data = self.db.execute_query(
            "SELECT password_hash FROM users WHERE id = ?", (user_id,)
        )
        
        if not user_data:
            return False
            
        # Verify current password
        if not verify_password(current_password, user_data[0]['password_hash']):
            return False
            
        # Validate new password
        if not validate_password(new_password):
            return False
            
        # Update password
        new_hash = hash_password(new_password)
        query = "UPDATE users SET password_hash = ? WHERE id = ?"
        
        return self.db.execute_update(query, (new_hash, user_id)) > 0
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        query = "UPDATE users SET active = 0 WHERE id = ?"
        return self.db.execute_update(query, (user_id,)) > 0
    
    def get_all_users(self) -> list:
        """Get all users (admin only)"""
        query = """
            SELECT id, username, full_name, role, active, created_at, last_login
            FROM users 
            ORDER BY username
        """
        return self.db.execute_query(query)
    
    def _update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        self.db.execute_update(query, (user_id,))
    
    def _log_login_attempt(self, username: str, success: bool):
        """Log login attempt for security audit"""
        # Create login_log table if it doesn't exist
        self.db.execute_update("""
            CREATE TABLE IF NOT EXISTS login_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        """)
        
        query = """
            INSERT INTO login_log (username, success, attempt_time)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """
        self.db.execute_update(query, (username, 1 if success else 0))
    
    def _log_logout(self):
        """Log user logout"""
        if self.current_user:
            # Update session duration in login_log
            pass

class LoginDialog:
    """Login dialog window"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.auth_manager = AuthenticationManager()
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title("Tembie's Spaza Shop - Login")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # Make modal
        if parent:
            self.dialog.transient(parent)
            self.dialog.grab_set()
        
        self.center_dialog()
        self.create_widgets()
        
        # Focus on username field
        self.username_entry.focus()
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 150
        else:
            x = (self.dialog.winfo_screenwidth() // 2) - 200
            y = (self.dialog.winfo_screenheight() // 2) - 150
            
        self.dialog.geometry(f"400x300+{x}+{y}")
    
    def create_widgets(self):
        """Create login form widgets"""
        main_frame = ttk.Frame(self.dialog, padding="30")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Logo/Title
        title_label = ttk.Label(main_frame, text="🏪 Tembie's Spaza Shop", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Point of Sale System", 
                                  font=('Arial', 10))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=2, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, 
                                       font=('Arial', 12), width=20)
        self.username_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=3, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                       show="*", font=('Arial', 12), width=20)
        self.password_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        ttk.Button(button_frame, text="Login", command=self.login, 
                  style='Large.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Quick access info
        info_frame = ttk.LabelFrame(main_frame, text="Demo Access", padding="10")
        info_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=20)
        
        ttk.Label(info_frame, text="Username: demo", font=('Arial', 9)).pack(anchor="w")
        ttk.Label(info_frame, text="Password: demo123", font=('Arial', 9)).pack(anchor="w")
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Attempt login"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password")
            return
        
        # Clear status
        self.status_label.config(text="Logging in...")
        self.dialog.update()
        
        # Attempt authentication
        if self.auth_manager.login(username, password):
            self.result = self.auth_manager.get_current_user()
            self.dialog.destroy()
        else:
            self.status_label.config(text="Invalid username or password")
            self.password_var.set("")  # Clear password
            self.password_entry.focus()
    
    def cancel(self):
        """Cancel login"""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[User]:
        """Show login dialog and return authenticated user"""
        self.dialog.mainloop()
        return self.result

# Global authentication manager
_auth_manager = None

def get_auth_manager() -> AuthenticationManager:
    """Get global authentication manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager

def ensure_demo_user():
    """Ensure demo user exists for testing"""
    auth_manager = get_auth_manager()
    
    # Check if demo user exists
    db = get_db_manager()
    existing = db.execute_query("SELECT id FROM users WHERE username = ?", ("demo",))
    
    if not existing:
        # Create demo user
        try:
            auth_manager.create_user("demo", "demo123", "Demo User", "admin", 1)
            print("✓ Demo user created (username: demo, password: demo123)")
        except Exception as e:
            print(f"Warning: Could not create demo user: {e}")

def show_login_dialog(parent=None) -> Optional[User]:
    """Show login dialog and return authenticated user"""
    ensure_demo_user()
    login_dialog = LoginDialog(parent)
    return login_dialog.show()

def test_authentication():
    """Test authentication system"""
    print("🔐 Testing Authentication System")
    print("=" * 40)
    
    ensure_demo_user()
    auth_manager = get_auth_manager()
    
    # Test login
    print("Testing login...")
    if auth_manager.login("demo", "demo123"):
        user = auth_manager.get_current_user()
        print(f"✓ Login successful: {user.full_name} ({user.role})")
        
        # Test permissions
        print("Testing permissions...")
        print(f"  Can access sales: {auth_manager.can_access_function('sales')}")
        print(f"  Can access settings: {auth_manager.can_access_function('settings')}")
        print(f"  Can manage products: {auth_manager.can_access_function('product_management')}")
        
        # Test session
        print("Testing session...")
        print(f"  Is logged in: {auth_manager.is_logged_in()}")
        
        # Test logout
        auth_manager.logout()
        print(f"  After logout: {auth_manager.is_logged_in()}")
        
    else:
        print("✗ Login failed")

if __name__ == "__main__":
    test_authentication()
