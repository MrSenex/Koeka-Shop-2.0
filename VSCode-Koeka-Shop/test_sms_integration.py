"""
SMS Receipt Integration Test
Test the complete SMS receipt functionality in GUI context
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sms_integration():
    """Test SMS functionality integration"""
    print("🧪 Testing SMS Receipt Integration")
    print("=" * 50)
    
    try:
        # Test imports
        from core.sales.sms_service import get_sms_service
        from core.sales.receipt import ReceiptGenerator
        from core.sales.transaction import TransactionManager
        from core.products.management import ProductManager
        
        print("✓ All modules imported successfully")
        
        # Initialize services
        sms_service = get_sms_service()
        receipt_generator = ReceiptGenerator()
        transaction_manager = TransactionManager()
        product_manager = ProductManager()
        
        print("✓ Services initialized")
        
        # Test SMS configuration
        print(f"✓ SMS Enabled: {sms_service.is_sms_enabled()}")
        print(f"✓ SMS Provider: {sms_service.config.get('sms_provider', 'Not configured')}")
        
        # Test receipt generator SMS method
        print("\n🔗 Testing receipt generator SMS integration...")
        
        # Create a test sale
        sale = transaction_manager.start_new_sale(user_id=1)
        products = product_manager.search_products("")
        
        if products:
            # Add a product
            transaction_manager.add_item_to_sale(products[0].id, 1)
            transaction_manager.set_payment_method("cash", sale.total_amount + 2.0)
            sale_id = transaction_manager.complete_sale()
            completed_sale = transaction_manager.get_sale_by_id(sale_id)
            
            print(f"✓ Test sale created: {completed_sale.transaction_ref}")
            
            # Test SMS sending through receipt generator
            result = receipt_generator.send_receipt_sms(completed_sale, "+27821234567")
            
            if result['success']:
                print("✅ SMS sent successfully through receipt generator!")
                print(f"   Message ID: {result.get('message_id')}")
            else:
                print(f"❌ SMS failed: {result['error']}")
            
            # Test SMS history
            history = sms_service.get_sms_history(limit=3)
            print(f"✓ SMS history entries: {len(history)}")
            
        else:
            print("⚠️ No products available for testing")
        
        print("\n🎉 SMS integration test completed!")
        
        # Print SMS usage guide
        print("\n📋 SMS FUNCTIONALITY GUIDE")
        print("=" * 40)
        print("1. In GUI: Complete a sale, then click '📱 SMS Receipt'")
        print("2. Enter customer phone number (0XX XXX XXXX format)")
        print("3. View SMS preview before sending")
        print("4. SMS will be sent via demo provider (printed to console)")
        print("5. SMS history is logged in database")
        print("\nConfiguration:")
        print("- SMS is enabled by default in demo mode")
        print("- Provider: demo (for testing)")
        print("- For production: Configure Twilio or Africa's Talking")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_integration()
