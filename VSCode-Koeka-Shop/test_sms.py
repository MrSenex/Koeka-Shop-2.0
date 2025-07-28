"""
Test SMS Receipt Functionality
Quick test to verify SMS receipt generation and sending works
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sms_functionality():
    """Test SMS receipt functionality"""
    print(" Testing SMS Receipt Functionality")
    print("=" * 50)
    
    try:
        # Import required modules
        from core.sales.sms_service import get_sms_service
        from core.sales.transaction import TransactionManager
        from core.products.management import ProductManager
        
        # Initialize services
        sms_service = get_sms_service()
        transaction_manager = TransactionManager()
        product_manager = ProductManager()
        
        print(" Services initialized successfully")
        
        # Check if SMS is enabled
        is_enabled = sms_service.is_sms_enabled()
        print(f"SMS Enabled: {is_enabled}")
        
        # Test phone number validation
        test_numbers = [
            "0821234567",     # Local format
            "+27821234567",   # International format  
            "27821234567",    # Country code without +
            "082-123-4567",   # With dashes
            "082 123 4567",   # With spaces
            "invalid",        # Invalid
        ]
        
        print("\n Testing phone number validation:")
        for number in test_numbers:
            validated = sms_service.validate_phone_number(number)
            status = "" if validated else ""
            print(f"  {status} {number:<15} -> {validated}")
        
        # Create a test sale
        print("\n Creating test sale...")
        sale = transaction_manager.start_new_sale(user_id=1)
        
        # Add some products
        products = product_manager.search_products("")
        if products:
            for product in products[:2]:
                transaction_manager.add_item_to_sale(product.id, 1)
                print(f"  Added: {product.name}")
        
        # Set payment and complete sale
        transaction_manager.set_payment_method("cash", sale.total_amount + 5.0)
        sale_id = transaction_manager.complete_sale()
        completed_sale = transaction_manager.get_sale_by_id(sale_id)
        
        print(f" Test sale completed: {completed_sale.transaction_ref}")
        
        # Generate SMS receipt
        print("\n Generating SMS receipt...")
        sms_text = sms_service.generate_sms_receipt(completed_sale)
        print("SMS Receipt Preview:")
        print("-" * 30)
        print(sms_text)
        print("-" * 30)
        
        # Test SMS sending (demo mode)
        print("\n Testing SMS sending...")
        test_phone = "+27821234567"
        result = sms_service.send_receipt_sms(completed_sale, test_phone)
        
        if result['success']:
            print(f" SMS sent successfully!")
            print(f"   Phone: {result.get('phone')}")
            print(f"   Message ID: {result.get('message_id')}")
        else:
            print(f" SMS failed: {result['error']}")
        
        # Check SMS history
        print("\n SMS History:")
        history = sms_service.get_sms_history(limit=5)
        if history:
            for entry in history:
                status = "" if entry['success'] else ""
                print(f"  {status} {entry['phone_number']} - {entry['sent_at']}")
        else:
            print("  No SMS history found")
        
        print("\n SMS functionality test completed successfully!")
        
    except Exception as e:
        print(f"\n Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_functionality()
