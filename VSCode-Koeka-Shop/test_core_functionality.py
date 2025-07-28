"""
Test script to verify core POS functionality
This script tests the database, product management, and sales processing
"""

import os
import sys
from datetime import datetime, date

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database.connection import get_db_manager
from core.products.management import ProductManager, Product
from core.sales.transaction import TransactionManager
from core.sales.receipt import ReceiptGenerator
from utils.helpers import hash_password

def test_database_initialization():
    """Test database initialization"""
    print("Testing database initialization...")
    
    try:
        db = get_db_manager()
        # Try a simple query
        result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in result]
        
        expected_tables = ['products', 'users', 'sales', 'sale_items', 'stock_movements', 'daily_cash', 'system_config']
        
        for table in expected_tables:
            if table in tables:
                print(f" Table '{table}' exists")
            else:
                print(f" Table '{table}' missing")
                return False
        
        print(" Database initialization successful")
        return True
    except Exception as e:
        print(f" Database initialization failed: {e}")
        return False

def test_product_management():
    """Test product management functionality"""
    print("\nTesting product management...")
    
    try:
        # Create admin user first (needed for stock movements)
        db = get_db_manager()
        admin_password = hash_password("admin123")
        
        db.execute_update("""
            INSERT OR IGNORE INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        """, ("admin", admin_password, "admin", "System Administrator"))
        
        # Get admin user ID
        admin_result = db.execute_query("SELECT id FROM users WHERE username = ?", ("admin",))
        admin_id = admin_result[0]['id'] if admin_result else 1
        
        product_manager = ProductManager()
        
        # Create test product
        import time
        unique_barcode = f"123456789012{int(time.time()) % 10000}"  # Make barcode unique
        
        test_product = Product(
            name="Test Cola 330ml",
            barcode=unique_barcode,
            category="Cooldrinks",
            cost_price=5.50,
            sell_price=8.00,
            current_stock=50,
            monthly_stock=100,
            min_stock=10,
            vat_rate=15.0,
            vat_inclusive=True
        )
        
        product_id = product_manager.create_product(test_product, admin_id)
        print(f" Created product with ID: {product_id}")
        
        # Test product retrieval
        retrieved_product = product_manager.get_product_by_id(product_id)
        if retrieved_product and retrieved_product.name == "Test Cola 330ml":
            print(" Product retrieval successful")
        else:
            print(" Product retrieval failed")
            return False
        
        # Test barcode search
        barcode_product = product_manager.get_product_by_barcode(unique_barcode)
        if barcode_product and barcode_product.id == product_id:
            print(" Barcode search successful")
        else:
            print(" Barcode search failed")
            return False
        
        # Test stock adjustment
        if product_manager.adjust_stock(product_id, -5, "adjustment", admin_id, "Test adjustment"):
            print(" Stock adjustment successful")
        else:
            print(" Stock adjustment failed")
            return False
        
        return True
    except Exception as e:
        print(f" Product management test failed: {e}")
        return False

def test_sales_processing():
    """Test sales transaction processing"""
    print("\nTesting sales processing...")
    
    try:
        # Get admin user ID
        db = get_db_manager()
        admin_result = db.execute_query("SELECT id FROM users WHERE username = ?", ("admin",))
        admin_id = admin_result[0]['id'] if admin_result else 1
        
        # Get test product
        product_manager = ProductManager()
        products = product_manager.search_products("Test Cola")
        if not products:
            print(" No test product found for sales test")
            return False
        
        test_product = products[0]
        
        # Create transaction manager and start sale
        transaction_manager = TransactionManager()
        sale = transaction_manager.start_new_sale(admin_id)
        
        print(f" Started new sale: {sale.transaction_ref}")
        
        # Add item to sale
        if transaction_manager.add_item_to_sale(test_product.id, 2):
            print(" Added item to sale")
        else:
            print(" Failed to add item to sale")
            return False
        
        # Set payment method
        total_amount = sale.total_amount
        if transaction_manager.set_payment_method("cash", total_amount + 2.00):
            print(f" Set payment method (Total: R{total_amount:.2f})")
        else:
            print(" Failed to set payment method")
            return False
        
        # Complete sale
        sale_id = transaction_manager.complete_sale()
        print(f" Completed sale with ID: {sale_id}")
        
        # Test receipt generation
        receipt_generator = ReceiptGenerator()
        completed_sale = transaction_manager.get_sale_by_id(sale_id)
        
        if completed_sale:
            receipt_text = receipt_generator.generate_receipt_text(completed_sale)
            print(" Generated receipt text")
            print("\n--- RECEIPT PREVIEW ---")
            print(receipt_text[:200] + "..." if len(receipt_text) > 200 else receipt_text)
            print("--- END RECEIPT ---\n")
        else:
            print(" Failed to generate receipt")
            return False
        
        return True
    except Exception as e:
        print(f" Sales processing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("TEMBIE'S SPAZA SHOP POS SYSTEM - CORE FUNCTIONALITY TEST")
    print("=" * 50)
    
    tests = [
        test_database_initialization,
        test_product_management,
        test_sales_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print(" All core functionality tests PASSED!")
        print("\nNext steps:")
        print("1. Run the application: python main.py")
        print("2. Build the GUI interface")
        print("3. Add user management features")
    else:
        print(" Some tests FAILED. Check the errors above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
