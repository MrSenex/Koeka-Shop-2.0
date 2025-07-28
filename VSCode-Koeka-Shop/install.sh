#!/bin/bash

echo "============================================================"
echo "   TEMBIE'S SPAZA SHOP POS SYSTEM - LINUX/MAC INSTALLER"
echo "============================================================"
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "  macOS: brew install python-tk"
    exit 1
fi

echo "Python found! Running setup..."
echo
python3 setup.py

echo
echo "Setup complete! You can now run:"
echo "  ./start_pos.sh   - To start the POS system"
echo "  or"
echo "  python3 app.py   - To start manually"
echo

# Make start script executable
chmod +x start_pos.sh
