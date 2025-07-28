# Koeka Shop POS Installation Script
# PowerShell version with enhanced features

param(
    [string]$InstallPath = $PSScriptRoot,
    [switch]$CreateShortcuts = $true,
    [switch]$CreateDemoData = $true
)

# Set console colors
$Host.UI.RawUI.BackgroundColor = "DarkBlue"
$Host.UI.RawUI.ForegroundColor = "White"
Clear-Host

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   KOEKA SHOP POS INSTALLATION WIZARD" -ForegroundColor Yellow  
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Welcome to the Koeka Shop Point of Sale System installer." -ForegroundColor Green
Write-Host "This script will guide you through the installation process." -ForegroundColor Green
Write-Host ""

# Function to write step headers
function Write-Step {
    param([string]$StepNumber, [string]$Description)
    Write-Host ""
    Write-Host "[$StepNumber] $Description..." -ForegroundColor Cyan
}

# Function to write success messages
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

# Function to write error messages
function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Function to write warning messages
function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

try {
    # Step 1: Check Python installation
    Write-Step "1/6" "Checking Python installation"
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python is installed: $pythonVersion"
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Error "Python is not installed or not in PATH"
        Write-Host ""
        Write-Host "Please install Python 3.8 or higher from: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Step 2: Check pip
    Write-Step "2/6" "Checking package installer (pip)"
    
    try {
        $pipVersion = python -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Pip is available: $pipVersion"
        } else {
            throw "Pip not found"
        }
    } catch {
        Write-Error "Pip is not available"
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Step 3: Install dependencies
    Write-Step "3/6" "Installing Python dependencies"
    
    if (Test-Path "requirements.txt") {
        Write-Host "Installing packages from requirements.txt..." -ForegroundColor White
        python -m pip install -r requirements.txt
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Dependencies installed successfully"
        } else {
            throw "Failed to install dependencies"
        }
    } else {
        Write-Warning "requirements.txt not found, skipping dependency installation"
    }

    # Step 4: Setup database
    Write-Step "4/6" "Setting up database"
    
    $dbSetup = python -c "from core.database.connection import get_db_manager; get_db_manager().initialize_schema(); print('Database initialized successfully')" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Database setup complete"
    } else {
        Write-Error "Database setup failed: $dbSetup"
        Read-Host "Press Enter to continue anyway"
    }

    # Step 5: Create demo data
    if ($CreateDemoData) {
        Write-Step "5/6" "Creating demo data"
        
        $demoSetup = python -c "from core.auth.authentication import ensure_demo_user; ensure_demo_user(); print('Demo user created')" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Demo data created"
        } else {
            Write-Warning "Could not create demo data: $demoSetup"
        }
    } else {
        Write-Step "5/6" "Skipping demo data creation"
    }

    # Step 6: Create shortcuts
    if ($CreateShortcuts) {
        Write-Step "6/6" "Creating shortcuts"
        
        try {
            # Create desktop shortcut
            $DesktopPath = [Environment]::GetFolderPath("Desktop")
            $ShortcutPath = Join-Path $DesktopPath "Koeka Shop POS.lnk"
            
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
            $Shortcut.TargetPath = "python"
            $Shortcut.Arguments = "`"$PSScriptRoot\app.py`""
            $Shortcut.WorkingDirectory = $PSScriptRoot
            $Shortcut.IconLocation = "$PSScriptRoot\icon.ico"
            $Shortcut.Description = "Koeka Shop Point of Sale System"
            $Shortcut.Save()
            
            # Create start menu shortcut
            $StartMenuPath = Join-Path ([Environment]::GetFolderPath("Programs")) "Koeka Shop"
            if (-not (Test-Path $StartMenuPath)) {
                New-Item -ItemType Directory -Path $StartMenuPath -Force | Out-Null
            }
            
            $StartMenuShortcut = Join-Path $StartMenuPath "Koeka Shop POS.lnk"
            $Shortcut2 = $WshShell.CreateShortcut($StartMenuShortcut)
            $Shortcut2.TargetPath = "python"
            $Shortcut2.Arguments = "`"$PSScriptRoot\app.py`""
            $Shortcut2.WorkingDirectory = $PSScriptRoot
            $Shortcut2.IconLocation = "$PSScriptRoot\icon.ico"
            $Shortcut2.Description = "Koeka Shop Point of Sale System"
            $Shortcut2.Save()
            
            Write-Success "Shortcuts created"
        } catch {
            Write-Warning "Could not create shortcuts: $($_.Exception.Message)"
        }
    } else {
        Write-Step "6/6" "Skipping shortcut creation"
    }

    # Installation complete
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "    INSTALLATION COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Koeka Shop POS has been successfully installed." -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start the application by:" -ForegroundColor White
    if ($CreateShortcuts) {
        Write-Host "  1. Double-clicking the desktop shortcut" -ForegroundColor White
        Write-Host "  2. Using the Start Menu shortcut" -ForegroundColor White
        Write-Host "  3. Running 'python app.py' in this folder" -ForegroundColor White
    } else {
        Write-Host "  • Running 'python app.py' in this folder" -ForegroundColor White
    }
    Write-Host ""
    if ($CreateDemoData) {
        Write-Host "Demo login credentials:" -ForegroundColor Yellow
        Write-Host "  Username: admin" -ForegroundColor Yellow
        Write-Host "  Password: admin123" -ForegroundColor Yellow
        Write-Host ""
    }
    Write-Host "For support, refer to the README.md file." -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "    INSTALLATION FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Error "Installation failed: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Please check the error message above and try again." -ForegroundColor Yellow
    Write-Host "For support, refer to the README.md file." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
