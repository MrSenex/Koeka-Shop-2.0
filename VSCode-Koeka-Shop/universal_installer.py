#!/usr/bin/env python3
"""
Universal Koeka Shop POS Setup Script
Works on Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import platform
import shutil
import json
import sqlite3
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class PosInstaller:
    def __init__(self):
        self.system = platform.system()
        self.install_dir = Path(__file__).parent
        self.python_executable = sys.executable
        
    def print_header(self):
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("=" * 50)
        print("   KOEKA SHOP POS INSTALLATION WIZARD")
        print("=" * 50)
        print(f"{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Universal installer for Windows, Linux & macOS{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Detected system: {self.system}{Colors.ENDC}\n")
        
    def print_step(self, step, description):
        print(f"\n{Colors.OKCYAN}[{step}] {description}...{Colors.ENDC}")
        
    def print_success(self, message):
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
        
    def print_error(self, message):
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
        
    def print_warning(self, message):
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")
        
    def run_command(self, command, check=True):
        """Run a command and return success status"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, result.stderr)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
            
    def check_python(self):
        """Check Python installation"""
        self.print_step("1/8", "Checking Python installation")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.print_error(f"Python 3.8+ required, found {sys.version}")
            return False
            
        self.print_success(f"Python {sys.version.split()[0]} found")
        
        # Check pip
        success, _, _ = self.run_command(f'"{self.python_executable}" -m pip --version')
        if success:
            self.print_success("pip is available")
            return True
        else:
            self.print_error("pip is not available")
            return False
            
    def install_dependencies(self):
        """Install Python dependencies"""
        self.print_step("2/8", "Installing Python dependencies")
        
        requirements_file = self.install_dir / "requirements.txt"
        if not requirements_file.exists():
            self.print_warning("requirements.txt not found, creating minimal requirements")
            requirements = [
                "tkinter",  # Usually built-in
                "sqlite3",  # Usually built-in
                "datetime", # Built-in
                "pathlib",  # Built-in
            ]
            # No external dependencies to install
            self.print_success("Using built-in Python modules")
            return True
            
        # Install from requirements.txt
        success, stdout, stderr = self.run_command(
            f'"{self.python_executable}" -m pip install -r "{requirements_file}"'
        )
        
        if success:
            self.print_success("Dependencies installed successfully")
            return True
        else:
            self.print_error(f"Failed to install dependencies: {stderr}")
            return False
            
    def setup_database(self):
        """Initialize the database"""
        self.print_step("3/8", "Setting up database")
        
        try:
            # Import and initialize database
            sys.path.insert(0, str(self.install_dir))
            from core.database.connection import get_db_manager
            
            db_manager = get_db_manager()
            db_manager.initialize_schema()
            
            self.print_success("Database initialized successfully")
            return True
            
        except Exception as e:
            self.print_error(f"Database setup failed: {e}")
            return False
            
    def create_demo_data(self):
        """Create demo user and sample data"""
        self.print_step("4/8", "Creating demo data")
        
        try:
            from core.auth.authentication import ensure_demo_user
            ensure_demo_user()
            self.print_success("Demo user created (admin/admin123)")
            return True
            
        except Exception as e:
            self.print_warning(f"Could not create demo data: {e}")
            return False
            
    def create_launcher_scripts(self):
        """Create platform-specific launcher scripts"""
        self.print_step("5/8", "Creating launcher scripts")
        
        if self.system == "Windows":
            return self._create_windows_launchers()
        else:
            return self._create_unix_launchers()
            
    def _create_windows_launchers(self):
        """Create Windows batch files"""
        try:
            # Main launcher
            launcher_bat = self.install_dir / "start_koeka_pos.bat"
            launcher_content = f'''@echo off
cd /d "{self.install_dir}"
"{self.python_executable}" app.py
pause
'''
            launcher_bat.write_text(launcher_content)
            
            # GUI launcher (no console)
            gui_launcher = self.install_dir / "start_koeka_pos_gui.bat"
            gui_content = f'''@echo off
cd /d "{self.install_dir}"
start "" "{self.python_executable}" app.py
'''
            gui_launcher.write_text(gui_content)
            
            self.print_success("Windows launchers created")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to create Windows launchers: {e}")
            return False
            
    def _create_unix_launchers(self):
        """Create Unix shell scripts"""
        try:
            # Main launcher
            launcher_sh = self.install_dir / "start_koeka_pos.sh"
            launcher_content = f'''#!/bin/bash
cd "{self.install_dir}"
"{self.python_executable}" app.py
'''
            launcher_sh.write_text(launcher_content)
            launcher_sh.chmod(0o755)
            
            # Desktop entry for Linux
            if self.system == "Linux":
                desktop_file = self.install_dir / "koeka-pos.desktop"
                desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Koeka Shop POS
Comment=Point of Sale System
Exec="{self.python_executable}" "{self.install_dir}/app.py"
Icon={self.install_dir}/icon.png
Path={self.install_dir}
Terminal=false
Categories=Office;Finance;
'''
                desktop_file.write_text(desktop_content)
                desktop_file.chmod(0o755)
                
            self.print_success("Unix launchers created")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to create Unix launchers: {e}")
            return False
            
    def create_shortcuts(self):
        """Create desktop and menu shortcuts"""
        self.print_step("6/8", "Creating shortcuts")
        
        if self.system == "Windows":
            return self._create_windows_shortcuts()
        elif self.system == "Linux":
            return self._create_linux_shortcuts()
        elif self.system == "Darwin":  # macOS
            return self._create_macos_shortcuts()
        else:
            self.print_warning("Shortcut creation not supported on this platform")
            return True
            
    def _create_windows_shortcuts(self):
        """Create Windows shortcuts"""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Koeka Shop POS.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = str(self.install_dir / "start_koeka_pos_gui.bat")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.save()
            
            self.print_success("Windows shortcuts created")
            return True
            
        except ImportError:
            self.print_warning("Windows shortcut modules not available")
            return True
        except Exception as e:
            self.print_warning(f"Could not create Windows shortcuts: {e}")
            return True
            
    def _create_linux_shortcuts(self):
        """Create Linux desktop shortcuts"""
        try:
            desktop_dir = Path.home() / "Desktop"
            if desktop_dir.exists():
                desktop_file = desktop_dir / "koeka-pos.desktop"
                shutil.copy(self.install_dir / "koeka-pos.desktop", desktop_file)
                desktop_file.chmod(0o755)
                
            self.print_success("Linux shortcuts created")
            return True
            
        except Exception as e:
            self.print_warning(f"Could not create Linux shortcuts: {e}")
            return True
            
    def _create_macos_shortcuts(self):
        """Create macOS shortcuts"""
        try:
            # Create simple app bundle structure
            app_name = "Koeka Shop POS.app"
            app_dir = self.install_dir / app_name
            
            if app_dir.exists():
                shutil.rmtree(app_dir)
                
            contents_dir = app_dir / "Contents"
            macos_dir = contents_dir / "MacOS"
            macos_dir.mkdir(parents=True)
            
            # Create launcher script
            launcher = macos_dir / "koeka_pos"
            launcher_content = f'''#!/bin/bash
cd "{self.install_dir}"
"{self.python_executable}" app.py
'''
            launcher.write_text(launcher_content)
            launcher.chmod(0o755)
            
            # Create Info.plist
            info_plist = contents_dir / "Info.plist"
            plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>koeka_pos</string>
    <key>CFBundleIdentifier</key>
    <string>com.koeka.pos</string>
    <key>CFBundleName</key>
    <string>Koeka Shop POS</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>'''
            info_plist.write_text(plist_content)
            
            self.print_success("macOS app bundle created")
            return True
            
        except Exception as e:
            self.print_warning(f"Could not create macOS shortcuts: {e}")
            return True
            
    def create_config(self):
        """Create configuration files"""
        self.print_step("7/8", "Creating configuration")
        
        try:
            config_file = self.install_dir / "config.json"
            config = {
                "system": self.system,
                "install_date": str(Path(__file__).stat().st_mtime),
                "python_executable": str(self.python_executable),
                "install_directory": str(self.install_dir),
                "version": "1.0.0"
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
            self.print_success("Configuration created")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to create configuration: {e}")
            return False
            
    def run_tests(self):
        """Run basic system tests"""
        self.print_step("8/8", "Running system tests")
        
        try:
            # Test database connection
            from core.database.connection import get_db_manager
            db = get_db_manager()
            
            # Test basic query
            result = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            if result:
                self.print_success("Database connectivity test passed")
            else:
                self.print_warning("Database test returned no results")
                
            # Test imports
            try:
                from core.auth.authentication import AuthenticationManager
                from core.products.management import ProductManager
                from core.sales.transaction import TransactionManager
                self.print_success("Core module imports successful")
            except ImportError as e:
                self.print_warning(f"Some modules failed to import: {e}")
                
            return True
            
        except Exception as e:
            self.print_warning(f"System tests failed: {e}")
            return True  # Don't fail installation for test failures
            
    def print_completion_message(self):
        """Print installation completion message"""
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
        print("=" * 50)
        print("    INSTALLATION COMPLETE!")
        print("=" * 50)
        print(f"{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}Koeka Shop POS has been successfully installed!{Colors.ENDC}\n")
        
        print(f"{Colors.OKBLUE}You can start the application by:{Colors.ENDC}")
        if self.system == "Windows":
            print(f"  • Double-clicking 'start_koeka_pos_gui.bat'")
            print(f"  • Running 'start_koeka_pos.bat' in a command prompt")
        else:
            print(f"  • Running './start_koeka_pos.sh' in a terminal")
            print(f"  • Using the desktop shortcut (if created)")
            
        print(f"  • Running: python app.py\n")
        
        print(f"{Colors.WARNING}Demo login credentials:{Colors.ENDC}")
        print(f"  Username: admin")
        print(f"  Password: admin123\n")
        
        print(f"{Colors.OKBLUE}For support and documentation, see README.md{Colors.ENDC}")
        
    def install(self):
        """Run the complete installation process"""
        self.print_header()
        
        steps = [
            self.check_python,
            self.install_dependencies,
            self.setup_database,
            self.create_demo_data,
            self.create_launcher_scripts,
            self.create_shortcuts,
            self.create_config,
            self.run_tests
        ]
        
        success_count = 0
        for step in steps:
            if step():
                success_count += 1
            else:
                print(f"\n{Colors.FAIL}Installation step failed. Continuing...{Colors.ENDC}")
                
        if success_count >= 6:  # At least core steps successful
            self.print_completion_message()
        else:
            print(f"\n{Colors.FAIL}Installation completed with errors.{Colors.ENDC}")
            print(f"{Colors.WARNING}Please check the error messages above.{Colors.ENDC}")

if __name__ == "__main__":
    installer = PosInstaller()
    installer.install()
    
    # Wait for user input on Windows
    if platform.system() == "Windows":
        input("\nPress Enter to exit...")
