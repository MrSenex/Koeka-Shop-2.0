@echo off
echo ============================================================
echo   TEMBIE'S SPAZA SHOP POS SYSTEM - WINDOWS INSTALLER
echo ============================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found! Running setup...
echo.
python setup.py

echo.
echo Setup complete! You can now run:
echo   start_pos.bat   - To start the POS system
echo   or
echo   python app.py   - To start manually
echo.
pause
