# Koeka Shop POS - Master Installation Guide

**Complete installation options for the Koeka Shop Point of Sale System**

---

## Quick Start (Choose Your Method)

| Installation Type | File | Best For | Difficulty |
|------------------|------|----------|------------|
| **One-Click Windows** | `install_wizard.ps1` | Windows users | Easy |
| **Universal Installer** | `universal_installer.py` | All platforms | Easy |
| **Professional .exe** | `installer.nsi` → Compile | Distribution | Medium |
| **Basic Scripts** | `install.bat` / `install.sh` | Quick setup | Easy |
| **GUI Wizard** | `install_wizard.py` | Visual interface | Easy |
| **Standalone App** | `setup_executable.py` | No Python needed | Advanced |

---

## Prerequisites

Before installation, ensure you have:

- **Python 3.8 or higher**  
- **pip** (Python package installer)  
- **Internet connection** (for dependencies)  

**Check your Python version:**
```bash
python --version
```

---

## Installation Methods

### Method 1: PowerShell Wizard (Windows) - RECOMMENDED
**Best for: Windows users who want a complete automated setup**

```powershell
# Option A: Basic installation
.\install_wizard.ps1

# Option B: Custom installation
.\install_wizard.ps1 -CreateShortcuts $false -CreateDemoData $false
```

**What it does:**
- Checks Python installation
- Installs dependencies automatically
- Sets up database with demo data
- Creates desktop & start menu shortcuts
- Creates launch scripts
- Full validation and error handling

**Output:** Ready-to-use POS system with shortcuts

---

### Method 2: Universal Cross-Platform Installer - RECOMMENDED
**Best for: Linux, macOS, or advanced Windows users**

```bash
python universal_installer.py
```

**What it does:**
- Works on Windows, Linux, and macOS
- Auto-detects operating system
- Creates platform-specific shortcuts
- Comprehensive system testing
- Professional installation experience

**Output:** Fully configured POS system for any platform

---

### Method 3: Professional Windows Installer (.exe)
**Best for: Professional distribution and deployment**

#### Step 1: Install NSIS
Download and install NSIS from: https://nsis.sourceforge.io/

#### Step 2: Compile Installer
```bash
# Navigate to project directory
cd path\to\koeka-shop-pos

# Compile the installer
makensis installer.nsi
```

#### Step 3: Distribute
```
Creates: KoekaShopPOS_Setup.exe
Professional Windows installer
Add/Remove Programs integration
Automatic uninstaller
Component selection
```

**Perfect for:** Software distribution, enterprise deployment

---

### Method 4: Basic Automated Scripts
**Best for: Quick setup without bells and whistles**

#### Windows:
```cmd
install.bat
```

#### Linux/macOS:
```bash
chmod +x install.sh
./install.sh
```

**What it does:**
- Installs dependencies
- Sets up database
- Basic validation
- No shortcuts or advanced features

---

### Method 5: GUI Installation Wizard
**Best for: Users who prefer graphical interfaces**

```bash
python install_wizard.py
```

**Features:**
- Step-by-step GUI wizard
- Progress bars and visual feedback
- Error handling with user prompts
- Cross-platform compatibility

---

### Method 6: Standalone Executable
**Best for: Computers without Python installed**

#### Step 1: Install cx_Freeze
```bash
pip install cx_Freeze
```

#### Step 2: Build Executable
```bash
python setup_executable.py build
```

#### Step 3: Distribute
```
Creates: build/exe.win-amd64-3.x/app.exe
No Python installation required
Bundles all dependencies
Single executable file
```

---

## Manual Installation (Advanced Users)

If you prefer to install manually or troubleshoot issues:

```bash
# 1. Navigate to project directory
cd koeka-shop-pos

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Initialize database
python -c "from core.database.connection import get_db_manager; get_db_manager().initialize_schema()"

# 4. Create demo user (admin/admin123)
python -c "from core.auth.authentication import ensure_demo_user; ensure_demo_user()"

# 5. Run the application
python app.py
```

---

## Starting the Application

After installation, you can start Koeka Shop POS using:

### Windows:
```powershell
# Double-click files:
start_koeka_pos_gui.bat     # Silent start (recommended)
start_koeka_pos.bat         # With console window

# Or use shortcuts:
Desktop shortcut
Start Menu → Koeka Shop POS

# Command line:
python app.py
```

### Linux/macOS:
```bash
# Shell script:
./start_koeka_pos.sh

# Desktop shortcut (if created)
Double-click desktop icon

# Command line:
python app.py
```

---

## Default Login Credentials

After installation, log in with:

**Username:** `admin`  
**Password:** `admin123`

> **Security Note:** Change the default password after first login

---

## Post-Installation File Structure

```
koeka-shop-pos/
├── app.py                     # Main application
├── spaza_shop.db             # SQLite database  
├── config.json               # Installation config
├── start_koeka_pos.*         # Launch scripts
├── requirements.txt          # Dependencies
├── core/                     # Core modules
│   ├── auth/                    # Authentication
│   ├── database/                # Database management
│   ├── products/                # Product management
│   ├── sales/                   # Sales & transactions
│   └── ui/                      # User interface
├── modules/                  # Optional features
│   ├── barcode_scanner/         # Barcode scanning
│   ├── basic_reporting/         # Reports
│   ├── customer_accounts/       # Customer management
│   └── inventory_management/    # Stock management
└── utils/                    # Utility functions
```

---

## Troubleshooting

### Common Issues & Solutions

#### "Python not found"
```bash
# Install Python 3.8+ from python.org
# Ensure "Add Python to PATH" is checked during installation
```

#### "Module not found" errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

#### Database errors
```bash
# Delete database and reinitialize
del spaza_shop.db  # Windows
rm spaza_shop.db   # Linux/macOS

# Re-run installer or manual setup
```

#### GUI not starting (Linux)
```bash
# Install tkinter
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install tkinter          # CentOS/RHEL
```

#### Permission errors (Windows)
```powershell
# Run PowerShell as Administrator
# Or change execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Which Installation Method Should I Choose?

### For Most Users:
- **Windows:** Use `install_wizard.ps1` (PowerShell wizard)
- **Mac/Linux:** Use `universal_installer.py`

### For Software Distribution:
- **Professional:** Compile `installer.nsi` to create .exe installer
- **Portable:** Use `setup_executable.py` to create standalone app

### For Developers:
- **Quick Setup:** Use `install.bat` or `install.sh`
- **Manual Control:** Follow manual installation steps

### For Non-Technical Users:
- **GUI Interface:** Use `install_wizard.py` (graphical)
- **One-Click:** Use PowerShell wizard with shortcuts

---

## Installation Success Checklist

After installation, verify everything works:

- [ ] Application starts without errors
- [ ] Login with admin/admin123 works
- [ ] Can add/edit products
- [ ] Can process test sale
- [ ] Reports generate correctly
- [ ] Database saves data properly

---

## Getting Help

If you encounter issues:

1. **Check this guide** for troubleshooting steps
2. **Review error messages** carefully
3. **Check Python version** (must be 3.8+)
4. **Verify file permissions** 
5. **Try manual installation** if automated methods fail

**Additional Documentation:**
- `README.md` - Project overview
- `QUICK_START.md` - Getting started guide
- `INSTALLATION_GUIDE.md` - Technical details
- `SMS_FUNCTIONALITY_GUIDE.md` - SMS features

---

## Success!

Once installed, you'll have a complete Point of Sale system with:

- **Product Management** - Add, edit, delete products  
- **Sales Processing** - Process transactions with receipts  
- **Cash Management** - Track cash drawer operations  
- **User Authentication** - Secure login system  
- **Reporting** - Daily sales and inventory reports  
- **SMS Integration** - Send receipts via SMS  
- **Modular Design** - Optional features available  

**Welcome to Koeka Shop POS!**
