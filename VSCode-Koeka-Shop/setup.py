#!/usr/bin/env python3
"""
Quick Setup Script for Tembie's Spaza Shop POS System
Automates the installation and initial setup process
"""

import os
import sys
import subprocess
import platform

def print_header():
    print("=" * 60)
    print("TEMBIE'S SPAZA SHOP POS SYSTEM - QUICK SETUP")
    print("=" * 60)
    print("Setting up your Point of Sale system...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"Python {version.major}.{version.minor}.{version.micro} - Too old")
        print("   Please install Python 3.8 or newer")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling dependencies...")
    try:
        # Check if requirements.txt exists
        if not os.path.exists("requirements.txt"):
            print("requirements.txt not found - creating minimal requirements")
            with open("requirements.txt", "w") as f:
                f.write("python-dotenv>=1.0.0\n")
        
        # Install requirements
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Dependencies installed successfully")
            return True
        else:
            print(f"Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def test_system():
    """Test core system functionality"""
    print("\nTesting system functionality...")
    try:
        # Test database initialization
        from core.database.connection import get_db_manager
        db = get_db_manager()
        print("Database connection - OK")
        
        # Test authentication
        from core.auth.authentication import get_auth_manager
        auth = get_auth_manager()
        print("Authentication system - OK")
        
        # Test transaction engine
        from core.sales.transaction import SalesManager
        sales = SalesManager()
        print("Sales transaction engine - OK")
        
        # Test product management
        from core.products.management import ProductManager
        products = ProductManager()
        print("Product management - OK")
        
        print("All core systems operational!")
        return True
        
    except Exception as e:
        print(f"System test failed: {e}")
        return False

def create_sample_data():
    """Create sample products and users for testing"""
    print("\nSetting up sample data...")
    try:
        from core.products.management import ProductManager
        from core.auth.authentication import get_auth_manager
        
        # Create sample products
        product_manager = ProductManager()
        
        sample_products = [
            {
                "name": "Coca Cola 330ml",
                "barcode": "123456789001",
                "category": "Cooldrinks",
                "cost_price": 8.50,
                "sell_price": 12.00,
                "current_stock": 50,
                "min_stock": 10
            },
            {
                "name": "White Bread 700g",
                "barcode": "123456789002", 
                "category": "Food",
                "cost_price": 12.00,
                "sell_price": 16.00,
                "current_stock": 20,
                "min_stock": 5
            },
            {
                "name": "2 Minute Noodles",
                "barcode": "123456789003",
                "category": "Food", 
                "cost_price": 3.50,
                "sell_price": 5.00,
                "current_stock": 100,
                "min_stock": 20
            }
        ]
        
        for product in sample_products:
            try:
                product_manager.add_product(**product)
                print(f"   Added: {product['name']}")
            except:
                # Product might already exist
                pass
                
        print("Sample products added")
        return True
        
    except Exception as e:
        print(f"Could not create sample data: {e}")
        return False

def show_completion_info():
    """Show completion information and next steps"""
    print("\nSETUP COMPLETE!")
    print("=" * 60)
    print("\nNEXT STEPS:")
    print()
    print("1. Start the application:")
    print("   python app.py")
    print()
    print("2. Login with demo credentials:")
    print("   Admin: admin / admin123")
    print("   POS:   demo / demo123")
    print()
    print("3. Configure your shop:")
    print("   - Go to Settings → Business")
    print("   - Update shop name and details")
    print("   - Add your products")
    print()
    print("4. Training resources:")
    print("   - Read INSTALLATION_GUIDE.md")
    print("   - Try CLI demo: python demo_cli.py")
    print("   - Run tests: python test_core_functionality.py")
    print()
    print("NEED HELP?")
    print("   - Check error messages")
    print("   - Refer to INSTALLATION_GUIDE.md")
    print("   - Restart the application")
    print()
    print("DAILY BACKUP REMINDER:")
    print("   Copy 'spaza_shop.db' file to USB/cloud storage")
    print()

def main():
    """Main setup process"""
    print_header()
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\nSetup failed at dependency installation")
        sys.exit(1)
    
    # Test system
    if not test_system():
        print("\nSetup failed at system testing")
        sys.exit(1)
    
    # Create sample data
    create_sample_data()
    
    # Show completion info
    show_completion_info()

if __name__ == "__main__":
    main()
