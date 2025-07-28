"""
Test Daily Cash Management System
Verify cash flow tracking and till reconciliation functionality
"""

import sys
import os
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cash_management():
    """Test daily cash management functionality"""
    print(" Testing Daily Cash Management")
    print("=" * 50)
    
    try:
        from core.sales.cash_management import get_cash_manager, CashManager
        from core.sales.transaction import TransactionManager
        from core.products.management import ProductManager
        from core.auth.authentication import ensure_demo_user
        
        # Ensure demo user exists
        ensure_demo_user()
        
        cash_manager = get_cash_manager()
        transaction_manager = TransactionManager()
        product_manager = ProductManager()
        
        print(" Cash management initialized")
        
        # Test 1: Start day
        print("\n1️⃣ Testing day start...")
        today = date.today()
        
        # Get current status
        summary = cash_manager.get_cash_summary(today)
        
        if not summary['day_started']:
            success = cash_manager.start_day(100.0, 1)  # Start with R100
            if success:
                print(" Day started with R100.00 opening amount")
            else:
                print(" Failed to start day")
                return False
        else:
            print(f" Day already started with R{summary['opening_amount']:.2f}")
        
        # Test 2: Make some sales to generate cash flow
        print("\n2️⃣ Creating test sales...")
        
        # Create a few sales
        products = product_manager.search_products("")
        if products:
            for i in range(3):
                sale = transaction_manager.start_new_sale(1)
                transaction_manager.add_item_to_sale(products[0].id, 1)
                transaction_manager.set_payment_method("cash", sale.total_amount + 5.0)
                sale_id = transaction_manager.complete_sale()
                print(f"   Created cash sale: R{sale.total_amount:.2f}")
        
        # Test 3: Update sales totals
        print("\n3️⃣ Updating sales totals...")
        success = cash_manager.update_sales_totals()
        if success:
            print(" Sales totals updated from transaction data")
        
        # Test 4: Record withdrawal
        print("\n4️⃣ Recording cash withdrawal...")
        success = cash_manager.record_withdrawal(20.0, "Personal use", 1)
        if success:
            print(" Recorded R20.00 withdrawal")
        
        # Test 5: Get updated summary
        print("\n5️⃣ Cash summary:")
        summary = cash_manager.get_cash_summary()
        print(f"  Opening amount: R{summary['opening_amount']:.2f}")
        print(f"  Cash sales: R{summary['cash_sales']:.2f}")
        print(f"  Card sales: R{summary['card_sales']:.2f}")
        print(f"  Withdrawals: R{summary['withdrawals']:.2f}")
        print(f"  Expected closing: R{summary['expected_closing']:.2f}")
        print(f"  Reconciled: {summary['reconciled']}")
        
        # Test 6: Till reconciliation
        print("\n6️⃣ Testing till reconciliation...")
        expected = summary['expected_closing']
        
        # Simulate actual count (slightly different for testing)
        actual_count = expected - 2.0  # R2 short
        
        result = cash_manager.reconcile_till(actual_count, 1, "End of day reconciliation")
        
        if result['success']:
            print(f" Till reconciled successfully")
            print(f"  Expected: R{result['expected']:.2f}")
            print(f"  Actual: R{result['actual']:.2f}")
            print(f"  Variance: R{result['variance']:.2f}")
            print(f"  Status: {result['status']}")
        else:
            print(" Till reconciliation failed")
        
        # Test 7: Generate daily report
        print("\n7️⃣ Generating daily report...")
        report = cash_manager.generate_daily_report()
        print("Daily Report Generated:")
        print("-" * 40)
        print(report)
        print("-" * 40)
        
        # Test 8: Cash history
        print("\n8️⃣ Testing cash history...")
        history = cash_manager.get_cash_history(7)
        print(f" Retrieved {len(history)} days of cash history")
        
        for day_record in history:
            status = " Reconciled" if day_record.reconciled else "⏳ Pending"
            print(f"  {day_record.date}: Opening R{day_record.opening_amount:.2f}, "
                  f"Sales R{day_record.cash_sales:.2f}, {status}")
        
        print("\n Cash management test completed successfully!")
        return True
        
    except Exception as e:
        print(f" Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_cash_management()
