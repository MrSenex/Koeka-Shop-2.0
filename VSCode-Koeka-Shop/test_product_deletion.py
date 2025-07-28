#!/usr/bin/env python3
"""
Test script for product deletion functionality
Demonstrates the new delete, archive, and restore features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.products.management import ProductManager, Product
from core.auth.authentication import ensure_demo_user, get_auth_manager
from datetime import date, datetime

def test_product_deletion():
    """Test the product deletion functionality"""
    print("=== Testing Product Deletion Functionality ===\n")
    
    # Setup authentication
    ensure_demo_user()
    auth_manager = get_auth_manager()
    demo_user = auth_manager.authenticate_user("demo", "demo123")
    
    if not demo_user:
        print("❌ Failed to authenticate demo user")
        return
    
    auth_manager.start_session(demo_user)
    print(f"✅ Authenticated as: {demo_user.username}")
    
    # Initialize product manager
    pm = ProductManager()
    
    # Test 1: Create a test product
    print("\n1. Creating test product...")
    test_product = Product(
        name="Test Delete Product",
        barcode="DELETE123",
        category="Other",
        cost_price=10.0,
        sell_price=15.0,
        current_stock=50,
        monthly_stock=100,
        min_stock=5
    )
    
    try:
        product_id = pm.create_product(test_product, demo_user.id)
        print(f"✅ Created product with ID: {product_id}")
    except Exception as e:
        print(f"❌ Failed to create product: {e}")
        return
    
    # Test 2: Check deletion constraints for new product
    print("\n2. Checking deletion constraints...")
    delete_info = pm.can_delete_product(product_id)
    print(f"Can delete: {delete_info['can_delete']}")
    print(f"Sales count: {delete_info['sales_count']}")
    print(f"Movements count: {delete_info['movements_count']}")
    print(f"Current stock: {delete_info['current_stock']}")
    print(f"Recommendation: {delete_info['recommendation']}")
    
    # Test 3: Delete the product (should work as it has no sales)
    if delete_info['can_delete']:
        print("\n3. Deleting product (safe deletion)...")
        try:
            success = pm.delete_product(product_id, demo_user.id)
            if success:
                print("✅ Product deleted successfully")
            else:
                print("❌ Failed to delete product")
        except Exception as e:
            print(f"❌ Error deleting product: {e}")
    else:
        print("\n3. Skipping deletion - product has constraints")
    
    # Test 4: Create another product for archiving
    print("\n4. Creating product for archiving test...")
    archive_product = Product(
        name="Test Archive Product",
        barcode="ARCHIVE123",
        category="Food",
        cost_price=5.0,
        sell_price=8.0,
        current_stock=25,
        monthly_stock=50,
        min_stock=3
    )
    
    try:
        archive_product_id = pm.create_product(archive_product, demo_user.id)
        print(f"✅ Created product for archiving with ID: {archive_product_id}")
    except Exception as e:
        print(f"❌ Failed to create archive product: {e}")
        return
    
    # Test 5: Archive the product
    print("\n5. Archiving product...")
    try:
        success = pm.archive_product(archive_product_id, demo_user.id)
        if success:
            print("✅ Product archived successfully")
        else:
            print("❌ Failed to archive product")
    except Exception as e:
        print(f"❌ Error archiving product: {e}")
    
    # Test 6: List archived products
    print("\n6. Listing archived products...")
    try:
        archived = pm.get_archived_products()
        print(f"Found {len(archived)} archived products:")
        for product in archived:
            print(f"  - {product.name} (ID: {product.id})")
    except Exception as e:
        print(f"❌ Error listing archived products: {e}")
    
    # Test 7: Check all products excludes archived by default
    print("\n7. Checking active products list...")
    try:
        active_products = pm.get_all_products(include_archived=False)
        archived_names = [p.name for p in active_products if p.name == "Test Archive Product"]
        if not archived_names:
            print("✅ Archived product correctly excluded from active list")
        else:
            print("❌ Archived product still appears in active list")
    except Exception as e:
        print(f"❌ Error checking active products: {e}")
    
    # Test 8: Restore archived product
    print("\n8. Restoring archived product...")
    try:
        success = pm.restore_product(archive_product_id, demo_user.id)
        if success:
            print("✅ Product restored successfully")
            
            # Verify it's back in active list
            active_products = pm.get_all_products(include_archived=False)
            restored_names = [p.name for p in active_products if p.name == "Test Archive Product"]
            if restored_names:
                print("✅ Restored product appears in active list")
            else:
                print("❌ Restored product not found in active list")
        else:
            print("❌ Failed to restore product")
    except Exception as e:
        print(f"❌ Error restoring product: {e}")
    
    # Test 9: Clean up - delete the test product
    print("\n9. Cleaning up test products...")
    try:
        # Get all products including archived
        all_products = pm.get_all_products(include_archived=True)
        test_products = [p for p in all_products if p.name.startswith("Test")]
        
        for product in test_products:
            try:
                pm.delete_product(product.id, demo_user.id, force=True)
                print(f"✅ Cleaned up: {product.name}")
            except Exception as e:
                print(f"❌ Failed to clean up {product.name}: {e}")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    
    print("\n=== Product Deletion Test Complete ===")

def demo_usage():
    """Demonstrate typical usage scenarios"""
    print("\n=== Usage Examples ===\n")
    
    print("Typical deletion workflow:")
    print("1. User selects product to delete")
    print("2. System checks: pm.can_delete_product(product_id)")
    print("3. If safe to delete: pm.delete_product(product_id, user_id)")
    print("4. If has constraints: offer archive option")
    print("5. Archive: pm.archive_product(product_id, user_id)")
    print("6. View archived: pm.get_archived_products()")
    print("7. Restore if needed: pm.restore_product(product_id, user_id)")

if __name__ == "__main__":
    test_product_deletion()
    demo_usage()
