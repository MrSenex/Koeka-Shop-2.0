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
    
    def get_all_products(self, include_archived: bool = False) -> List[Product]:
        """Get all products"""
        if include_archived:
            query = "SELECT * FROM products ORDER BY name"
        else:
            query = "SELECT * FROM products WHERE (archived IS NULL OR archived = 0) ORDER BY name"
        
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
    
    def delete_product(self, product_id: int, user_id: int, force: bool = False) -> bool:
        """
        Delete a product from the system
        
        Args:
            product_id: ID of the product to delete
            user_id: ID of the user performing the deletion
            force: If True, force delete even if there are associated records
        
        Returns:
            bool: True if deletion was successful, False otherwise
        
        Raises:
            ValueError: If product has associated sales/movements and force=False
        """
        # Check if product exists
        product = self.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        # Check for associated sales
        sales_count_query = "SELECT COUNT(*) as count FROM sale_items WHERE product_id = ?"
        sales_result = self.db.execute_query(sales_count_query, (product_id,))
        sales_count = sales_result[0]['count'] if sales_result else 0
        
        # Check for stock movements
        movements_count_query = "SELECT COUNT(*) as count FROM stock_movements WHERE product_id = ?"
        movements_result = self.db.execute_query(movements_count_query, (product_id,))
        movements_count = movements_result[0]['count'] if movements_result else 0
        
        if (sales_count > 0 or movements_count > 0) and not force:
            raise ValueError(
                f"Cannot delete product '{product.name}'. "
                f"It has {sales_count} associated sales and {movements_count} stock movements. "
                f"Use force=True to delete anyway or consider archiving instead."
            )
        
        try:
            # If forcing deletion with associated records, we need to handle them
            if force and (sales_count > 0 or movements_count > 0):
                # Log the deletion for audit purposes
                self._log_stock_movement(
                    product_id, 'deletion', -product.current_stock,
                    product.current_stock, 0, user_id,
                    f"Product deleted (force): had {sales_count} sales, {movements_count} movements"
                )
                
                # Note: We don't delete sale_items or stock_movements to preserve historical data
                # They will reference a non-existent product_id, but this maintains data integrity
                # for historical reports
            
            # Delete the product
            delete_query = "DELETE FROM products WHERE id = ?"
            rows_affected = self.db.execute_update(delete_query, (product_id,))
            
            return rows_affected > 0
            
        except Exception as e:
            raise ValueError(f"Failed to delete product: {str(e)}")
    
    def archive_product(self, product_id: int, user_id: int) -> bool:
        """
        Archive a product instead of deleting it (soft delete)
        This is safer for products with sales history
        """
        # Add an 'archived' column if it doesn't exist
        try:
            self.db.execute_update("ALTER TABLE products ADD COLUMN archived BOOLEAN DEFAULT 0", ())
        except:
            # Column might already exist
            pass
        
        # Archive the product
        archive_query = """
            UPDATE products 
            SET archived = 1, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        rows_affected = self.db.execute_update(archive_query, (product_id,))
        
        if rows_affected > 0:
            # Log the archival
            product = self.get_product_by_id(product_id)
            if product:
                self._log_stock_movement(
                    product_id, 'adjustment', -product.current_stock,
                    product.current_stock, 0, user_id,
                    "Product archived - stock cleared"
                )
                
                # Clear stock when archiving
                self.db.execute_update(
                    "UPDATE products SET current_stock = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (product_id,)
                )
        
        return rows_affected > 0
    
    def get_archived_products(self) -> List[Product]:
        """Get all archived products"""
        query = "SELECT * FROM products WHERE archived = 1 ORDER BY name"
        try:
            results = self.db.execute_query(query)
            return [self._row_to_product(row) for row in results]
        except:
            # If archived column doesn't exist, return empty list
            return []
    
    def restore_product(self, product_id: int, user_id: int) -> bool:
        """Restore an archived product"""
        restore_query = """
            UPDATE products 
            SET archived = 0, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND archived = 1
        """
        rows_affected = self.db.execute_update(restore_query, (product_id,))
        
        if rows_affected > 0:
            self._log_stock_movement(
                product_id, 'adjustment', 0, 0, 0, user_id,
                "Product restored from archive"
            )
        
        return rows_affected > 0
    
    def can_delete_product(self, product_id: int) -> Dict[str, Any]:
        """
        Check if a product can be safely deleted
        
        Returns:
            dict: Contains 'can_delete' boolean and details about constraints
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return {'can_delete': False, 'reason': 'Product not found'}
        
        # Check for associated sales
        sales_count_query = "SELECT COUNT(*) as count FROM sale_items WHERE product_id = ?"
        sales_result = self.db.execute_query(sales_count_query, (product_id,))
        sales_count = sales_result[0]['count'] if sales_result else 0
        
        # Check for stock movements
        movements_count_query = "SELECT COUNT(*) as count FROM stock_movements WHERE product_id = ?"
        movements_result = self.db.execute_query(movements_count_query, (product_id,))
        movements_count = movements_result[0]['count'] if movements_result else 0
        
        can_delete = sales_count == 0 and movements_count == 0
        
        return {
            'can_delete': can_delete,
            'sales_count': sales_count,
            'movements_count': movements_count,
            'current_stock': product.current_stock,
            'recommendation': 'archive' if not can_delete else 'delete'
        }

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
