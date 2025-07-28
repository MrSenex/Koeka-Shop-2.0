@echo off
title Koeka Shop POS Installation Wizard
color 0A

echo.
echo ========================================
echo    KOEKA SHOP POS INSTALLATION WIZARD
echo ========================================
echo.
echo Welcome to the Koeka Shop Point of Sale System installer.
echo This wizard will guide you through the installation process.
echo.
pause

:check_python
echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Python is installed
    python --version
) else (
    echo ✗ Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:check_requirements
echo.
echo [2/5] Installing Python dependencies...
if exist requirements.txt (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% == 0 (
        echo ✓ Dependencies installed successfully
    ) else (
        echo ✗ Failed to install dependencies
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
) else (
    echo ✗ requirements.txt not found
    pause
    exit /b 1
)

:setup_database
echo.
echo [3/5] Setting up database...
python -c "from core.database.connection import get_db_manager; get_db_manager().initialize_schema(); print('Database initialized successfully')"
if %errorlevel% == 0 (
    echo ✓ Database setup complete
) else (
    echo ✗ Database setup failed
    pause
    exit /b 1
)

:create_shortcuts
echo.
echo [4/5] Creating desktop shortcuts...

:: Get current directory
set "CURRENT_DIR=%~dp0"

:: Create desktop shortcut for main app
echo Creating Koeka Shop POS shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Koeka Shop POS.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%CURRENT_DIR%app.py\"'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.IconLocation = '%CURRENT_DIR%icon.ico'; $Shortcut.Description = 'Koeka Shop Point of Sale System'; $Shortcut.Save()"

:: Create start menu shortcut
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Koeka Shop" mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Koeka Shop"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Koeka Shop\Koeka Shop POS.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%CURRENT_DIR%app.py\"'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.IconLocation = '%CURRENT_DIR%icon.ico'; $Shortcut.Description = 'Koeka Shop Point of Sale System'; $Shortcut.Save()"

echo ✓ Shortcuts created

:final_setup
echo.
echo [5/5] Final configuration...

echo Setting up demo user...
python -c "from core.auth.authentication import ensure_demo_user; ensure_demo_user(); print('Demo user created')"

echo.
echo ========================================
echo    INSTALLATION COMPLETE!
echo ========================================
echo.
echo Koeka Shop POS has been successfully installed.
echo.
echo You can now start the application by:
echo   1. Double-clicking the desktop shortcut
echo   2. Running 'python app.py' in this folder
echo   3. Using the Start Menu shortcut
echo.
echo Demo login credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo For support, refer to the README.md file.
echo.
pause
