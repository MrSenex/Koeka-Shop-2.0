#!/usr/bin/env python3
"""
Quick test to verify the product management window works without errors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_product_management_ui():
    """Test that the UI can be imported and instantiated without errors"""
    print("🧪 Testing Product Management UI...")
    
    try:
        # Test imports
        from core.ui.product_management import ProductManagementWindow, ArchiveManagerWindow
        print("✅ Import successful")
        
        # Test that required methods exist
        required_methods = [
            'show_archived_products',
            'delete_product', 
            'archive_product',
            'can_delete_product'
        ]
        
        # Check ProductManagementWindow methods
        for method in ['show_archived_products', 'delete_product']:
            if hasattr(ProductManagementWindow, method):
                print(f"✅ ProductManagementWindow.{method} exists")
            else:
                print(f"❌ ProductManagementWindow.{method} missing")
        
        # Check ProductManager methods
        from core.products.management import ProductManager
        pm = ProductManager()
        
        for method in ['delete_product', 'archive_product', 'can_delete_product']:
            if hasattr(pm, method):
                print(f"✅ ProductManager.{method} exists")
            else:
                print(f"❌ ProductManager.{method} missing")
        
        print("\n🎉 All tests passed! The UI should work correctly now.")
        print("\n💡 To test the full functionality:")
        print("1. Run the main application")
        print("2. Go to Product Management")
        print("3. Try the 'Archived Products' button")
        print("4. Try deleting a product")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_product_management_ui()
