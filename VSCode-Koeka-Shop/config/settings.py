"""
System settings and configuration for Tembie's Spaza Shop POS System
Centralized configuration management
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from core.database.connection import get_db_manager

@dataclass
class SystemSettings:
    """System configuration settings"""
    # General
    shop_name: str = "Tembie's Spaza Shop"
    shop_address: str = ""
    shop_phone: str = ""
    shop_email: str = ""
    theme: str = "default"
    language: str = "en"
    timezone: str = "Africa/Johannesburg"
    
    # Business
    vat_registered: bool = True
    vat_number: str = ""
    default_vat_rate: float = 15.0
    vat_inclusive_default: bool = True
    currency: str = "ZAR"
    currency_symbol: str = "R"
    receipt_header: str = ""
    receipt_footer: str = "Thank you for your business!"
    
    # System
    database_path: str = ""
    auto_backup: bool = True
    backup_frequency: str = "daily"  # daily, weekly, monthly
    auto_logout_minutes: int = 30
    require_login: bool = True
    audit_logging: bool = True
    barcode_scanner_enabled: bool = False
    receipt_printer_enabled: bool = False
    cash_drawer_enabled: bool = False
    
    # Legacy fields for backward compatibility
    vat_rate: float = 15.0
    low_stock_threshold: int = 5
    receipt_auto_close: bool = False
    receipt_auto_close_seconds: int = 30

class SettingsManager:
    """Manages system settings and configuration"""
    
    def __init__(self):
        self.db = get_db_manager()
        self._settings_cache: Optional[SystemSettings] = None
    
    def get_settings(self) -> SystemSettings:
        """Get current system settings"""
        if self._settings_cache is None:
            self._load_settings()
        return self._settings_cache
    
    def _load_settings(self):
        """Load settings from database"""
        query = "SELECT key, value FROM system_config"
        results = self.db.execute_query(query)
        
        config_dict = {}
        for row in results:
            config_dict[row['key']] = row['value']
        
        # Create settings object with defaults
        self._settings_cache = SystemSettings(
            # General
            shop_name=config_dict.get('shop_name', "Tembie's Spaza Shop"),
            shop_address=config_dict.get('shop_address', ""),
            shop_phone=config_dict.get('shop_phone', ""),
            shop_email=config_dict.get('shop_email', ""),
            theme=config_dict.get('theme', "default"),
            language=config_dict.get('language', "en"),
            timezone=config_dict.get('timezone', "Africa/Johannesburg"),
            
            # Business
            vat_registered=config_dict.get('vat_registered', 'true').lower() == 'true',
            vat_number=config_dict.get('vat_number', ""),
            default_vat_rate=float(config_dict.get('default_vat_rate', 15.0)),
            vat_inclusive_default=config_dict.get('vat_inclusive_default', 'true').lower() == 'true',
            currency=config_dict.get('currency', 'ZAR'),
            currency_symbol=config_dict.get('currency_symbol', 'R'),
            receipt_header=config_dict.get('receipt_header', ""),
            receipt_footer=config_dict.get('receipt_footer', "Thank you for your business!"),
            
            # System
            database_path=config_dict.get('database_path', ""),
            auto_backup=config_dict.get('auto_backup', 'true').lower() == 'true',
            backup_frequency=config_dict.get('backup_frequency', 'daily'),
            auto_logout_minutes=int(config_dict.get('auto_logout_minutes', 30)),
            require_login=config_dict.get('require_login', 'true').lower() == 'true',
            audit_logging=config_dict.get('audit_logging', 'true').lower() == 'true',
            barcode_scanner_enabled=config_dict.get('barcode_scanner_enabled', 'false').lower() == 'true',
            receipt_printer_enabled=config_dict.get('receipt_printer_enabled', 'false').lower() == 'true',
            cash_drawer_enabled=config_dict.get('cash_drawer_enabled', 'false').lower() == 'true',
            
            # Legacy fields for backward compatibility
            vat_rate=float(config_dict.get('vat_rate', 15.0)),
            low_stock_threshold=int(config_dict.get('low_stock_threshold', 5)),
            receipt_auto_close=config_dict.get('receipt_auto_close', 'false').lower() == 'true',
            receipt_auto_close_seconds=int(config_dict.get('receipt_auto_close_seconds', 30))
        )
    
    def update_setting(self, key: str, value: str, user_id: int) -> bool:
        """Update a single setting"""
        query = """
            INSERT OR REPLACE INTO system_config (key, value, updated_by, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        success = self.db.execute_update(query, (key, value, user_id)) > 0
        
        if success:
            self._settings_cache = None  # Clear cache to force reload
        
        return success
    
    def update_settings(self, settings: SystemSettings, user_id: int) -> bool:
        """Update multiple settings"""
        settings_dict = {
            # General
            'shop_name': settings.shop_name,
            'shop_address': settings.shop_address,
            'shop_phone': settings.shop_phone,
            'shop_email': settings.shop_email,
            'theme': settings.theme,
            'language': settings.language,
            'timezone': settings.timezone,
            
            # Business
            'vat_registered': 'true' if settings.vat_registered else 'false',
            'vat_number': settings.vat_number,
            'default_vat_rate': str(settings.default_vat_rate),
            'vat_inclusive_default': 'true' if settings.vat_inclusive_default else 'false',
            'currency': settings.currency,
            'currency_symbol': settings.currency_symbol,
            'receipt_header': settings.receipt_header,
            'receipt_footer': settings.receipt_footer,
            
            # System
            'database_path': settings.database_path,
            'auto_backup': 'true' if settings.auto_backup else 'false',
            'backup_frequency': settings.backup_frequency,
            'auto_logout_minutes': str(settings.auto_logout_minutes),
            'require_login': 'true' if settings.require_login else 'false',
            'audit_logging': 'true' if settings.audit_logging else 'false',
            'barcode_scanner_enabled': 'true' if settings.barcode_scanner_enabled else 'false',
            'receipt_printer_enabled': 'true' if settings.receipt_printer_enabled else 'false',
            'cash_drawer_enabled': 'true' if settings.cash_drawer_enabled else 'false',
            
            # Legacy fields for backward compatibility
            'vat_rate': str(settings.vat_rate),
            'low_stock_threshold': str(settings.low_stock_threshold),
            'receipt_auto_close': 'true' if settings.receipt_auto_close else 'false',
            'receipt_auto_close_seconds': str(settings.receipt_auto_close_seconds)
        }
        
        query = """
            INSERT OR REPLACE INTO system_config (key, value, updated_by, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        try:
            for key, value in settings_dict.items():
                self.db.execute_update(query, (key, value, user_id))
            
            self._settings_cache = None  # Clear cache to force reload
            return True
        except Exception:
            return False
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Get a single setting value"""
        query = "SELECT value FROM system_config WHERE key = ?"
        results = self.db.execute_query(query, (key,))
        
        if results:
            return results[0]['value']
        return default
    
    def reset_to_defaults(self, user_id: int) -> bool:
        """Reset all settings to defaults"""
        default_settings = SystemSettings()
        return self.update_settings(default_settings, user_id)
    
    def export_settings(self) -> Dict[str, Any]:
        """Export settings for backup/restore"""
        settings = self.get_settings()
        return {
            'shop_name': settings.shop_name,
            'vat_rate': settings.vat_rate,
            'currency': settings.currency,
            'receipt_footer': settings.receipt_footer,
            'low_stock_threshold': settings.low_stock_threshold,
            'backup_enabled': settings.backup_enabled,
            'backup_frequency': settings.backup_frequency,
            'auto_logout_minutes': settings.auto_logout_minutes,
            'receipt_auto_close': settings.receipt_auto_close,
            'receipt_auto_close_seconds': settings.receipt_auto_close_seconds
        }
    
    def import_settings(self, settings_dict: Dict[str, Any], user_id: int) -> bool:
        """Import settings from backup/restore"""
        try:
            settings = SystemSettings(
                shop_name=settings_dict.get('shop_name', "Tembie's Spaza Shop"),
                vat_rate=float(settings_dict.get('vat_rate', 15.0)),
                currency=settings_dict.get('currency', 'ZAR'),
                receipt_footer=settings_dict.get('receipt_footer', "Thank you for your business!"),
                low_stock_threshold=int(settings_dict.get('low_stock_threshold', 5)),
                backup_enabled=bool(settings_dict.get('backup_enabled', True)),
                backup_frequency=settings_dict.get('backup_frequency', 'daily'),
                auto_logout_minutes=int(settings_dict.get('auto_logout_minutes', 30)),
                receipt_auto_close=bool(settings_dict.get('receipt_auto_close', False)),
                receipt_auto_close_seconds=int(settings_dict.get('receipt_auto_close_seconds', 30))
            )
            
            return self.update_settings(settings, user_id)
        except (ValueError, TypeError):
            return False

# Global settings manager instance
settings_manager = SettingsManager()

def get_settings_manager() -> SettingsManager:
    """Get the global settings manager instance"""
    return settings_manager
