# Koeka Shop POS NSIS Installer Script
# This creates a professional Windows installer (.exe)

!define APPNAME "Koeka Shop POS"
!define COMPANYNAME "Tembie's Spaza Shop"
!define DESCRIPTION "Point of Sale System for Rural Spaza Shops"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

# Define installer properties
Name "${APPNAME}"
Icon "icon.ico"
OutFile "KoekaShopPOS_Setup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
RequestExecutionLevel admin

# Include modern UI
!include "MUI2.nsh"

# Define pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

# Set languages
!insertmacro MUI_LANGUAGE "English"

# Default section
Section "Core Application" SecCore
    SectionIn RO  # Required section
    
    SetOutPath $INSTDIR
    
    # Copy application files
    File /r "*.*"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    # Registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                     "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                     "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                     "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                     "DisplayIcon" "$INSTDIR\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                     "Publisher" "${COMPANYNAME}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                       "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                       "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                       "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
                       "NoRepair" 1
SectionEnd

# Optional shortcuts section
Section "Desktop Shortcut" SecDesktop
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" \
                   "python" \
                   '"$INSTDIR\app.py"' \
                   "$INSTDIR\icon.ico" \
                   0 \
                   SW_SHOWNORMAL \
                   "" \
                   "Koeka Shop Point of Sale System"
SectionEnd

# Optional start menu section
Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" \
                   "python" \
                   '"$INSTDIR\app.py"' \
                   "$INSTDIR\icon.ico" \
                   0 \
                   SW_SHOWNORMAL \
                   "" \
                   "Koeka Shop Point of Sale System"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" \
                   "$INSTDIR\uninstall.exe"
SectionEnd

# Python dependencies section
Section "Install Python Dependencies" SecDeps
    DetailPrint "Installing Python dependencies..."
    ExecWait 'python -m pip install -r "$INSTDIR\requirements.txt"' $0
    ${If} $0 != 0
        MessageBox MB_OK "Failed to install Python dependencies. Please install them manually."
    ${EndIf}
SectionEnd

# Database setup section
Section "Initialize Database" SecDB
    DetailPrint "Setting up database..."
    ExecWait 'python -c "from core.database.connection import get_db_manager; get_db_manager().initialize_schema()"' $0
    ${If} $0 != 0
        MessageBox MB_OK "Failed to initialize database. Please run setup manually."
    ${EndIf}
SectionEnd

# Section descriptions
LangString DESC_SecCore ${LANG_ENGLISH} "Core application files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Create a desktop shortcut"
LangString DESC_SecStartMenu ${LANG_ENGLISH} "Create start menu shortcuts"
LangString DESC_SecDeps ${LANG_ENGLISH} "Install Python dependencies automatically"
LangString DESC_SecDB ${LANG_ENGLISH} "Initialize the application database"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
!insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
!insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} $(DESC_SecStartMenu)
!insertmacro MUI_DESCRIPTION_TEXT ${SecDeps} $(DESC_SecDeps)
!insertmacro MUI_DESCRIPTION_TEXT ${SecDB} $(DESC_SecDB)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

# Uninstaller section
Section "Uninstall"
    # Remove files
    RMDir /r "$INSTDIR"
    
    # Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APPNAME}"
    
    # Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd

# Functions
Function .onInit
    # Check if Python is installed
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.8\InstallPath" ""
    ${If} $0 == ""
        ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.9\InstallPath" ""
    ${EndIf}
    ${If} $0 == ""
        ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.10\InstallPath" ""
    ${EndIf}
    ${If} $0 == ""
        ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.11\InstallPath" ""
    ${EndIf}
    ${If} $0 == ""
        MessageBox MB_YESNO "Python 3.8+ is required but not found. Do you want to continue anyway?" IDYES +2
        Abort
    ${EndIf}
FunctionEnd
