"""
Test Authentication Integration
Verify authentication works with GUI components
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_integration():
    """Test authentication integration"""
    print(" Testing Authentication Integration")
    print("=" * 50)
    
    try:
        # Test imports
        from core.auth.authentication import (
            AuthenticationManager, 
            User, 
            ensure_demo_user,
            get_auth_manager
        )
        print(" Authentication modules imported")
        
        # Ensure demo user exists
        ensure_demo_user()
        print(" Demo user ensured")
        
        # Test authentication manager
        auth_manager = get_auth_manager()
        
        # Test login
        if auth_manager.login("demo", "demo123"):
            user = auth_manager.get_current_user()
            print(f" Login successful: {user.full_name}")
            
            # Test permissions
            print("\n Permission Tests:")
            permissions = [
                ('sales', 'Sales transactions'),
                ('product_management', 'Product management'),
                ('reports', 'View reports'),
                ('settings', 'System settings'),
                ('user_management', 'User management')
            ]
            
            for perm, desc in permissions:
                can_access = auth_manager.can_access_function(perm)
                status = "" if can_access else ""
                print(f"  {status} {desc}: {can_access}")
            
            # Test role hierarchy
            print(f"\n User Role: {user.role}")
            print(f" Has admin permissions: {auth_manager.has_permission('admin')}")
            
            auth_manager.logout()
            print(" Logout successful")
            
        else:
            print(" Login failed")
            return False
        
        # Test with different roles
        print("\n Testing Different User Roles:")
        
        # Create test users
        test_users = [
            ("operator", "operator123", "POS Operator", "pos_operator"),
            ("stockmgr", "manager123", "Stock Manager", "stock_manager")
        ]
        
        for username, password, full_name, role in test_users:
            try:
                user_id = auth_manager.create_user(username, password, full_name, role, 1)
                print(f" Created {role}: {username}")
                
                # Test login
                if auth_manager.login(username, password):
                    user = auth_manager.get_current_user()
                    can_sales = auth_manager.can_access_function('sales')
                    can_reports = auth_manager.can_access_function('reports')
                    print(f"  - {user.full_name}: Sales={can_sales}, Reports={can_reports}")
                    auth_manager.logout()
                
            except ValueError as e:
                if "already exists" in str(e):
                    print(f"️ User {username} already exists")
                else:
                    print(f" Error creating {username}: {e}")
        
        print("\n Authentication integration test completed!")
        return True
        
    except Exception as e:
        print(f" Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_auth_integration()
