#  INSTALLATION GUIDE
# Tembie's Spaza Shop POS System

##  Overview
This guide will walk you through installing and setting up Tembie's Spaza Shop POS System on your computer. The system is designed to be simple, reliable, and work offline with minimal technical requirements.

##  System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, Linux, or macOS
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space (2GB recommended for data growth)
- **Python**: Version 3.8 or higher
- **Display**: 1024x768 minimum resolution (1366x768 recommended)

### Recommended Hardware
- **Computer**: Desktop or laptop with keyboard and mouse
- **Display**: 19" monitor or larger for comfortable operation
- **Backup**: USB drive for regular data backups
- **Optional**: Barcode scanner (can be added later)
- **Optional**: Receipt printer (thermal printer recommended)

##  Installation Steps

### Step 1: Install Python

**Windows:**
1. Go to [python.org](https://python.org/downloads)
2. Download Python 3.11 or newer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt and typing:
   ```cmd
   python --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

**macOS:**
```bash
# Install using Homebrew (recommended)
brew install python-tk
```

### Step 2: Download the POS System

**Option A: Download ZIP File**
1. Download the system files to your computer
2. Extract to a folder like `C:\POS-System\` (Windows) or `/home/username/POS-System/` (Linux)

**Option B: Git Clone (if you have Git)**
```bash
git clone [repository-url] POS-System
cd POS-System
```

### Step 3: Install Dependencies

Open Command Prompt/Terminal in the POS system folder:

**Windows:**
```cmd
cd C:\POS-System\VSCode-Koeka-Shop
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
cd /path/to/POS-System/VSCode-Koeka-Shop
pip3 install -r requirements.txt
```

### Step 4: Initialize the System

Run the initialization test:
```bash
python test_core_functionality.py
```

You should see:
```
 Database initialization successful
 All core functionality tests PASSED!
```

### Step 5: First Time Setup

**Start the Application:**
```bash
python app.py
```

**Default Login Credentials:**
- **Admin User**: `admin` / `admin123`
- **POS User**: `demo` / `demo123`

##  Quick Start Guide

### 1. Initial Configuration

**Login as Admin:**
1. Start the application: `python app.py`
2. Login with: `admin` / `admin123`
3. Click "Settings" to configure your shop

**Shop Settings:**
- Shop Name: "Tembie's Spaza Shop" (or your shop name)
- Address: Your shop address
- Phone: Your contact number
- VAT Rate: 15% (South African standard)

**Create Your First Products:**
1. Go to "Product Management"
2. Click "Add New Product"
3. Enter product details:
   - Name: e.g., "Coca Cola 330ml"
   - Category: "Cooldrinks"
   - Cost Price: What you pay suppliers
   - Selling Price: What customers pay
   - Current Stock: How many you have
   - Minimum Stock: Reorder level

### 2. Daily Operations

**Morning Startup:**
1. Start application: `python app.py`
2. Login as POS operator
3. Start a new sale by clicking "Sales"

**Making a Sale:**
1. Search/scan for products
2. Add items to sale
3. Choose payment method (Cash/Card)
4. Complete sale
5. Show receipt to customer (or SMS if requested)

**End of Day:**
1. Go to "Reports" → "Cash Management"
2. Count your till
3. Reconcile cash (compare expected vs actual)
4. Generate daily report

## ️ Troubleshooting

### Common Issues

**"Python not found" Error:**
- Ensure Python is installed and added to PATH
- Restart Command Prompt/Terminal after Python installation

**"Module not found" Error:**
- Run: `pip install -r requirements.txt`
- Ensure you're in the correct folder

**Database Errors:**
- Delete `spaza_shop.db` file and restart application
- System will recreate a fresh database

**GUI Not Starting:**
- Ensure you have tkinter installed:
  ```bash
  python -c "import tkinter; print('GUI ready')"
  ```

**Performance Issues:**
- Close other programs to free RAM
- Ensure at least 500MB free disk space

### Getting Help

1. **Check Error Messages**: Look for specific error descriptions
2. **Restart Application**: Close and restart can fix temporary issues
3. **Check File Permissions**: Ensure the POS folder is writable
4. **Update Python**: Use Python 3.9+ for best compatibility

##  Security Setup

### User Management

**Create Shop Staff Accounts:**
1. Login as admin
2. Go to Settings → Users
3. Add new users with appropriate roles:
   - **Admin**: Full access (shop owner)
   - **POS Operator**: Sales only (cashiers)
   - **Stock Manager**: Inventory management

**Password Security:**
- Use strong passwords (mix of letters, numbers)
- Change default passwords immediately
- Don't share admin credentials

### Data Protection

**Daily Backups:**
1. Copy `spaza_shop.db` file daily
2. Store on USB drive or cloud storage
3. Keep backups in safe location

**Database Location:**
```
Windows: C:\POS-System\VSCode-Koeka-Shop\spaza_shop.db
Linux: /path/to/POS-System/VSCode-Koeka-Shop/spaza_shop.db
```

##  Hardware Integration

### Barcode Scanner Setup

**USB Barcode Scanners:**
1. Connect scanner to USB port
2. Scanner appears as keyboard input
3. Test by scanning into a text editor
4. In POS: Scanner input goes directly to product search

**Recommended Scanners:**
- Any USB "keyboard wedge" barcode scanner
- 1D/2D scanner capability preferred
- Price range: R300-R800

### Receipt Printer Setup

**Thermal Printers (Future Enhancement):**
- 58mm or 80mm thermal printers
- USB or network connection
- ESC/POS command compatible

**Current Solution:**
- Display receipt on screen
- Customer can photograph with phone
- Clear, readable format optimized for photos

##  Data Management

### Regular Maintenance

**Weekly Tasks:**
- Backup database file
- Review low stock alerts
- Check cash reconciliation accuracy

**Monthly Tasks:**
- Generate monthly reports
- Review product performance
- Update product prices if needed
- Clean up old transaction data (optional)

### Export Data

**For Accounting:**
1. Go to Reports → Monthly Report
2. Use Export function for accounting software
3. Available formats: CSV, text summary

**For Tax Purposes:**
- VAT reports available in Reports section
- Keep monthly backups for SARS compliance

##  Training Resources

### New User Training

**Shop Owner (Admin) - 4 Hours:**
1. System overview and navigation (1 hour)
2. Product management and pricing (1 hour)
3. Reports and cash management (1 hour)
4. User management and troubleshooting (1 hour)

**Cashier (POS Operator) - 2 Hours:**
1. Login and daily startup (30 minutes)
2. Processing sales and payments (1 hour)
3. Handling returns and voids (30 minutes)

**Stock Manager - 2 Hours:**
1. Adding and editing products (1 hour)
2. Stock adjustments and counts (1 hour)

### Quick Reference Cards

**Daily Startup Checklist:**
- [ ] Start application
- [ ] Login with correct user
- [ ] Verify opening till amount
- [ ] Check low stock alerts

**End of Day Checklist:**
- [ ] Complete final sale
- [ ] Count physical cash
- [ ] Reconcile in system
- [ ] Generate daily report
- [ ] Backup database

##  Support Information

### Self-Help Resources
- Check error messages carefully
- Restart application for temporary issues
- Refer to this installation guide
- Use the CLI demo for testing: `python demo_cli.py`

### System Files Overview

**Key Files:**
- `app.py` - Main application launcher
- `spaza_shop.db` - Your business data (BACKUP REGULARLY!)
- `requirements.txt` - Python dependencies
- `test_core_functionality.py` - System health check

**Folders:**
- `core/` - Essential system functions
- `modules/` - Optional features (reporting, etc.)
- `config/` - System settings

##  Installation Verification

Run these commands to verify your installation:

```bash
# Test database and core functions
python test_core_functionality.py

# Test all GUI interfaces
python test_gui_interfaces.py

# Start the main application
python app.py
```

**Success Indicators:**
- All tests show "PASSED"
- Login screen appears when running app.py
- Can login with demo credentials
- Product management opens without errors

##  You're Ready!

Your Tembie's Spaza Shop POS System is now installed and ready for use. Start with the admin account to configure your shop settings, add your products, and create user accounts for your staff.

**Remember:**
- Backup your data regularly
- Start with a few products to learn the system
- Use the demo credentials initially, then create proper accounts
- Keep this guide handy for reference

**Happy selling! **

---
*For technical issues beyond this guide, check the error messages and try restarting the application. Most issues resolve with a fresh restart.*
