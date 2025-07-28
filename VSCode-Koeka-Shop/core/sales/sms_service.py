"""
SMS Service for Tembie's Spaza Shop POS System
Handles SMS notifications including receipt sending
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime
from core.sales.transaction import Sale
from core.sales.receipt import ReceiptGenerator
from core.database.connection import get_db_manager

class SMSService:
    """Handles SMS functionality for receipts and notifications"""
    
    def __init__(self):
        self.db = get_db_manager()
        self.receipt_generator = ReceiptGenerator()
        self._load_sms_config()
    
    def _load_sms_config(self):
        """Load SMS configuration from database"""
        query = """
            SELECT key, value FROM system_config 
            WHERE key IN ('sms_enabled', 'sms_api_key', 'sms_sender_name', 'sms_provider')
        """
        results = self.db.execute_query(query)
        
        self.config = {}
        for row in results:
            self.config[row['key']] = row['value']
        
        # Set defaults
        self.config.setdefault('sms_enabled', 'false')
        self.config.setdefault('sms_provider', 'demo')  # demo, twilio, africastalking, etc.
        self.config.setdefault('sms_sender_name', "Tembie's Shop")
    
    def is_sms_enabled(self) -> bool:
        """Check if SMS functionality is enabled"""
        return self.config.get('sms_enabled', 'false').lower() == 'true'
    
    def validate_phone_number(self, phone: str) -> Optional[str]:
        """Validate and format South African phone number"""
        # Remove all non-digits
        phone = re.sub(r'[^\d]', '', phone)
        
        # Handle different formats
        if phone.startswith('0'):
            # Local format (0XX XXX XXXX) -> +27XX XXX XXXX
            phone = '+27' + phone[1:]
        elif phone.startswith('27'):
            # Country code without + -> +27XX XXX XXXX
            phone = '+' + phone
        elif not phone.startswith('+27'):
            # Assume it's missing country code
            if len(phone) == 9:
                phone = '+27' + phone
            else:
                return None
        
        # Validate final format: +27XXXXXXXXX (12 characters total)
        if len(phone) == 12 and phone.startswith('+27'):
            return phone
        
        return None
    
    def generate_sms_receipt(self, sale: Sale) -> str:
        """Generate SMS-optimized receipt text"""
        lines = []
        
        # Header
        lines.extend([
            f"{self.config.get('sms_sender_name', 'Shop')} Receipt",
            f"Ref: {sale.transaction_ref}",
            f"Date: {sale.date_time.strftime('%d/%m/%Y %H:%M')}",
            "",
        ])
        
        # Items (condensed format for SMS)
        for item in sale.items:
            name = item.product_name[:15] + "..." if len(item.product_name) > 15 else item.product_name
            lines.append(f"{item.quantity}x {name} R{item.total_price:.2f}")
        
        lines.extend([
            "",
            f"Items: {sale.item_count}",
            f"Subtotal: R{sale.subtotal:.2f}",
            f"VAT: R{sale.vat_amount:.2f}",
            f"TOTAL: R{sale.total_amount:.2f}",
            "",
            f"Paid: {sale.payment_method.upper()}",
        ])
        
        if sale.payment_method == 'cash' and sale.change_given > 0:
            lines.append(f"Change: R{sale.change_given:.2f}")
        
        lines.extend([
            "",
            "Thank you for shopping with us!",
            "Keep this SMS as proof of purchase."
        ])
        
        return "\n".join(lines)
    
    def send_receipt_sms(self, sale: Sale, phone_number: str) -> Dict[str, Any]:
        """Send receipt via SMS"""
        # Validate phone number
        formatted_phone = self.validate_phone_number(phone_number)
        if not formatted_phone:
            return {
                'success': False,
                'error': 'Invalid phone number format. Please use format: 0XX XXX XXXX'
            }
        
        # Check if SMS is enabled
        if not self.is_sms_enabled():
            return {
                'success': False,
                'error': 'SMS service is not enabled. Contact administrator.'
            }
        
        # Generate SMS receipt
        sms_text = self.generate_sms_receipt(sale)
        
        # Send SMS based on provider
        provider = self.config.get('sms_provider', 'demo')
        
        if provider == 'demo':
            result = self._send_demo_sms(formatted_phone, sms_text)
        elif provider == 'twilio':
            result = self._send_twilio_sms(formatted_phone, sms_text)
        elif provider == 'africastalking':
            result = self._send_africastalking_sms(formatted_phone, sms_text)
        else:
            return {
                'success': False,
                'error': f'Unsupported SMS provider: {provider}'
            }
        
        # Log SMS attempt
        self._log_sms_attempt(sale.transaction_ref, formatted_phone, result['success'], result.get('error'))
        
        return result
    
    def _send_demo_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Demo SMS sender (for testing/development)"""
        # Simulate SMS sending with 95% success rate
        import random
        
        if random.random() < 0.95:  # 95% success rate
            print(f"\n📱 DEMO SMS SENT TO {phone}")
            print("=" * 40)
            print(message)
            print("=" * 40)
            
            return {
                'success': True,
                'message_id': f'demo_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'phone': phone
            }
        else:
            return {
                'success': False,
                'error': 'Demo: Network error (simulated failure)'
            }
    
    def _send_twilio_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio (requires twilio package)"""
        try:
            # This would require: pip install twilio
            # from twilio.rest import Client
            
            # For now, return placeholder
            return {
                'success': False,
                'error': 'Twilio SMS integration not implemented. Install twilio package and configure.'
            }
        except ImportError:
            return {
                'success': False,
                'error': 'Twilio package not installed. Run: pip install twilio'
            }
    
    def _send_africastalking_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Send SMS via Africa's Talking (requires africastalking package)"""
        try:
            # This would require: pip install africastalking
            # import africastalking
            
            # For now, return placeholder
            return {
                'success': False,
                'error': 'Africa\'s Talking SMS integration not implemented. Install africastalking package and configure.'
            }
        except ImportError:
            return {
                'success': False,
                'error': 'Africa\'s Talking package not installed. Run: pip install africastalking'
            }
    
    def _log_sms_attempt(self, transaction_ref: str, phone: str, success: bool, error: str = None):
        """Log SMS sending attempt"""
        query = """
            INSERT INTO sms_log (transaction_ref, phone_number, sent_at, success, error_message)
            VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            self.db.execute_update(query, (
                transaction_ref,
                phone,
                datetime.now().isoformat(),
                1 if success else 0,
                error
            ))
        except Exception as e:
            # Don't fail the SMS operation due to logging issues
            print(f"Warning: Could not log SMS attempt: {e}")
    
    def get_sms_history(self, transaction_ref: str = None, limit: int = 50) -> list:
        """Get SMS sending history"""
        if transaction_ref:
            query = """
                SELECT * FROM sms_log 
                WHERE transaction_ref = ?
                ORDER BY sent_at DESC
            """
            params = (transaction_ref,)
        else:
            query = """
                SELECT * FROM sms_log 
                ORDER BY sent_at DESC
                LIMIT ?
            """
            params = (limit,)
        
        try:
            return self.db.execute_query(query, params)
        except Exception:
            # Return empty list if table doesn't exist yet
            return []
    
    def configure_sms_provider(self, provider: str, api_key: str = None, sender_name: str = None):
        """Configure SMS provider settings"""
        updates = [
            ('sms_provider', provider),
            ('sms_enabled', 'true')
        ]
        
        if api_key:
            updates.append(('sms_api_key', api_key))
        
        if sender_name:
            updates.append(('sms_sender_name', sender_name))
        
        for key, value in updates:
            query = """
                INSERT OR REPLACE INTO system_config (key, value, updated_at)
                VALUES (?, ?, ?)
            """
            self.db.execute_update(query, (key, value, datetime.now().isoformat()))
        
        # Reload config
        self._load_sms_config()

# Global SMS service instance
_sms_service = None

def get_sms_service() -> SMSService:
    """Get global SMS service instance"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service
