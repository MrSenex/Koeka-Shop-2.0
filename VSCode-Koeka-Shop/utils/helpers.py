"""
Common utility functions for Tembie's Spaza Shop POS System
Provides helper functions used across the application
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List, Union

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    # Generate a random salt
    salt = secrets.token_hex(16)
    
    # Hash password with salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Return salt:hash format
    return f"{salt}:{password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, password_hash = stored_hash.split(':')
        
        # Hash the provided password with the stored salt
        test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # Compare hashes
        return test_hash == password_hash
    except ValueError:
        return False

def generate_transaction_ref() -> str:
    """Generate unique transaction reference"""
    # Use timestamp + random hex for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(4).upper()
    return f"TXN-{timestamp[-8:]}{random_part[:4]}"

def calculate_vat_amount(total_amount: float, vat_rate: float, vat_inclusive: bool = True) -> float:
    """Calculate VAT amount from total"""
    if vat_rate <= 0:
        return 0.0
    
    if vat_inclusive:
        # VAT is included in the total amount
        return total_amount * (vat_rate / (100 + vat_rate))
    else:
        # VAT is added to the total amount
        return total_amount * (vat_rate / 100)

def calculate_subtotal(total_amount: float, vat_rate: float, vat_inclusive: bool = True) -> float:
    """Calculate subtotal (amount before VAT)"""
    if vat_rate <= 0:
        return total_amount
    
    if vat_inclusive:
        # Remove VAT from total
        return total_amount - calculate_vat_amount(total_amount, vat_rate, vat_inclusive)
    else:
        # Subtotal is the same as total when VAT is not included
        return total_amount

def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime to string"""
    if dt is None:
        return ""
    return dt.strftime(format_str)

def format_date(d: date, format_str: str = '%Y-%m-%d') -> str:
    """Format date to string"""
    if d is None:
        return ""
    return d.strftime(format_str)

def parse_datetime(dt_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """Parse string to datetime"""
    try:
        return datetime.strptime(dt_str, format_str)
    except (ValueError, TypeError):
        return None

def parse_date(date_str: str, format_str: str = '%Y-%m-%d') -> Optional[date]:
    """Parse string to date"""
    try:
        return datetime.strptime(date_str, format_str).date()
    except (ValueError, TypeError):
        return None

def get_date_range(start_date: date, end_date: date) -> List[date]:
    """Get list of dates between start and end date (inclusive)"""
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates

def get_month_start_end(year: int, month: int) -> tuple[date, date]:
    """Get first and last day of a month"""
    start_date = date(year, month, 1)
    
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    return start_date, end_date

def round_currency(amount: float, decimal_places: int = 2) -> float:
    """Round amount to specified decimal places"""
    return round(float(amount), decimal_places)

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, return default if division by zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default

def percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0 if new_value == 0 else 100.0
    
    return ((new_value - old_value) / old_value) * 100

def create_backup_filename(prefix: str = "spaza_backup") -> str:
    """Create backup filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.json"

def save_json_file(data: Dict[str, Any], filepath: str) -> bool:
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        return True
    except Exception:
        return False

def load_json_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception:
        return False

def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except (OSError, FileNotFoundError):
        return 0

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with optional suffix"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_filename(filename: str) -> str:
    """Clean filename by removing invalid characters"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    cleaned = filename
    
    for char in invalid_chars:
        cleaned = cleaned.replace(char, '_')
    
    # Remove multiple consecutive underscores
    while '__' in cleaned:
        cleaned = cleaned.replace('__', '_')
    
    # Strip leading/trailing underscores and spaces
    cleaned = cleaned.strip('_ ')
    
    return cleaned if cleaned else "untitled"

def get_business_days_between(start_date: date, end_date: date) -> int:
    """Get number of business days (Mon-Fri) between two dates"""
    current_date = start_date
    business_days = 0
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

def is_weekend(check_date: date) -> bool:
    """Check if date is weekend (Saturday or Sunday)"""
    return check_date.weekday() >= 5  # Saturday = 5, Sunday = 6

def get_quarter_dates(year: int, quarter: int) -> tuple[date, date]:
    """Get start and end dates for a quarter"""
    if quarter not in [1, 2, 3, 4]:
        raise ValueError("Quarter must be 1, 2, 3, or 4")
    
    start_month = (quarter - 1) * 3 + 1
    start_date = date(year, start_month, 1)
    
    end_month = quarter * 3
    if end_month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, end_month + 1, 1) - timedelta(days=1)
    
    return start_date, end_date
