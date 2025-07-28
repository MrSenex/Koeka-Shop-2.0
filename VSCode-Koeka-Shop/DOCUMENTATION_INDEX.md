# Koeka Shop POS - Documentation Index

**Quick access to all installation and setup documentation**

---

## Installation & Setup

| Document | Purpose | Audience |
|----------|---------|----------|
| **[MASTER_INSTALLATION_GUIDE.md](MASTER_INSTALLATION_GUIDE.md)** | Complete installation options guide | **Everyone** |
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | Technical installation details | Developers |
| [INSTALLATION_OPTIONS.md](INSTALLATION_OPTIONS.md) | Alternative installation methods | Advanced users |
| [QUICK_START.md](QUICK_START.md) | Fast getting started guide | New users |

---

## Installation Files

| File | Type | Platform | Description |
|------|------|----------|-------------|
| `install_wizard.ps1` | PowerShell | Windows | **Recommended Windows installer** |
| `universal_installer.py` | Python | All | **Recommended cross-platform installer** |
| `install_wizard.py` | Python GUI | All | Graphical installation wizard |
| `installer.nsi` | NSIS Script | Windows | Professional .exe installer source |
| `setup_executable.py` | cx_Freeze | All | Standalone executable builder |
| `install.bat` | Batch | Windows | Basic automated installer |
| `install.sh` | Shell | Linux/macOS | Basic automated installer |

---

## Core Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview and quick start |
| [functional_specification_complete.md](functional_specification_complete.md) | Complete system requirements |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Development progress summary |
| [SMS_FUNCTIONALITY_GUIDE.md](SMS_FUNCTIONALITY_GUIDE.md) | SMS integration guide |

---

## Quick Start Commands

### Windows (Recommended):
```powershell
.\install_wizard.ps1
```

### All Platforms (Recommended):
```bash
python universal_installer.py
```

### Manual Installation:
```bash
pip install -r requirements.txt
python app.py
```

### Login Credentials:
- **Username:** `admin`
- **Password:** `admin123`

---

## Development Files

| File | Purpose |
|------|---------|
| `app.py` | Main application entry point |
| `main.py` | Alternative launcher |
| `gui.py` | GUI interface |
| `sales_gui.py` | Sales interface |
| `demo_cli.py` | Command-line demo |

---

## Testing Files

| File | Purpose |
|------|---------|
| `test_core_functionality.py` | Core system tests |
| `test_authentication.py` | Authentication tests |
| `test_cash_management.py` | Cash management tests |
| `test_gui_interfaces.py` | GUI interface tests |
| `test_sms_integration.py` | SMS functionality tests |

---

## Recommended Reading Order

### For New Users:
1. [MASTER_INSTALLATION_GUIDE.md](MASTER_INSTALLATION_GUIDE.md) - Start here!
2. [QUICK_START.md](QUICK_START.md) - Learn the basics
3. [README.md](README.md) - Understand the system

### For Developers:
1. [functional_specification_complete.md](functional_specification_complete.md) - Requirements
2. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Current status
3. [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Technical details

### For System Administrators:
1. [MASTER_INSTALLATION_GUIDE.md](MASTER_INSTALLATION_GUIDE.md) - Installation options
2. [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - Technical setup
3. [SMS_FUNCTIONALITY_GUIDE.md](SMS_FUNCTIONALITY_GUIDE.md) - SMS configuration

---

## Need Help?

1. **Start here:** [MASTER_INSTALLATION_GUIDE.md](MASTER_INSTALLATION_GUIDE.md)
2. **Common issues:** Check troubleshooting sections in installation guides
3. **Technical details:** Review individual documentation files
4. **Testing:** Run the test files to verify functionality

---

**Welcome to Koeka Shop POS!**
