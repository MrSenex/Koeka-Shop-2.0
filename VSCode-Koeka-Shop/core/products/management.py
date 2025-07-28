"""
Product management for Tembie's Spaza Shop POS System
Handles CRUD operations for products and stock management
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from core.database.connection import get_db_manager

@dataclass
class Product:
    """Product data model"""
    id: Optional[int] = None
    name: str = ""
    barcode: Optional[str] = None
    category: str = "Other"
    cost_price: float = 0.0
    sell_price: float = 0.0
    current_stock: int = 0
    monthly_stock: int = 0
    min_stock: int = 0
    vat_rate: float = 15.0
    vat_inclusive: bool = True
    expiry_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProductManager:
    """Manages product operations"""
    
    CATEGORIES = ['Food', 'Household', 'Sweets', 'Cooldrinks', 'Other']
    
    def __init__(self):
        self.db = get_db_manager()
    
    def create_product(self, product: Product, user_id: int) -> int:
        """Create a new product"""
        query = """
            INSERT INTO products 
            (name, barcode, category, cost_price, sell_price, current_stock, 
             monthly_stock, min_stock, vat_rate, vat_inclusive, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            product.name, product.barcode, product.category,
            product.cost_price, product.sell_price, product.current_stock,
            product.monthly_stock, product.min_stock, product.vat_rate,
            product.vat_inclusive, product.expiry_date
        )
        
        product_id = self.db.get_last_insert_id(query, params)
        
        # Log initial stock if greater than 0
        if product.current_stock > 0:
            self._log_stock_movement(
                product_id, 'addition', product.current_stock, 
                0, product.current_stock, user_id, "Initial stock"
            )
        
        return product_id
    
    def update_product(self, product: Product, user_id: int) -> bool:
        """Update an existing product"""
        query = """
            UPDATE products 
            SET name=?, barcode=?, category=?, cost_price=?, sell_price=?, 
                monthly_stock=?, min_stock=?, vat_rate=?, vat_inclusive=?, 
                expiry_date=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """
        params = (
            product.name, product.barcode, product.category,
            product.cost_price, product.sell_price, product.monthly_stock,
            product.min_stock, product.vat_rate, product.vat_inclusive,
            product.expiry_date, product.id
        )
        
        return self.db.execute_update(query, params) > 0
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        query = "SELECT * FROM products WHERE id = ?"
        results = self.db.execute_query(query, (product_id,))
        
        if results:
            return self._row_to_product(results[0])
        return None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get product by barcode"""
        query = "SELECT * FROM products WHERE barcode = ?"
        results = self.db.execute_query(query, (barcode,))
        
        if results:
            return self._row_to_product(results[0])
        return None
    
    def search_products(self, search_term: str) -> List[Product]:
        """Search products by name or barcode"""
        query = """
            SELECT * FROM products 
            WHERE name LIKE ? OR barcode LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        results = self.db.execute_query(query, (search_pattern, search_pattern))
        
        return [self._row_to_product(row) for row in results]
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get all products in a category"""
        query = "SELECT * FROM products WHERE category = ? ORDER BY name"
        results = self.db.execute_query(query, (category,))
        
        return [self._row_to_product(row) for row in results]
    
    def get_all_products(self) -> List[Product]:
        """Get all products"""
        query = "SELECT * FROM products ORDER BY name"
        results = self.db.execute_query(query)
        
        return [self._row_to_product(row) for row in results]
    
    def get_low_stock_products(self) -> List[Product]:
        """Get products with stock below minimum level"""
        query = "SELECT * FROM products WHERE current_stock <= min_stock ORDER BY current_stock"
        results = self.db.execute_query(query)
        
        return [self._row_to_product(row) for row in results]
    
    def adjust_stock(self, product_id: int, quantity_change: int, 
                    movement_type: str, user_id: int, reason: str = "") -> bool:
        """Adjust product stock and log the movement"""
        # Get current stock
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        previous_stock = product.current_stock
        new_stock = previous_stock + quantity_change
        
        # Prevent negative stock
        if new_stock < 0:
            raise ValueError("Cannot reduce stock below zero")
        
        # Update product stock
        query = """
            UPDATE products 
            SET current_stock = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        
        if self.db.execute_update(query, (new_stock, product_id)) > 0:
            # Log the movement
            self._log_stock_movement(
                product_id, movement_type, quantity_change,
                previous_stock, new_stock, user_id, reason
            )
            return True
        
        return False
    
    def reduce_stock_for_sale(self, product_id: int, quantity: int, 
                             sale_id: int, user_id: int) -> bool:
        """Reduce stock for a sale transaction"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        if product.current_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {product.current_stock}, Required: {quantity}")
        
        previous_stock = product.current_stock
        new_stock = previous_stock - quantity
        
        # Update product stock
        query = """
            UPDATE products 
            SET current_stock = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        
        if self.db.execute_update(query, (new_stock, product_id)) > 0:
            # Log the movement with sale reference
            self._log_stock_movement(
                product_id, 'sale', -quantity,
                previous_stock, new_stock, user_id, 
                f"Sale transaction", sale_id
            )
            return True
        
        return False
    
    def _log_stock_movement(self, product_id: int, movement_type: str, 
                           quantity_change: int, previous_stock: int, 
                           new_stock: int, user_id: int, reason: str = "",
                           reference_id: Optional[int] = None):
        """Log stock movement to audit trail"""
        query = """
            INSERT INTO stock_movements 
            (product_id, movement_type, quantity_change, previous_stock, 
             new_stock, user_id, reason, reference_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            product_id, movement_type, quantity_change, previous_stock,
            new_stock, user_id, reason, reference_id
        )
        
        self.db.execute_update(query, params)
    
    def get_stock_movements(self, product_id: Optional[int] = None, 
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get stock movement history"""
        if product_id:
            query = """
                SELECT sm.*, p.name as product_name, u.username
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                JOIN users u ON sm.user_id = u.id
                WHERE sm.product_id = ?
                ORDER BY sm.date_time DESC
                LIMIT ?
            """
            params = (product_id, limit)
        else:
            query = """
                SELECT sm.*, p.name as product_name, u.username
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                JOIN users u ON sm.user_id = u.id
                ORDER BY sm.date_time DESC
                LIMIT ?
            """
            params = (limit,)
        
        results = self.db.execute_query(query, params)
        return [dict(row) for row in results]
    
    def _row_to_product(self, row) -> Product:
        """Convert database row to Product object"""
        # Helper function to parse datetime with microseconds
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
        
        return Product(
            id=row['id'],
            name=row['name'],
            barcode=row['barcode'],
            category=row['category'],
            cost_price=float(row['cost_price']),
            sell_price=float(row['sell_price']),
            current_stock=row['current_stock'],
            monthly_stock=row['monthly_stock'],
            min_stock=row['min_stock'],
            vat_rate=float(row['vat_rate']),
            vat_inclusive=bool(row['vat_inclusive']),
            expiry_date=datetime.strptime(row['expiry_date'], '%Y-%m-%d').date() if row['expiry_date'] else None,
            created_at=parse_datetime_safe(row['created_at']),
            updated_at=parse_datetime_safe(row['updated_at'])
        )
