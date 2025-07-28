"""
Setup script for creating standalone executable using cx_Freeze
This creates a complete installer package with Python included
"""

import sys
from cx_Freeze import setup, Executable
import os

# Dependencies that need to be included
build_exe_options = {
    "packages": [
        "tkinter", "sqlite3", "datetime", "hashlib", "uuid", 
        "threading", "csv", "tempfile", "pathlib"
    ],
    "include_files": [
        ("core/", "core/"),
        ("modules/", "modules/"),
        ("config/", "config/"),
        ("utils/", "utils/"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md"),
        ("spaza_shop.db", "spaza_shop.db"),
    ],
    "excludes": ["test", "tests", "__pycache__"],
    "optimize": 2,
    "include_msvcrt": True,
}

# Base for Windows GUI application (no console window)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Create executable
executable = Executable(
    script="app.py",
    base=base,
    target_name="KoekaShopPOS.exe",
    icon="icon.ico",
    shortcut_name="Koeka Shop POS",
    shortcut_dir="DesktopFolder",
)

# Setup configuration
setup(
    name="Koeka Shop POS",
    version="1.0.0",
    description="Point of Sale System for Rural Spaza Shops",
    author="Tembie's Spaza Shop",
    options={"build_exe": build_exe_options},
    executables=[executable],
)

# Additional installer creation script
if __name__ == "__main__":
    print("Building Koeka Shop POS executable...")
    print("This will create a standalone executable with all dependencies included.")
    print("")
    print("After building, you can find the executable in the 'build' folder.")
    print("To create the installer, run: python setup.py build")
