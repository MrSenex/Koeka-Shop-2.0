"""
Simple CLI demo for Tembie's Spaza Shop POS System
Demonstrates core functionality through command-line interface
"""

import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.products.management import ProductManager, Product
from core.sales.transaction import TransactionManager
from core.sales.receipt import ReceiptGenerator
from core.database.connection import get_db_manager
from utils.helpers import hash_password
from utils.validation import validate_price, validate_stock_quantity

class SimplePOSDemo:
    """Simple CLI demonstration of POS functionality"""
    
    def __init__(self):
        self.product_manager = ProductManager()
        self.transaction_manager = TransactionManager()
        self.receipt_generator = ReceiptGenerator()
        self.current_user_id = self._get_demo_user()
    
    def _get_demo_user(self):
        """Get or create demo user"""
        db = get_db_manager()
        result = db.execute_query("SELECT id FROM users WHERE username = ?", ("demo",))
        
        if result:
            return result[0]['id']
        else:
            # Create demo user
            password_hash = hash_password("demo123")
            return db.get_last_insert_id("""
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (?, ?, ?, ?)
            """, ("demo", password_hash, "admin", "Demo User"))
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "=" * 50)
        print("🏪 TEMBIE'S SPAZA SHOP - POS DEMO")
        print("=" * 50)
        print("1. View Products")
        print("2. Add New Product")
        print("3. Start New Sale")
        print("4. View Sales History")
        print("5. Check Stock Levels")
        print("6. Generate Test Receipt")
        print("7. View SMS History")
        print("0. Exit")
        print("=" * 50)
    
    def view_products(self):
        """Display all products"""
        print("\n📦 PRODUCT CATALOG")
        print("-" * 80)
        print(f"{'ID':<4} {'Name':<25} {'Barcode':<15} {'Price':<8} {'Stock':<6} {'Category':<12}")
        print("-" * 80)
        
        products = self.product_manager.get_all_products()
        
        if not products:
            print("No products found. Add some products first!")
            return
        
        for product in products:
            stock_status = "⚠️ LOW" if product.current_stock <= product.min_stock else "✓"
            print(f"{product.id:<4} {product.name[:24]:<25} {product.barcode or 'N/A':<15} "
                  f"R{product.sell_price:<7.2f} {product.current_stock:<4} {stock_status:<3} {product.category:<12}")
        
        print("-" * 80)
        print(f"Total products: {len(products)}")
    
    def add_product(self):
        """Add a new product"""
        print("\n➕ ADD NEW PRODUCT")
        print("-" * 30)
        
        try:
            name = input("Product name: ").strip()
            if not name:
                print("❌ Product name cannot be empty!")
                return
            
            barcode = input("Barcode (optional): ").strip() or None
            
            print("Categories: Food, Household, Sweets, Cooldrinks, Other")
            category = input("Category: ").strip()
            if category not in ['Food', 'Household', 'Sweets', 'Cooldrinks', 'Other']:
                print("❌ Invalid category!")
                return
            
            cost_price = float(input("Cost price (R): "))
            if not validate_price(cost_price):
                print("❌ Invalid cost price!")
                return
            
            sell_price = float(input("Selling price (R): "))
            if not validate_price(sell_price):
                print("❌ Invalid selling price!")
                return
            
            current_stock = int(input("Current stock: "))
            if not validate_stock_quantity(current_stock):
                print("❌ Invalid stock quantity!")
                return
            
            min_stock = int(input("Minimum stock level: "))
            if not validate_stock_quantity(min_stock):
                print("❌ Invalid minimum stock!")
                return
            
            product = Product(
                name=name,
                barcode=barcode,
                category=category,
                cost_price=cost_price,
                sell_price=sell_price,
                current_stock=current_stock,
                monthly_stock=current_stock * 2,  # Default to double current stock
                min_stock=min_stock,
                vat_rate=15.0,
                vat_inclusive=True
            )
            
            product_id = self.product_manager.create_product(product, self.current_user_id)
            print(f"✅ Product created with ID: {product_id}")
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ Error creating product: {e}")
    
    def start_sale(self):
        """Start a new sale transaction"""
        print("\n🛒 NEW SALE")
        print("-" * 20)
        
        try:
            sale = self.transaction_manager.start_new_sale(self.current_user_id)
            print(f"Started sale: {sale.transaction_ref}")
            
            while True:
                print(f"\nCurrent sale total: R{sale.total_amount:.2f}")
                print("Options:")
                print("1. Add item by ID")
                print("2. Add item by barcode") 
                print("3. View current sale")
                print("4. Remove item")
                print("5. Complete sale")
                print("0. Cancel sale")
                
                choice = input("Choice: ").strip()
                
                if choice == "1":
                    self._add_item_by_id()
                elif choice == "2":
                    self._add_item_by_barcode()
                elif choice == "3":
                    self._view_current_sale()
                elif choice == "4":
                    self._remove_item()
                elif choice == "5":
                    if self._complete_sale():
                        break
                elif choice == "0":
                    self.transaction_manager.current_sale = None
                    print("❌ Sale cancelled")
                    break
                else:
                    print("❌ Invalid choice!")
                    
        except Exception as e:
            print(f"❌ Error in sale: {e}")
    
    def _add_item_by_id(self):
        """Add item to sale by product ID"""
        try:
            product_id = int(input("Product ID: "))
            quantity = int(input("Quantity (default 1): ") or "1")
            
            self.transaction_manager.add_item_to_sale(product_id, quantity)
            print(f"✅ Added {quantity} item(s)")
            
        except ValueError:
            print("❌ Invalid ID or quantity!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _add_item_by_barcode(self):
        """Add item to sale by barcode"""
        try:
            barcode = input("Barcode: ").strip()
            quantity = int(input("Quantity (default 1): ") or "1")
            
            self.transaction_manager.add_item_by_barcode(barcode, quantity)
            print(f"✅ Added {quantity} item(s)")
            
        except ValueError:
            print("❌ Invalid quantity!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _view_current_sale(self):
        """View current sale items"""
        sale = self.transaction_manager.get_current_sale()
        if not sale or not sale.items:
            print("❌ No items in current sale")
            return
        
        print("\n📋 CURRENT SALE")
        print("-" * 60)
        print(f"{'Item':<25} {'Qty':<4} {'Price':<8} {'Total':<8}")
        print("-" * 60)
        
        for item in sale.items:
            print(f"{item.product_name[:24]:<25} {item.quantity:<4} "
                  f"R{item.unit_price:<7.2f} R{item.total_price:<7.2f}")
        
        print("-" * 60)
        print(f"Subtotal: R{sale.subtotal:.2f}")
        print(f"VAT (15%): R{sale.vat_amount:.2f}")
        print(f"TOTAL: R{sale.total_amount:.2f}")
    
    def _remove_item(self):
        """Remove item from current sale"""
        try:
            product_id = int(input("Product ID to remove: "))
            self.transaction_manager.remove_item_from_sale(product_id)
            print("✅ Item removed")
        except ValueError:
            print("❌ Invalid product ID!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _complete_sale(self):
        """Complete the current sale"""
        sale = self.transaction_manager.get_current_sale()
        if not sale or not sale.items:
            print("❌ No items to complete sale")
            return False
        
        print(f"\nTotal amount: R{sale.total_amount:.2f}")
        print("Payment methods: cash, card, mixed")
        
        payment_method = input("Payment method: ").strip().lower()
        if payment_method not in ['cash', 'card', 'mixed']:
            print("❌ Invalid payment method!")
            return False
        
        try:
            if payment_method == 'cash':
                cash_amount = float(input(f"Cash received (min R{sale.total_amount:.2f}): "))
                self.transaction_manager.set_payment_method('cash', cash_amount)
            elif payment_method == 'card':
                self.transaction_manager.set_payment_method('card', 0.0, sale.total_amount)
            else:  # mixed
                card_amount = float(input("Card amount: "))
                cash_amount = float(input("Cash amount: "))
                self.transaction_manager.set_payment_method('mixed', cash_amount, card_amount)
            
            if not self.transaction_manager.validate_payment():
                print("❌ Insufficient payment!")
                return False
            
            sale_id = self.transaction_manager.complete_sale()
            print(f"✅ Sale completed! ID: {sale_id}")
            
            # Show receipt
            completed_sale = self.transaction_manager.get_sale_by_id(sale_id)
            if completed_sale:
                print("\n📄 RECEIPT")
                print("=" * 50)
                receipt = self.receipt_generator.generate_receipt_text(completed_sale)
                print(receipt)
                print("=" * 50)
                
                # Offer SMS receipt option
                self._offer_sms_receipt(completed_sale)
            
            return True
            
        except ValueError:
            print("❌ Invalid payment amount!")
            return False
        except Exception as e:
            print(f"❌ Error completing sale: {e}")
            return False
    
    def view_sales_history(self):
        """View recent sales"""
        print("\n📊 SALES HISTORY (Today)")
        print("-" * 80)
        
        db = get_db_manager()
        today = datetime.now().date()
        
        query = """
            SELECT s.id, s.transaction_ref, s.date_time, s.total_amount, s.payment_method,
                   COUNT(si.id) as item_count
            FROM sales s
            LEFT JOIN sale_items si ON s.id = si.sale_id
            WHERE DATE(s.date_time) = ? AND s.voided = 0
            GROUP BY s.id
            ORDER BY s.date_time DESC
            LIMIT 10
        """
        
        results = db.execute_query(query, (today.isoformat(),))
        
        if not results:
            print("No sales found for today.")
            return
        
        print(f"{'ID':<4} {'Transaction':<12} {'Time':<8} {'Items':<6} {'Total':<10} {'Payment':<8}")
        print("-" * 80)
        
        for row in results:
            time_str = row['date_time'].split(' ')[1][:5]  # Extract HH:MM
            print(f"{row['id']:<4} {row['transaction_ref']:<12} {time_str:<8} "
                  f"{row['item_count']:<6} R{row['total_amount']:<9.2f} {row['payment_method']:<8}")
        
        print("-" * 80)
        
        # Calculate totals
        total_sales = sum(row['total_amount'] for row in results)
        print(f"Total sales today: R{total_sales:.2f} ({len(results)} transactions)")
    
    def check_stock_levels(self):
        """Check stock levels and show alerts"""
        print("\n📦 STOCK LEVEL CHECK")
        print("-" * 60)
        
        low_stock = self.product_manager.get_low_stock_products()
        
        if not low_stock:
            print("✅ All products have adequate stock!")
            return
        
        print("⚠️ LOW STOCK ALERTS:")
        print(f"{'Product':<25} {'Current':<8} {'Minimum':<8} {'Status':<10}")
        print("-" * 60)
        
        for product in low_stock:
            status = "URGENT" if product.current_stock == 0 else "LOW"
            print(f"{product.name[:24]:<25} {product.current_stock:<8} {product.min_stock:<8} {status:<10}")
        
        print("-" * 60)
        print(f"⚠️ {len(low_stock)} product(s) need restocking!")
    
    def generate_test_receipt(self):
        """Generate a test receipt for demonstration"""
        print("\n📄 TEST RECEIPT GENERATION")
        print("-" * 30)
        
        db = get_db_manager()
        query = "SELECT id FROM sales WHERE voided = 0 ORDER BY date_time DESC LIMIT 1"
        results = db.execute_query(query)
        
        if not results:
            print("❌ No sales found. Complete a sale first!")
            return
        
        sale = self.transaction_manager.get_sale_by_id(results[0]['id'])
        if sale:
            receipt = self.receipt_generator.generate_receipt_text(sale)
            print("\n" + "=" * 50)
            print("📄 RECEIPT (Latest Sale)")
            print("=" * 50)
            print(receipt)
            print("=" * 50)
        else:
            print("❌ Could not load sale data!")
    
    def _offer_sms_receipt(self, sale):
        """Offer to send receipt via SMS"""
        print("\n📱 SMS RECEIPT OPTION")
        print("-" * 30)
        
        send_sms = input("Send receipt via SMS? (y/n): ").strip().lower()
        if send_sms == 'y':
            phone = input("Enter customer phone number (e.g., 0821234567): ").strip()
            
            if not phone:
                print("❌ No phone number entered")
                return
            
            try:
                from core.sales.sms_service import get_sms_service
                sms_service = get_sms_service()
                
                print("📱 Sending SMS receipt...")
                result = sms_service.send_receipt_sms(sale, phone)
                
                if result['success']:
                    print(f"✅ SMS receipt sent successfully to {result.get('phone')}!")
                    print(f"   Message ID: {result.get('message_id')}")
                else:
                    print(f"❌ Failed to send SMS: {result['error']}")
                    
            except Exception as e:
                print(f"❌ SMS error: {e}")
    
    def view_sms_history(self):
        """View SMS sending history"""
        print("\n📱 SMS HISTORY")
        print("-" * 80)
        
        try:
            from core.sales.sms_service import get_sms_service
            sms_service = get_sms_service()
            
            history = sms_service.get_sms_history(limit=20)
            
            if not history:
                print("No SMS history found.")
                return
            
            print(f"{'Date/Time':<20} {'Phone':<15} {'Transaction':<12} {'Status':<8} {'Error':<30}")
            print("-" * 80)
            
            for entry in history:
                status = "✅ Sent" if entry['success'] else "❌ Failed"
                error = entry['error_message'][:28] + "..." if entry['error_message'] and len(entry['error_message']) > 30 else entry['error_message'] or ""
                
                print(f"{entry['sent_at'][:19]:<20} {entry['phone_number']:<15} "
                      f"{entry['transaction_ref']:<12} {status:<8} {error:<30}")
            
            print("-" * 80)
            print(f"Total SMS attempts: {len(history)}")
            
        except Exception as e:
            print(f"❌ Error viewing SMS history: {e}")
    
    def run(self):
        """Run the demo"""
        print("🏪 Welcome to Tembie's Spaza Shop POS Demo!")
        print("This demonstrates the core functionality implemented.")
        
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option: ").strip()
                
                if choice == "1":
                    self.view_products()
                elif choice == "2":
                    self.add_product()
                elif choice == "3":
                    self.start_sale()
                elif choice == "4":
                    self.view_sales_history()
                elif choice == "5":
                    self.check_stock_levels()
                elif choice == "6":
                    self.generate_test_receipt()
                elif choice == "7":
                    self.view_sms_history()
                elif choice == "0":
                    print("\n👋 Thank you for using Tembie's Spaza Shop POS!")
                    break
                else:
                    print("❌ Invalid choice! Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    demo = SimplePOSDemo()
    demo.run()
