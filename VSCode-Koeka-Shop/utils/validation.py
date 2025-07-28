"""
Data validation utilities for Tembie's Spaza Shop POS System
Provides validation functions for user input and business logic
"""

import re
from typing import Optional, Union
from datetime import datetime, date

def validate_product_name(name: str) -> bool:
    """Validate product name"""
    if not name or not name.strip():
        return False
    
    # Must be between 1 and 100 characters
    if len(name.strip()) > 100:
        return False
    
    return True

def validate_barcode(barcode: Optional[str]) -> bool:
    """Validate product barcode"""
    if barcode is None or barcode == "":
        return True  # Barcode is optional
    
    # Remove spaces and check if numeric
    barcode_clean = barcode.replace(" ", "")
    
    # Must be numeric and between 8-18 digits (common barcode lengths)
    if not barcode_clean.isdigit():
        return False
    
    if len(barcode_clean) < 8 or len(barcode_clean) > 18:
        return False
    
    return True

def validate_price(price: Union[str, float, int]) -> bool:
    """Validate price value"""
    try:
        price_float = float(price)
        
        # Must be positive
        if price_float < 0:
            return False
        
        # Must not exceed reasonable maximum (R100,000)
        if price_float > 100000:
            return False
        
        # Check for reasonable decimal places (max 2)
        price_str = str(price_float)
        if '.' in price_str:
            decimal_places = len(price_str.split('.')[1])
            if decimal_places > 2:
                return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_stock_quantity(quantity: Union[str, int]) -> bool:
    """Validate stock quantity"""
    try:
        quantity_int = int(quantity)
        
        # Must be non-negative
        if quantity_int < 0:
            return False
        
        # Must not exceed reasonable maximum (1,000,000)
        if quantity_int > 1000000:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_vat_rate(vat_rate: Union[str, float, int]) -> bool:
    """Validate VAT rate percentage"""
    try:
        vat_float = float(vat_rate)
        
        # Must be between 0 and 100
        if vat_float < 0 or vat_float > 100:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_category(category: str) -> bool:
    """Validate product category"""
    valid_categories = ['Food', 'Household', 'Sweets', 'Cooldrinks', 'Other']
    return category in valid_categories

def validate_expiry_date(expiry_date: Optional[Union[str, date]]) -> bool:
    """Validate expiry date"""
    if expiry_date is None:
        return True  # Expiry date is optional
    
    if isinstance(expiry_date, date):
        # Must be in the future or today
        return expiry_date >= date.today()
    
    if isinstance(expiry_date, str):
        try:
            # Try to parse date string (YYYY-MM-DD format)
            parsed_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            return parsed_date >= date.today()
        except ValueError:
            return False
    
    return False

def validate_username(username: str) -> bool:
    """Validate username"""
    if not username or not username.strip():
        return False
    
    # Must be between 3 and 50 characters
    username = username.strip()
    if len(username) < 3 or len(username) > 50:
        return False
    
    # Must contain only alphanumeric characters and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    
    return True

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if not password:
        return False
    
    # Must be at least 6 characters
    if len(password) < 6:
        return False
    
    # Must contain at least one letter and one number
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_number = bool(re.search(r'[0-9]', password))
    
    return has_letter and has_number

def validate_user_role(role: str) -> bool:
    """Validate user role"""
    valid_roles = ['admin', 'pos_operator', 'stock_manager']
    return role in valid_roles

def validate_payment_method(payment_method: str) -> bool:
    """Validate payment method"""
    valid_methods = ['cash', 'card', 'mixed']
    return payment_method in valid_methods

def validate_cash_amount(amount: Union[str, float, int], total_due: float = 0) -> bool:
    """Validate cash payment amount"""
    try:
        amount_float = float(amount)
        
        # Must be non-negative
        if amount_float < 0:
            return False
        
        # For cash payments, should be at least the total due
        # (though we allow overpayment for change)
        if total_due > 0 and amount_float < total_due:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_transaction_ref(transaction_ref: str) -> bool:
    """Validate transaction reference format"""
    if not transaction_ref or not transaction_ref.strip():
        return False
    
    # Expected format: TXN-XXXXXXXX (8 hex characters)
    pattern = r'^TXN-[A-F0-9]{8}$'
    return bool(re.match(pattern, transaction_ref.strip()))

def sanitize_string(input_str: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not input_str:
        return ""
    
    # Strip whitespace and limit length
    sanitized = input_str.strip()[:max_length]
    
    # Remove any null bytes
    sanitized = sanitized.replace('\x00', '')
    
    return sanitized

def format_currency(amount: Union[str, float, int], currency: str = "ZAR") -> str:
    """Format amount as currency string"""
    try:
        amount_float = float(amount)
        if currency == "ZAR":
            return f"R{amount_float:.2f}"
        else:
            return f"{currency} {amount_float:.2f}"
    except (ValueError, TypeError):
        return f"{currency} 0.00"

def parse_currency(currency_str: str) -> float:
    """Parse currency string to float"""
    try:
        # Remove currency symbols and spaces
        clean_str = re.sub(r'[^\d.-]', '', currency_str)
        return float(clean_str)
    except (ValueError, TypeError):
        return 0.0
