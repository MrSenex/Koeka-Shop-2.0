"""
Test script for the new GUI interfaces
Run this to test all the new administrative GUI components
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_login_screen():
    """Test the login screen"""
    print("Testing Login Screen...")
    try:
        from app import LoginScreen
        
        root = tk.Tk()
        root.withdraw()  # Hide root
        
        login = LoginScreen()
        return True
        
    except Exception as e:
        print(f"Login Screen Error: {e}")
        return False

def test_main_dashboard():
    """Test the main dashboard with admin user"""
    print("Testing Main Dashboard...")
    try:
        from core.auth.authentication import ensure_demo_user, get_auth_manager
        from core.ui.main_window import MainWindow
        
        # Ensure demo user exists
        ensure_demo_user()
        
        # Authenticate admin user
        auth_manager = get_auth_manager()
        admin_user = auth_manager.authenticate_user("admin", "admin123")
        
        if admin_user:
            auth_manager.start_session(admin_user)
            
            # Test main window
            root = tk.Tk()
            root.withdraw()
            
            app = MainWindow(user=admin_user)
            print(" Main Dashboard loaded successfully")
            
            # Don't actually show - just test creation
            root.destroy()
            return True
        else:
            print(" Failed to authenticate admin user")
            return False
            
    except Exception as e:
        print(f"Main Dashboard Error: {e}")
        return False

def test_product_management():
    """Test product management GUI"""
    print("Testing Product Management...")
    try:
        from core.auth.authentication import ensure_demo_user, get_auth_manager
        from core.ui.product_management import ProductManagementWindow
        
        # Setup auth
        ensure_demo_user()
        auth_manager = get_auth_manager()
        admin_user = auth_manager.authenticate_user("admin", "admin123")
        auth_manager.start_session(admin_user)
        
        # Test product management
        root = tk.Tk()
        root.withdraw()
        
        app = ProductManagementWindow(user=admin_user)
        print(" Product Management loaded successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"Product Management Error: {e}")
        return False

def test_reports_window():
    """Test reports and cash management GUI"""
    print("Testing Reports Window...")
    try:
        from core.auth.authentication import ensure_demo_user, get_auth_manager
        from core.ui.reports_window import ReportsWindow
        
        # Setup auth
        ensure_demo_user()
        auth_manager = get_auth_manager()
        admin_user = auth_manager.authenticate_user("admin", "admin123")
        auth_manager.start_session(admin_user)
        
        # Test reports
        root = tk.Tk()
        root.withdraw()
        
        app = ReportsWindow(user=admin_user)
        print(" Reports Window loaded successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"Reports Window Error: {e}")
        return False

def test_settings_window():
    """Test settings GUI"""
    print("Testing Settings Window...")
    try:
        from core.auth.authentication import ensure_demo_user, get_auth_manager
        from core.ui.settings_window import SettingsWindow
        
        # Setup auth
        ensure_demo_user()
        auth_manager = get_auth_manager()
        admin_user = auth_manager.authenticate_user("admin", "admin123")
        auth_manager.start_session(admin_user)
        
        # Test settings
        root = tk.Tk()
        root.withdraw()
        
        app = SettingsWindow(user=admin_user)
        print(" Settings Window loaded successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"Settings Window Error: {e}")
        return False

def test_sales_screen():
    """Test the existing sales screen"""
    print("Testing Sales Screen...")
    try:
        from core.auth.authentication import ensure_demo_user, get_auth_manager
        from core.ui.sales_screen import SalesScreen
        
        # Setup auth
        ensure_demo_user()
        auth_manager = get_auth_manager()
        pos_user = auth_manager.authenticate_user("demo", "demo123")
        auth_manager.start_session(pos_user)
        
        # Test sales screen
        root = tk.Tk()
        root.withdraw()
        
        app = SalesScreen(user=pos_user)
        print(" Sales Screen loaded successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"Sales Screen Error: {e}")
        return False

def main():
    """Run all GUI tests"""
    print("=" * 50)
    print(" TESTING ALL GUI INTERFACES")
    print("=" * 50)
    
    tests = [
        ("Login Screen", test_login_screen),
        ("Main Dashboard", test_main_dashboard),
        ("Product Management", test_product_management),
        ("Reports Window", test_reports_window),
        ("Settings Window", test_settings_window),
        ("Sales Screen", test_sales_screen),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f" {test_name} - PASSED")
            else:
                print(f" {test_name} - FAILED")
        except Exception as e:
            print(f" {test_name} - ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print(" TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = " PASS" if success else " FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print(" ALL TESTS PASSED! GUI interfaces are ready.")
        print("\n TO START THE APPLICATION:")
        print("   python app.py")
        print("\n Demo Credentials:")
        print("   Admin: admin/admin123")
        print("   POS User: demo/demo123")
    else:
        print(f"️  {total - passed} tests failed. Check errors above.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
