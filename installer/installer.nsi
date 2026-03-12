; WatchDog Installer Script
; This script creates a professional Windows installer for WatchDog

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"

; General Configuration
Name "WatchDog"
OutFile "WatchDog_Installer.exe"
Unicode True
InstallDir "$PROGRAMFILES\WatchDog"
InstallDirRegKey HKCU "Software\WatchDog" ""
RequestExecutionLevel admin

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "wizard.bmp"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
Page custom ConfigPage ConfigPageLeave
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Version Information
VIProductVersion "1.2.0.0"
VIAddVersionKey "ProductName" "WatchDog"
VIAddVersionKey "CompanyName" "WatchDog Team"
VIAddVersionKey "FileVersion" "1.2.0.0"
VIAddVersionKey "ProductVersion" "1.2.0.0"
VIAddVersionKey "FileDescription" "System Intelligence Framework"

; Global Variables
Var ConfigDialog
Var GitHubTokenField
Var AnthropicKeyField
Var AutoUpdateField
Var StartMenuFolder

; Configuration Page
Function ConfigPage
    !insertmacro MUI_HEADER_TEXT "Configuration" "Configure WatchDog settings"

    nsDialogs::Create 1018
    Pop $ConfigDialog

    ${If} $ConfigDialog == error
        Abort
    ${EndIf}

    ${NSD_CreateLabel} 0 0 100% 12u "GitHub Token (for updates):"
    Pop $0

    ${NSD_CreateText} 0 13u 100% 12u ""
    Pop $GitHubTokenField
    ${NSD_SetText} $GitHubTokenField ""

    ${NSD_CreateLabel} 0 30u 100% 12u "Anthropic API Key (for AI features):"
    Pop $0

    ${NSD_CreatePassword} 0 43u 100% 12u ""
    Pop $AnthropicKeyField
    ${NSD_SetText} $AnthropicKeyField ""

    ${NSD_CreateCheckBox} 0 60u 100% 12u "Enable automatic updates"
    Pop $AutoUpdateField
    ${NSD_Check} $AutoUpdateField

    nsDialogs::Show
FunctionEnd

Function ConfigPageLeave
    ${NSD_GetText} $GitHubTokenField $0
    ${NSD_GetText} $AnthropicKeyField $1
    ${NSD_GetState} $AutoUpdateField $2

    ; Store values temporarily
    WriteRegStr HKCU "Software\WatchDog\Temp" "GitHubToken" $0
    WriteRegStr HKCU "Software\WatchDog\Temp" "AnthropicKey" $1
    WriteRegDWORD HKCU "Software\WatchDog\Temp" "AutoUpdate" $2
FunctionEnd

; Encrypt and store sensitive data
Function StoreSecureConfig
    ; Read temporary values
    ReadRegStr $0 HKCU "Software\WatchDog\Temp" "GitHubToken"
    ReadRegStr $1 HKCU "Software\WatchDog\Temp" "AnthropicKey"
    ReadRegDWORD $2 HKCU "Software\WatchDog\Temp" "AutoUpdate"

    ; Encrypt and store in registry (using simple obfuscation)
    ; In production, use proper encryption like DPAPI
    StrCpy $3 $0
    Call EncryptString
    WriteRegStr HKCU "Software\WatchDog\Config" "GitHubToken" $3

    StrCpy $3 $1
    Call EncryptString
    WriteRegStr HKCU "Software\WatchDog\Config" "AnthropicKey" $3

    WriteRegDWORD HKCU "Software\WatchDog\Config" "AutoUpdate" $2

    ; Clean up temp values
    DeleteRegKey HKCU "Software\WatchDog\Temp"
FunctionEnd

; Simple string encryption (XOR with key)
Function EncryptString
    Exch $3
    Push $4
    Push $5
    Push $6

    StrCpy $4 "WatchDogSecureKey2024" ; Encryption key
    StrCpy $5 0
    StrCpy $6 ""

    loop:
        StrCpy $7 $3 1 $5
        StrCmp $7 "" done

        StrCpy $8 $4 1 $5
        StrCmp $8 "" 0 +2
        StrCpy $8 $4 1 0 ; Wrap around key

        ; XOR operation
        IntOp $7 $7 ^ $8

        StrCpy $6 "$6$7"
        IntOp $5 $5 + 1
        Goto loop

    done:
    StrCpy $3 $6
    Pop $6
    Pop $5
    Pop $4
    Exch $3
FunctionEnd

; Decrypt string (same as encrypt for XOR)
Function DecryptString
    Call EncryptString
FunctionEnd

; Installer Sections
Section "WatchDog Core" SecCore
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Copy main executable
    File "WatchDog.exe"

    ; Copy required files
    File "settings.json"
    File "LICENSE"
    File "README.md"

    ; Create data directories
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\data\logs"
    CreateDirectory "$INSTDIR\data\cache"

    ; Store secure configuration
    Call StoreSecureConfig

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Registry entries
    WriteRegStr HKCU "Software\WatchDog" "" $INSTDIR
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog" "DisplayName" "WatchDog"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog" "DisplayVersion" "1.2.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog" "Publisher" "WatchDog Team"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog" "NoRepair" 1
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog" "DisplayIcon" "$INSTDIR\WatchDog.exe"

SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\WatchDog.lnk" "$INSTDIR\WatchDog.exe" "" "$INSTDIR\WatchDog.exe" 0
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall WatchDog.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\WatchDog.lnk" "$INSTDIR\WatchDog.exe" "" "$INSTDIR\WatchDog.exe" 0
SectionEnd

; Section Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Installs the core WatchDog application and required files."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Creates Start Menu shortcuts for easy access."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Creates a desktop shortcut for quick launching."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller Section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\WatchDog.exe"
    Delete "$INSTDIR\settings.json"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\Uninstall.exe"

    ; Remove directories
    RMDir /r "$INSTDIR\data"
    RMDir "$INSTDIR"

    ; Remove shortcuts
    Delete "$SMPROGRAMS\$StartMenuFolder\WatchDog.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall WatchDog.lnk"
    RMDir "$SMPROGRAMS\$StartMenuFolder"
    Delete "$DESKTOP\WatchDog.lnk"

    ; Remove registry entries
    DeleteRegKey HKCU "Software\WatchDog"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WatchDog"

    ; Remove secure config
    DeleteRegKey HKCU "Software\WatchDog\Config"
SectionEnd

; Initialization
Function .onInit
    ; Check Windows version
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK "WatchDog requires Windows 10 or later."
        Abort
    ${EndIf}

    ; Check if already installed
    ReadRegStr $R0 HKCU "Software\WatchDog" ""
    ${If} $R0 != ""
        MessageBox MB_YESNO "WatchDog is already installed. Do you want to reinstall?" IDYES continue
        Abort
        continue:
    ${EndIf}

    ; Set default start menu folder
    StrCpy $StartMenuFolder "WatchDog"
FunctionEnd

; Success message
Function .onInstSuccess
    MessageBox MB_OK "WatchDog has been successfully installed!"
FunctionEnd