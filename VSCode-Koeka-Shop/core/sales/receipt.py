"""
Receipt generation for Tembie's Spaza Shop POS System
Handles screen display, printing, and SMS receipt functionality
"""

from datetime import datetime
from typing import Dict, Any, Optional
from core.sales.transaction import Sale
from core.database.connection import get_db_manager

class ReceiptGenerator:
    """Generates receipts for display and printing"""
    
    def __init__(self):
        self.db = get_db_manager()
        self._load_shop_config()
    
    def _load_shop_config(self):
        """Load shop configuration for receipts"""
        query = "SELECT key, value FROM system_config WHERE key IN ('shop_name', 'receipt_footer')"
        results = self.db.execute_query(query)
        
        self.config = {}
        for row in results:
            self.config[row['key']] = row['value']
        
        # Set defaults if not found
        self.config.setdefault('shop_name', "Tembie's Spaza Shop")
        self.config.setdefault('receipt_footer', "Thank you for your business!")
    
    def generate_receipt_text(self, sale: Sale) -> str:
        """Generate receipt text for screen display or printing"""
        receipt_lines = []
        
        # Header
        receipt_lines.extend([
            "=" * 50,
            "PROOF OF PURCHASE".center(50),
            "=" * 50,
            "",
            self.config['shop_name'].center(50),
            "",
            f"Transaction: {sale.transaction_ref}",
            f"Date: {sale.date_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "-" * 50,
        ])
        
        # Items
        receipt_lines.append(f"{'Item':<20} {'Qty':<5} {'Price':<10} {'Total':<10}")
        receipt_lines.append("-" * 50)
        
        for item in sale.items:
            item_name = item.product_name[:18] if len(item.product_name) > 18 else item.product_name
            receipt_lines.append(
                f"{item_name:<20} {item.quantity:<5} "
                f"R{item.unit_price:<9.2f} R{item.total_price:<9.2f}"
            )
        
        receipt_lines.append("-" * 50)
        
        # Totals
        receipt_lines.extend([
            f"{'Items:':<30} {sale.item_count:>5}",
            "",
            f"{'Subtotal:':<30} R{sale.subtotal:>12.2f}",
            f"{'VAT (15%):':<30} R{sale.vat_amount:>12.2f}",
            "",
            f"{'TOTAL:':<30} R{sale.total_amount:>12.2f}",
            "=" * 50,
        ])
        
        # Payment details
        if sale.payment_method == 'cash':
            receipt_lines.extend([
                f"{'Payment Method:':<30} {'CASH':>15}",
                f"{'Cash Received:':<30} R{sale.cash_amount:>12.2f}",
                f"{'Change Given:':<30} R{sale.change_given:>12.2f}",
            ])
        elif sale.payment_method == 'card':
            receipt_lines.extend([
                f"{'Payment Method:':<30} {'CARD':>15}",
                f"{'Card Amount:':<30} R{sale.card_amount:>12.2f}",
            ])
        elif sale.payment_method == 'mixed':
            receipt_lines.extend([
                f"{'Payment Method:':<30} {'MIXED':>15}",
                f"{'Card Amount:':<30} R{sale.card_amount:>12.2f}",
                f"{'Cash Amount:':<30} R{sale.cash_amount:>12.2f}",
                f"{'Change Given:':<30} R{sale.change_given:>12.2f}",
            ])
        
        receipt_lines.extend([
            "",
            "=" * 50,
            "",
            self.config['receipt_footer'].center(50),
            "",
            "Keep this receipt for your records".center(50),
            "Photo with your cell phone if needed".center(50),
            "",
            "=" * 50,
        ])
        
        return "\n".join(receipt_lines)
    
    def generate_receipt_data(self, sale: Sale) -> Dict[str, Any]:
        """Generate structured receipt data for UI display"""
        return {
            'shop_name': self.config['shop_name'],
            'transaction_ref': sale.transaction_ref,
            'date_time': sale.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [
                {
                    'name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price
                }
                for item in sale.items
            ],
            'item_count': sale.item_count,
            'subtotal': sale.subtotal,
            'vat_amount': sale.vat_amount,
            'total_amount': sale.total_amount,
            'payment_method': sale.payment_method.upper(),
            'cash_amount': sale.cash_amount,
            'card_amount': sale.card_amount,
            'change_given': sale.change_given,
            'footer': self.config['receipt_footer']
        }
    
    def print_receipt(self, sale: Sale) -> bool:
        """Print receipt (placeholder for future thermal printer support)"""
        # TODO: Implement thermal printer support
        # For now, just return True to indicate success
        receipt_text = self.generate_receipt_text(sale)
        
        # Future implementation:
        # - Send to thermal printer
        # - Handle printer errors
        # - Return actual print status
        
        return True
    
    def send_receipt_sms(self, sale: Sale, phone_number: str) -> Dict[str, Any]:
        """Send receipt via SMS"""
        from core.sales.sms_service import get_sms_service
        
        sms_service = get_sms_service()
        return sms_service.send_receipt_sms(sale, phone_number)
    
    def get_receipt_for_reprint(self, transaction_ref: str) -> str:
        """Get receipt text for reprinting by transaction reference"""
        query = "SELECT id FROM sales WHERE transaction_ref = ?"
        results = self.db.execute_query(query, (transaction_ref,))
        
        if not results:
            raise ValueError(f"Transaction {transaction_ref} not found")
        
        # Import here to avoid circular import
        from core.sales.transaction import TransactionManager
        
        transaction_manager = TransactionManager()
        sale = transaction_manager.get_sale_by_id(results[0]['id'])
        
        if not sale:
            raise ValueError(f"Could not load sale data for {transaction_ref}")
        
        # Add reprint notice
        receipt_text = self.generate_receipt_text(sale)
        reprint_notice = "\n*** REPRINT ***\n" + receipt_text + "\n*** REPRINT ***\n"
        
        return reprint_notice
