# Point of Sale System for Tembie's Spaza Shop

A comprehensive, zero-cost Point of Sale system designed for rural spaza shops in South Africa. Built with Python and SQLite for maximum compatibility and minimal dependencies.

## Quick Start

### Easy Installation (Recommended)

For the best installation experience, see our **[Master Installation Guide](MASTER_INSTALLATION_GUIDE.md)** which provides 6 different installation methods.

**Quick Options:**
- **Windows:** Run `.\install_wizard.ps1` (PowerShell)
- **All Platforms:** Run `python universal_installer.py`
- **Manual:** Follow the steps below

### 1. Manual Setup
```bash
# Clone or download the project
cd VSCode-Koeka-Shop

# Install dependencies (minimal requirements)
pip install -r requirements.txt

# Initialize the system
python app.py
```

**Default Login:** Username: `admin` | Password: `admin123`

### 2. Test Core Functionality
```bash
# Run comprehensive tests
python test_core_functionality.py

# Try the interactive CLI demo
python demo_cli.py
```

## Current Implementation Status

### CORE FEATURES IMPLEMENTED
- **Database Schema** - Complete SQLite setup with all required tables
- **Product Management** - CRUD operations, stock tracking, barcode support
- **Sales Processing** - Multi-item transactions, payment handling, stock reduction
- **Receipt Generation** - Screen display optimized for mobile photography
- **Payment Processing** - Cash, card, and mixed payment methods
- **Stock Management** - Dual stock levels, movement tracking, audit trail
- **VAT Calculations** - 15% VAT handling (inclusive/exclusive)
- **Data Validation** - Comprehensive input validation and security
- **Settings Management** - Configurable system parameters

### IN DEVELOPMENT
- **User Management** - Authentication and role-based access
- **GUI Interface** - Tkinter-based user interface
- **Daily Cash Management** - Till reconciliation and reporting
- **Basic Reporting** - Daily and monthly reports

### PLANNED FEATURES
- **Barcode Scanner Integration**
- **Backup & Restore System**
- **Advanced Reporting & Analytics**
- **Customer Credit Management**
- **Supplier Management**

## ️ Project Structure

```
VSCode-Koeka-Shop/
├── core/                          # Core POS system
│   ├── database/                  # Database management
│   ├── products/                  # Product CRUD & stock management
│   ├── sales/                     # Transaction processing & receipts
│   └── ui/                        # User interface (planned)
├── modules/                       # Optional add-on modules
│   ├── customer_accounts/         # Customer & credit management
│   ├── inventory_management/      # Advanced stock features
│   ├── basic_reporting/           # Reports and analytics
│   └── [other modules]/
├── config/                        # Configuration management
├── utils/                         # Shared utilities
├── tests/                         # Test files
├── main.py                        # Application entry point
├── demo_cli.py                    # Interactive CLI demonstration
└── test_core_functionality.py    # Core system tests
```

##  Key Features

### Sales Processing
- **Multi-item transactions** with quantity adjustments
- **Barcode scanning support** (hardware to be purchased)
- **Manual product lookup** and search
- **Real-time stock reduction** during sales
- **Transaction void capability** with stock restoration

### Payment Handling
- **Cash payments** with change calculation
- **Card payments** (manual entry)
- **Mixed payments** (partial cash, partial card)
- **Payment validation** and reconciliation

### Receipt System
- **Screen display** optimized for mobile phone photography
- **Professional formatting** with all required details
- **Configurable shop name** and footer messages
- **Future thermal printer** support ready

### Stock Management
- **Dual stock levels** (monthly target + minimum safety)
- **Automatic stock reduction** on sales
- **Manual adjustments** for damage, theft, spoilage
- **Complete audit trail** of all stock movements
- **Low stock alerts** and reorder notifications

### Product Management
- **Complete product catalog** with categories
- **Barcode support** for efficient scanning
- **VAT handling** (15% inclusive/exclusive)
- **Expiry date tracking** for perishables
- **Cost and selling price** management

##  Demo Usage

### CLI Demo Features
The `demo_cli.py` provides a full interactive demonstration:

1. **View Products** - Browse the complete catalog
2. **Add Products** - Create new products with validation
3. **Process Sales** - Complete transaction workflow
4. **View History** - See daily sales summary
5. **Stock Alerts** - Check low stock warnings
6. **Receipt Display** - Generate formatted receipts

### Sample Data
Run `python main.py` and choose 'y' to create sample products:
- Coca Cola 330ml (Cooldrinks)
- White Bread 700g (Food)
- Simba Chips 120g (Sweets)

##  Technical Details

### Technology Stack
- **Python 3.8+** - Main programming language
- **SQLite** - Embedded database (zero installation)
- **Tkinter** - GUI framework (planned, built into Python)
- **Zero external dependencies** for core functionality

### Database Schema
Complete schema includes:
- `products` - Product catalog with stock levels
- `sales` & `sale_items` - Transaction records
- `stock_movements` - Complete audit trail
- `users` - User management and roles
- `daily_cash` - Till reconciliation
- `system_config` - Configurable settings

### Data Validation
- Input sanitization and validation
- Business rule enforcement
- Audit trail for all changes
- Password hashing and security

##  Business Requirements

This system implements the complete functional specification for rural spaza shops:

### Real-World Constraints Addressed
- **Transport limitations** - Optimal reorder calculations
- **Cash flow management** - Till reconciliation
- **Variable technical skills** - Simple, intuitive interface
- **No printer initially** - Mobile-optimized receipt display

### Rural Business Features
- **Dual stock system** for monthly supply runs
- **Credit management** for community customers
- **Flexible payment methods** for rural economy
- **Offline operation** with no internet dependency

##  Next Development Phase

1. **User Authentication** - Login system with role-based access
2. **Tkinter GUI** - Professional desktop interface
3. **Daily Cash Management** - Till reconciliation features
4. **Reporting System** - Business intelligence and analytics
5. **Module System** - Plugin architecture for optional features

##  Documentation

- **functional_specification_complete.md** - Complete business requirements
- **Code Documentation** - Inline comments and docstrings
- **Test Coverage** - Comprehensive test suite

##  Support

This system is designed for Tembie's spaza shop and similar rural businesses. The modular architecture allows for customization and expansion as the business grows.

**Core System**: Free and open source
**Optional Modules**: Available as business needs develop
**Training**: Built-in help and documentation

---

**Built for South African spaza shops - Simple, reliable, and designed to grow with your business. **
