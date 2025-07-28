"""
GUI Launcher for Tembie's Spaza Shop POS System
Launches the graphical user interface
"""

import sys
import os
from tkinter import messagebox

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required components are available"""
    try:
        import tkinter as tk
        print(" Tkinter GUI framework available")
        
        from core.database.connection import get_db_manager
        print(" Database connection available")
        
        from core.products.management import ProductManager
        print(" Product management available")
        
        from core.sales.transaction import TransactionManager
        print(" Sales transaction system available")
        
        return True
    except ImportError as e:
        print(f" Missing dependency: {e}")
        return False
    except Exception as e:
        print(f" System error: {e}")
        return False

def initialize_system():
    """Initialize the POS system for GUI use"""
    try:
        from core.database.connection import get_db_manager
        from config.settings import get_settings_manager
        
        # Initialize database
        db = get_db_manager()
        print(" Database initialized")
        
        # Load settings
        settings_manager = get_settings_manager()
        settings = settings_manager.get_settings()
        print(f" Settings loaded for: {settings.shop_name}")
        
        return True
    except Exception as e:
        print(f" System initialization failed: {e}")
        return False

def create_demo_data():
    """Create demo data if database is empty"""
    try:
        from core.products.management import ProductManager
        from core.database.connection import get_db_manager
        from utils.helpers import hash_password
        
        db = get_db_manager()
        product_manager = ProductManager()
        
        # Check if we have products
        products = product_manager.get_all_products()
        if products:
            print(f" Found {len(products)} products in database")
            return True
        
        print("Creating demo data...")
        
        # Create demo user if not exists
        try:
            admin_password = hash_password("admin123")
            user_id = db.get_last_insert_id("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (?, ?, ?, ?)
            """, ("admin", admin_password, "admin", "System Administrator"))
            print(f" Created admin user (ID: {user_id})")
        except:
            # User might already exist
            result = db.execute_query("SELECT id FROM users WHERE username = ?", ("admin",))
            user_id = result[0]['id'] if result else 1
        
        # Create sample products
        from core.products.management import Product
        
        sample_products = [
            Product(name="Coca Cola 330ml", barcode="2000000001", category="Cooldrinks", 
                   cost_price=5.50, sell_price=8.00, current_stock=24, monthly_stock=144, min_stock=12),
            Product(name="White Bread 700g", barcode="2000000002", category="Food", 
                   cost_price=12.00, sell_price=15.50, current_stock=10, monthly_stock=60, min_stock=5),
            Product(name="Simba Chips 120g", barcode="2000000003", category="Sweets", 
                   cost_price=8.50, sell_price=12.00, current_stock=15, monthly_stock=90, min_stock=8),
            Product(name="2L Fresh Milk", barcode="2000000004", category="Food", 
                   cost_price=22.00, sell_price=28.50, current_stock=8, monthly_stock=48, min_stock=6),
            Product(name="Energade 500ml", barcode="2000000005", category="Cooldrinks", 
                   cost_price=8.00, sell_price=12.50, current_stock=18, monthly_stock=72, min_stock=10)
        ]
        
        created_count = 0
        for product in sample_products:
            try:
                existing = product_manager.get_product_by_barcode(product.barcode)
                if not existing:
                    product_id = product_manager.create_product(product, user_id)
                    print(f" Created product: {product.name} (ID: {product_id})")
                    created_count += 1
            except Exception as e:
                print(f"• Error creating {product.name}: {e}")
        
        print(f" Created {created_count} demo products")
        return True
        
    except Exception as e:
        print(f" Demo data creation failed: {e}")
        return False

def launch_gui():
    """Launch the main GUI application with authentication"""
    try:
        print("Starting authentication...")
        
        # Show login dialog
        from core.auth.authentication import show_login_dialog
        user = show_login_dialog()
        
        if not user:
            print("Login cancelled by user")
            return
        
        print(f" Authenticated: {user.full_name} ({user.role})")
        print("Launching GUI...")
        
        from core.ui.main_window import MainWindow
        
        app = MainWindow(user)
        print(" GUI started successfully")
        app.run()
        
    except Exception as e:
        error_msg = f"Failed to start GUI: {str(e)}"
        print(f" {error_msg}")
        
        # Show error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("GUI Error", error_msg)
            root.destroy()
        except:
            pass

def main():
    """Main entry point for GUI launcher"""
    print("=" * 60)
    print(" TEMBIE'S SPAZA SHOP - GUI LAUNCHER")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n Missing dependencies. Please check your installation.")
        input("Press Enter to exit...")
        return
    
    # Initialize system
    if not initialize_system():
        print("\n System initialization failed.")
        input("Press Enter to exit...")
        return
    
    # Create demo data if needed
    if not create_demo_data():
        print("\n️ Warning: Demo data creation failed, but GUI will still work.")
    
    print("\n Starting GUI Application...")
    print("-" * 60)
    
    # Launch GUI
    launch_gui()
    
    print("\n GUI application closed.")

if __name__ == "__main__":
    main()
