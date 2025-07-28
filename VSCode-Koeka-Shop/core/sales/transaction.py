"""
Sales transaction processing for Tembie's Spaza Shop POS System
Handles complete sales workflow including payment processing and stock reduction
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from core.database.connection import get_db_manager
from core.products.management import ProductManager, Product

@dataclass
class SaleItem:
    """Individual item in a sale"""
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    vat_rate: float
    
    def calculate_vat_amount(self) -> float:
        """Calculate VAT amount for this item"""
        if self.vat_rate > 0:
            return self.total_price * (self.vat_rate / (100 + self.vat_rate))
        return 0.0

@dataclass
class Sale:
    """Complete sale transaction"""
    id: Optional[int] = None
    transaction_ref: str = field(default_factory=lambda: f"TXN-{uuid.uuid4().hex[:8].upper()}")
    date_time: datetime = field(default_factory=datetime.now)
    user_id: int = 0
    items: List[SaleItem] = field(default_factory=list)
    payment_method: str = "cash"  # cash, card, mixed
    cash_amount: float = 0.0
    card_amount: float = 0.0
    change_given: float = 0.0
    voided: bool = False
    voided_by: Optional[int] = None
    voided_at: Optional[datetime] = None
    void_reason: str = ""
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal before VAT"""
        return sum(item.total_price - item.calculate_vat_amount() for item in self.items)
    
    @property
    def vat_amount(self) -> float:
        """Calculate total VAT amount"""
        return sum(item.calculate_vat_amount() for item in self.items)
    
    @property
    def total_amount(self) -> float:
        """Calculate total amount including VAT"""
        return sum(item.total_price for item in self.items)
    
    @property
    def item_count(self) -> int:
        """Total number of items"""
        return sum(item.quantity for item in self.items)

class TransactionManager:
    """Manages sales transactions"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.product_manager = ProductManager()
        self.current_sale: Optional[Sale] = None
    
    def start_new_sale(self, user_id: int) -> Sale:
        """Start a new sale transaction"""
        self.current_sale = Sale(user_id=user_id)
        return self.current_sale
    
    def add_item_to_sale(self, product_id: int, quantity: int = 1) -> bool:
        """Add item to current sale"""
        if not self.current_sale:
            raise ValueError("No active sale. Start a new sale first.")
        
        product = self.product_manager.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Check stock availability
        if product.current_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {product.current_stock}, Required: {quantity}")
        
        # Check if item already exists in sale
        existing_item = None
        for item in self.current_sale.items:
            if item.product_id == product_id:
                existing_item = item
                break
        
        if existing_item:
            # Update existing item
            new_quantity = existing_item.quantity + quantity
            if product.current_stock < new_quantity:
                raise ValueError(f"Insufficient stock. Available: {product.current_stock}, Required: {new_quantity}")
            
            existing_item.quantity = new_quantity
            existing_item.total_price = existing_item.unit_price * new_quantity
        else:
            # Add new item
            sale_item = SaleItem(
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.sell_price,
                total_price=product.sell_price * quantity,
                vat_rate=product.vat_rate if product.vat_inclusive else 0.0
            )
            self.current_sale.items.append(sale_item)
        
        return True
    
    def remove_item_from_sale(self, product_id: int) -> bool:
        """Remove item from current sale"""
        if not self.current_sale:
            return False
        
        self.current_sale.items = [
            item for item in self.current_sale.items 
            if item.product_id != product_id
        ]
        return True
    
    def update_item_quantity(self, product_id: int, new_quantity: int) -> bool:
        """Update quantity of item in current sale"""
        if not self.current_sale:
            return False
        
        if new_quantity <= 0:
            return self.remove_item_from_sale(product_id)
        
        product = self.product_manager.get_product_by_id(product_id)
        if not product:
            return False
        
        # Check stock availability
        if product.current_stock < new_quantity:
            raise ValueError(f"Insufficient stock. Available: {product.current_stock}, Required: {new_quantity}")
        
        for item in self.current_sale.items:
            if item.product_id == product_id:
                item.quantity = new_quantity
                item.total_price = item.unit_price * new_quantity
                return True
        
        return False
    
    def add_item_by_barcode(self, barcode: str, quantity: int = 1) -> bool:
        """Add item to sale by barcode"""
        product = self.product_manager.get_product_by_barcode(barcode)
        if not product:
            raise ValueError(f"Product with barcode {barcode} not found")
        
        return self.add_item_to_sale(product.id, quantity)
    
    def set_payment_method(self, payment_method: str, cash_amount: float = 0.0, 
                          card_amount: float = 0.0) -> bool:
        """Set payment method and amounts"""
        if not self.current_sale:
            return False
        
        valid_methods = ['cash', 'card', 'mixed']
        if payment_method not in valid_methods:
            raise ValueError(f"Invalid payment method. Must be one of: {valid_methods}")
        
        self.current_sale.payment_method = payment_method
        self.current_sale.cash_amount = cash_amount
        self.current_sale.card_amount = card_amount
        
        # Calculate change for cash payments
        if payment_method == 'cash':
            self.current_sale.change_given = max(0, cash_amount - self.current_sale.total_amount)
        elif payment_method == 'mixed':
            cash_due = max(0, self.current_sale.total_amount - card_amount)
            self.current_sale.change_given = max(0, cash_amount - cash_due)
        else:
            self.current_sale.change_given = 0.0
        
        return True
    
    def validate_payment(self) -> bool:
        """Validate that payment covers the total amount"""
        if not self.current_sale:
            return False
        
        total_paid = self.current_sale.cash_amount + self.current_sale.card_amount
        return total_paid >= self.current_sale.total_amount
    
    def complete_sale(self) -> int:
        """Complete the sale transaction and save to database"""
        if not self.current_sale:
            raise ValueError("No active sale to complete")
        
        if not self.current_sale.items:
            raise ValueError("Cannot complete sale with no items")
        
        if not self.validate_payment():
            raise ValueError("Payment amount is insufficient")
        
        # Save sale to database
        sale_id = self._save_sale_to_db()
        
        # Reduce stock for all items
        for item in self.current_sale.items:
            self.product_manager.reduce_stock_for_sale(
                item.product_id, item.quantity, sale_id, self.current_sale.user_id
            )
        
        # Clear current sale
        completed_sale = self.current_sale
        self.current_sale = None
        
        return sale_id
    
    def void_sale(self, sale_id: int, user_id: int, reason: str) -> bool:
        """Void a completed sale and restore stock"""
        # Get sale details
        sale = self.get_sale_by_id(sale_id)
        if not sale:
            return False
        
        if sale.voided:
            raise ValueError("Sale is already voided")
        
        # Mark sale as voided
        query = """
            UPDATE sales 
            SET voided = 1, voided_by = ?, voided_at = CURRENT_TIMESTAMP, void_reason = ?
            WHERE id = ?
        """
        
        if self.db.execute_update(query, (user_id, reason, sale_id)) > 0:
            # Restore stock for all items
            for item in sale.items:
                self.product_manager.adjust_stock(
                    item.product_id, item.quantity, 'adjustment',
                    user_id, f"Stock restored from voided sale {sale.transaction_ref}"
                )
            return True
        
        return False
    
    def get_current_sale(self) -> Optional[Sale]:
        """Get the current active sale"""
        return self.current_sale
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """Get sale by ID from database"""
        query = """
            SELECT s.*, si.id as item_id, si.product_id, si.quantity, 
                   si.unit_price, si.total_price, si.vat_rate, p.name as product_name
            FROM sales s
            LEFT JOIN sale_items si ON s.id = si.sale_id
            LEFT JOIN products p ON si.product_id = p.id
            WHERE s.id = ?
            ORDER BY si.id
        """
        
        results = self.db.execute_query(query, (sale_id,))
        if not results:
            return None
        
        # Build sale object from results
        first_row = results[0]
        
        # Helper function to parse datetime safely
        def parse_datetime_safe(dt_str):
            if not dt_str:
                return None
            try:
                # Try with microseconds first
                return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    # Try without microseconds
                    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None
        
        sale = Sale(
            id=first_row['id'],
            transaction_ref=first_row['transaction_ref'],
            date_time=parse_datetime_safe(first_row['date_time']) or datetime.now(),
            user_id=first_row['user_id'],
            payment_method=first_row['payment_method'],
            cash_amount=float(first_row['cash_amount']),
            card_amount=float(first_row['card_amount']),
            change_given=float(first_row['change_given']),
            voided=bool(first_row['voided']),
            voided_by=first_row['voided_by'],
            voided_at=parse_datetime_safe(first_row['voided_at']),
            void_reason=first_row['void_reason'] or ""
        )
        
        # Add items
        for row in results:
            if row['item_id']:  # Only if there are items
                sale.items.append(SaleItem(
                    product_id=row['product_id'],
                    product_name=row['product_name'],
                    quantity=row['quantity'],
                    unit_price=float(row['unit_price']),
                    total_price=float(row['total_price']),
                    vat_rate=float(row['vat_rate'])
                ))
        
        return sale
    
    def get_sales_by_date(self, date: datetime.date) -> List[Sale]:
        """Get all sales for a specific date"""
        query = """
            SELECT id FROM sales 
            WHERE DATE(date_time) = ? AND voided = 0
            ORDER BY date_time DESC
        """
        
        results = self.db.execute_query(query, (date.isoformat(),))
        sales = []
        
        for row in results:
            sale = self.get_sale_by_id(row['id'])
            if sale:
                sales.append(sale)
        
        return sales
    
    def _save_sale_to_db(self) -> int:
        """Save current sale to database"""
        # Insert sale record
        sale_query = """
            INSERT INTO sales 
            (transaction_ref, date_time, user_id, subtotal, vat_amount, total_amount,
             payment_method, cash_amount, card_amount, change_given)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        sale_params = (
            self.current_sale.transaction_ref,
            self.current_sale.date_time,
            self.current_sale.user_id,
            self.current_sale.subtotal,
            self.current_sale.vat_amount,
            self.current_sale.total_amount,
            self.current_sale.payment_method,
            self.current_sale.cash_amount,
            self.current_sale.card_amount,
            self.current_sale.change_given
        )
        
        sale_id = self.db.get_last_insert_id(sale_query, sale_params)
        
        # Insert sale items
        item_query = """
            INSERT INTO sale_items 
            (sale_id, product_id, quantity, unit_price, total_price, vat_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        for item in self.current_sale.items:
            item_params = (
                sale_id, item.product_id, item.quantity,
                item.unit_price, item.total_price, item.vat_rate
            )
            self.db.execute_update(item_query, item_params)
        
        return sale_id
