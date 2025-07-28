"""
Module registry for tracking installed optional modules
Manages the modular system architecture described in the specification
"""

from typing import Dict, List, Set
from dataclasses import dataclass
from core.database.connection import get_db_manager

@dataclass
class ModuleInfo:
    """Information about an optional module"""
    name: str
    version: str
    tier: int  # 1, 2, 3 as per specification
    description: str
    dependencies: List[str]  # List of required modules
    enabled: bool = True

class ModuleRegistry:
    """Manages optional module registration and dependencies"""
    
    # Define available modules as per specification
    AVAILABLE_MODULES = {
        # Tier 1 Modules (Most Popular)
        'customer_accounts': ModuleInfo(
            name='Customer Accounts',
            version='1.0.0',
            tier=1,
            description='Credit tracking and customer database',
            dependencies=['core']
        ),
        'inventory_management': ModuleInfo(
            name='Inventory Management',
            version='1.0.0',
            tier=1,
            description='Stock alerts and reorder points',
            dependencies=['core']
        ),
        'basic_reporting': ModuleInfo(
            name='Basic Reporting',
            version='1.0.0',
            tier=1,
            description='Daily and weekly sales reports',
            dependencies=['core']
        ),
        
        # Tier 2 Modules (Business Growth)
        'supplier_management': ModuleInfo(
            name='Supplier Management',
            version='1.0.0',
            tier=2,
            description='Purchase orders and supplier tracking',
            dependencies=['core', 'inventory_management']
        ),
        'barcode_scanner': ModuleInfo(
            name='Barcode Scanner',
            version='1.0.0',
            tier=2,
            description='Product scanning capability',
            dependencies=['core']
        ),
        'advanced_reporting': ModuleInfo(
            name='Advanced Reporting',
            version='1.0.0',
            tier=2,
            description='Profit analysis, trends, tax reports',
            dependencies=['core', 'basic_reporting']
        ),
        
        # Tier 3 Modules (Advanced Features)
        'mobile_integration': ModuleInfo(
            name='Mobile Integration',
            version='1.0.0',
            tier=3,
            description='SMS notifications and mobile payments',
            dependencies=['core', 'customer_accounts']
        ),
        'loyalty_programs': ModuleInfo(
            name='Loyalty Programs',
            version='1.0.0',
            tier=3,
            description='Points, discounts, customer rewards',
            dependencies=['core', 'customer_accounts']
        )
    }
    
    def __init__(self):
        self.db = get_db_manager()
        self._ensure_registry_table()
    
    def _ensure_registry_table(self):
        """Create module registry table if it doesn't exist"""
        query = """
            CREATE TABLE IF NOT EXISTS module_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                tier INTEGER NOT NULL,
                description TEXT,
                enabled BOOLEAN DEFAULT 1,
                installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.db.execute_update(query)
    
    def register_module(self, module_id: str) -> bool:
        """Register a module as installed"""
        if module_id not in self.AVAILABLE_MODULES:
            return False
        
        module_info = self.AVAILABLE_MODULES[module_id]
        
        query = """
            INSERT OR REPLACE INTO module_registry 
            (module_id, name, version, tier, description, enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        params = (
            module_id, module_info.name, module_info.version,
            module_info.tier, module_info.description, module_info.enabled
        )
        
        return self.db.execute_update(query, params) > 0
    
    def unregister_module(self, module_id: str) -> bool:
        """Unregister a module"""
        query = "DELETE FROM module_registry WHERE module_id = ?"
        return self.db.execute_update(query, (module_id,)) > 0
    
    def enable_module(self, module_id: str) -> bool:
        """Enable a registered module"""
        query = """
            UPDATE module_registry 
            SET enabled = 1, updated_at = CURRENT_TIMESTAMP 
            WHERE module_id = ?
        """
        return self.db.execute_update(query, (module_id,)) > 0
    
    def disable_module(self, module_id: str) -> bool:
        """Disable a registered module"""
        query = """
            UPDATE module_registry 
            SET enabled = 0, updated_at = CURRENT_TIMESTAMP 
            WHERE module_id = ?
        """
        return self.db.execute_update(query, (module_id,)) > 0
    
    def is_module_installed(self, module_id: str) -> bool:
        """Check if a module is installed"""
        query = "SELECT id FROM module_registry WHERE module_id = ?"
        results = self.db.execute_query(query, (module_id,))
        return len(results) > 0
    
    def is_module_enabled(self, module_id: str) -> bool:
        """Check if a module is enabled"""
        query = "SELECT enabled FROM module_registry WHERE module_id = ?"
        results = self.db.execute_query(query, (module_id,))
        
        if results:
            return bool(results[0]['enabled'])
        return False
    
    def get_installed_modules(self) -> List[Dict]:
        """Get list of all installed modules"""
        query = """
            SELECT module_id, name, version, tier, description, enabled, installed_at
            FROM module_registry
            ORDER BY tier, name
        """
        results = self.db.execute_query(query)
        return [dict(row) for row in results]
    
    def get_enabled_modules(self) -> List[Dict]:
        """Get list of enabled modules"""
        query = """
            SELECT module_id, name, version, tier, description, installed_at
            FROM module_registry
            WHERE enabled = 1
            ORDER BY tier, name
        """
        results = self.db.execute_query(query)
        return [dict(row) for row in results]
    
    def get_available_modules(self) -> Dict[str, ModuleInfo]:
        """Get all available modules"""
        return self.AVAILABLE_MODULES.copy()
    
    def get_modules_by_tier(self, tier: int) -> List[Dict]:
        """Get modules by tier level"""
        available = {k: v for k, v in self.AVAILABLE_MODULES.items() if v.tier == tier}
        
        result = []
        for module_id, module_info in available.items():
            result.append({
                'module_id': module_id,
                'name': module_info.name,
                'version': module_info.version,
                'tier': module_info.tier,
                'description': module_info.description,
                'dependencies': module_info.dependencies,
                'installed': self.is_module_installed(module_id),
                'enabled': self.is_module_enabled(module_id)
            })
        
        return sorted(result, key=lambda x: x['name'])
    
    def check_dependencies(self, module_id: str) -> Dict[str, bool]:
        """Check if module dependencies are satisfied"""
        if module_id not in self.AVAILABLE_MODULES:
            return {}
        
        module_info = self.AVAILABLE_MODULES[module_id]
        dependency_status = {}
        
        for dep in module_info.dependencies:
            if dep == 'core':
                dependency_status[dep] = True  # Core is always available
            else:
                dependency_status[dep] = self.is_module_enabled(dep)
        
        return dependency_status
    
    def can_install_module(self, module_id: str) -> bool:
        """Check if module can be installed (dependencies satisfied)"""
        deps = self.check_dependencies(module_id)
        return all(deps.values())
    
    def get_installation_summary(self) -> Dict:
        """Get summary of module installation status"""
        installed = self.get_installed_modules()
        
        summary = {
            'total_available': len(self.AVAILABLE_MODULES),
            'total_installed': len(installed),
            'total_enabled': len([m for m in installed if m['enabled']]),
            'by_tier': {
                1: {'installed': 0, 'enabled': 0, 'available': 0},
                2: {'installed': 0, 'enabled': 0, 'available': 0},
                3: {'installed': 0, 'enabled': 0, 'available': 0}
            }
        }
        
        # Count available by tier
        for module_info in self.AVAILABLE_MODULES.values():
            summary['by_tier'][module_info.tier]['available'] += 1
        
        # Count installed/enabled by tier
        for module in installed:
            tier = module['tier']
            summary['by_tier'][tier]['installed'] += 1
            if module['enabled']:
                summary['by_tier'][tier]['enabled'] += 1
        
        return summary

# Global module registry instance
module_registry = ModuleRegistry()

def get_module_registry() -> ModuleRegistry:
    """Get the global module registry instance"""
    return module_registry
