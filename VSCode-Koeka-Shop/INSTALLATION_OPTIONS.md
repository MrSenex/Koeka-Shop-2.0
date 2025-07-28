# Koeka Shop POS - Installation Options

This document describes the various installation methods available for the Koeka Shop Point of Sale system.

## Quick Installation (Recommended)

### Option 1: PowerShell Script (Windows)
```powershell
# Run as Administrator (optional, for system-wide installation)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_wizard.ps1
```

### Option 2: Universal Python Installer (All Platforms)
```bash
python universal_installer.py
```

## Installation Methods Overview

| Method | File | Platform | Features |
|--------|------|----------|----------|
| **Batch Script** | `install.bat` | Windows | Basic automated installation |
| **Shell Script** | `install.sh` | Linux/macOS | Basic automated installation |
| **PowerShell** | `install_wizard.ps1` | Windows | Enhanced with shortcuts & validation |
| **Python Installer** | `install_wizard.py` | All | GUI-based installation wizard |
| **Universal** | `universal_installer.py` | All | Comprehensive cross-platform installer |
| **NSIS Installer** | `installer.nsi` | Windows | Professional .exe installer |
| **Executable** | `setup_executable.py` | All | Create standalone executable |

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **tkinter** (usually included with Python)

## Installation Steps

### 1. Basic Installation
```bash
# Clone or download the project
cd koeka-shop-pos

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from core.database.connection import get_db_manager; get_db_manager().initialize_schema()"

# Create demo user
python -c "from core.auth.authentication import ensure_demo_user; ensure_demo_user()"

# Run the application
python app.py
```

### 2. Using Installation Wizards

#### PowerShell Wizard (Windows)
```powershell
# Navigate to the project directory
cd path\to\koeka-shop-pos

# Run the PowerShell installer
.\install_wizard.ps1

# Optional parameters:
.\install_wizard.ps1 -CreateShortcuts $false -CreateDemoData $false
```

#### Python GUI Installer
```bash
# Run the GUI installer
python install_wizard.py

# Follow the on-screen instructions
```

#### Universal Cross-Platform Installer
```bash
# Works on Windows, Linux, and macOS
python universal_installer.py

# Automatically detects platform and creates appropriate shortcuts
```

### 3. Professional Installation (Windows)

#### Create Windows Installer (.exe)
```bash
# Install NSIS (Nullsoft Scriptable Install System)
# Download from: https://nsis.sourceforge.io/

# Compile the installer script
makensis installer.nsi

# This creates: koeka_shop_pos_installer.exe
```

#### Create Standalone Executable
```bash
# Install cx_Freeze
pip install cx_Freeze

# Create executable
python setup_executable.py build

# Find the executable in: build/exe.win-amd64-3.x/
```

## Post-Installation

### Starting the Application

#### Windows:
- Double-click `start_koeka_pos_gui.bat` (silent start)
- Double-click `start_koeka_pos.bat` (with console)
- Use desktop shortcut (if created)
- Command line: `python app.py`

#### Linux/macOS:
- Run `./start_koeka_pos.sh`
- Use desktop shortcut (if created)  
- Command line: `python app.py`

### Default Login Credentials
- **Username:** `admin`
- **Password:** `admin123`

### File Structure After Installation
```
koeka-shop-pos/
├── app.py                    # Main application entry point
├── spaza_shop.db            # SQLite database
├── config.json              # Installation configuration
├── start_koeka_pos.*        # Platform-specific launchers
├── core/                    # Core application modules
├── modules/                 # Optional feature modules
└── utils/                   # Utility functions
```

## Troubleshooting

### Common Issues

1. **Python not found**
   - Install Python 3.8+ from python.org
   - Ensure Python is added to PATH

2. **Module import errors**
   - Run: `pip install -r requirements.txt`
   - Check Python version: `python --version`

3. **Database errors**
   - Delete `spaza_shop.db` and re-run installer
   - Check file permissions

4. **GUI not starting**
   - Install tkinter: `pip install tk` (Linux)
   - Check display settings (Linux/macOS)

### Getting Help

1. Check the main `README.md` file
2. Review the `INSTALLATION_GUIDE.md`
3. Check the `QUICK_START.md` guide
4. Review error messages in the console

## Development Installation

For developers who want to contribute:

```bash
# Clone the repository
git clone <repository-url>
cd koeka-shop-pos

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## Uninstallation

### Windows:
1. Delete installation directory
2. Remove shortcuts from Desktop and Start Menu
3. Remove from Programs list (if installed via .exe)

### Linux/macOS:
1. Delete installation directory
2. Remove shortcuts from Desktop
3. Remove any symlinks created

## Support

For technical support and bug reports, please refer to the project documentation or contact the development team.
