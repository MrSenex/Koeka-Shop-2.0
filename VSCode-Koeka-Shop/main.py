"""
Point of Sale System for Tembie's Spaza Shop
Main application entry point

See functional_specification_complete.md for requirements.
"""

import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import sqlite3
        print("✓ SQLite3 available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

def initialize_system():
    """Initialize the POS system"""
    try:
        from core.database.connection import get_db_manager
        from config.settings import get_settings_manager
        
        print("Initializing Tembie's Spaza Shop POS System...")
        
        # Initialize database
        db = get_db_manager()
        print("✓ Database initialized")
        
        # Load settings
        settings_manager = get_settings_manager()
        settings = settings_manager.get_settings()
        print(f"✓ Settings loaded for: {settings.shop_name}")
        
        return True
    except Exception as e:
        print(f"✗ System initialization failed: {e}")
        return False

def show_welcome_screen():
    """Display welcome screen with system status"""
    print("=" * 60)
    print("🏪 TEMBIE'S SPAZA SHOP - POINT OF SALE SYSTEM")
    print("=" * 60)
    print(f"System Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: SQLite (Embedded)")
    print(f"Status: Core System Ready")
    print("=" * 60)
    print()
    
    print("CORE FEATURES IMPLEMENTED:")
    print("✓ Database Schema & Connection Management")
    print("✓ Product Management (CRUD, Stock Tracking)")
    print("✓ Sales Transaction Processing")
    print("✓ Receipt Generation (Screen Display)")
    print("✓ Payment Processing (Cash, Card, Mixed)")
    print("✓ Stock Movement Audit Trail")
    print("✓ VAT Calculations")
    print("✓ Data Validation & Security")
    print()
    
    print("NEXT DEVELOPMENT PHASE:")
    print("• User Management & Authentication")
    print("• Tkinter GUI Interface")
    print("• Daily Cash Management")
    print("• Reporting System")
    print("• Barcode Scanner Integration")
    print()
    
    print("TO TEST CORE FUNCTIONALITY:")
    print("  python test_core_functionality.py")
    print()
    
    print("FOR FULL IMPLEMENTATION DETAILS:")
    print("  See functional_specification_complete.md")
    print("=" * 60)

def run_demo_mode():
    """Run basic demo to show functionality"""
    try:
        from core.products.management import ProductManager, Product
        from core.sales.transaction import TransactionManager
        from utils.helpers import hash_password
        from core.database.connection import get_db_manager
        
        print("DEMO MODE - Creating sample data...")
        
        # Create demo user
        db = get_db_manager()
        admin_password = hash_password("demo123")
        
        try:
            user_id = db.get_last_insert_id("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (?, ?, ?, ?)
            """, ("demo", admin_password, "admin", "Demo User"))
            print(f"✓ Created demo user (ID: {user_id})")
        except:
            # User might already exist
            result = db.execute_query("SELECT id FROM users WHERE username = ?", ("demo",))
            user_id = result[0]['id'] if result else 1
        
        # Create sample products
        product_manager = ProductManager()
        
        sample_products = [
            Product(name="Coca Cola 330ml", barcode="2000000001", category="Cooldrinks", 
                   cost_price=5.50, sell_price=8.00, current_stock=24, monthly_stock=144, min_stock=12),
            Product(name="White Bread 700g", barcode="2000000002", category="Food", 
                   cost_price=12.00, sell_price=15.50, current_stock=10, monthly_stock=60, min_stock=5),
            Product(name="Simba Chips 120g", barcode="2000000003", category="Sweets", 
                   cost_price=8.50, sell_price=12.00, current_stock=15, monthly_stock=90, min_stock=8)
        ]
        
        for product in sample_products:
            try:
                existing = product_manager.get_product_by_barcode(product.barcode)
                if not existing:
                    product_id = product_manager.create_product(product, user_id)
                    print(f"✓ Created product: {product.name} (ID: {product_id})")
                else:
                    print(f"• Product already exists: {product.name}")
            except Exception as e:
                print(f"• Error creating {product.name}: {e}")
        
        print("✓ Demo data ready!")
        print("\nYou can now:")
        print("1. Run test_core_functionality.py to see the system in action")
        print("2. Examine the database file: spaza_shop.db")
        print("3. Start developing the GUI interface")
        
        return True
    except Exception as e:
        print(f"Demo mode failed: {e}")
        return False

def main():
    """Main application entry point"""
    if not check_dependencies():
        print("Please install required dependencies and try again.")
        return
    
    if not initialize_system():
        print("System initialization failed. Please check the error messages above.")
        return
    
    show_welcome_screen()
    
    # Ask if user wants to run demo
    try:
        response = input("Create sample data for testing? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            run_demo_mode()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
