!define APPNAME "OneShareInput"
!define COMPANY "OneShare"
!define VERSION "0.1.0"
!define EXE_NAME "OneShareInput.exe"

!include "MUI2.nsh"

Name "${APPNAME} ${VERSION}"
OutFile "OneShareInput-Setup-${VERSION}.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
RequestExecutionLevel user

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Spanish"

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "..\..\dist\OneShareInput\*.*"
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${EXE_NAME}"
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${EXE_NAME}"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APPNAME}.lnk"
  RMDir /r "$SMPROGRAMS\${APPNAME}"
  RMDir /r "$INSTDIR"
SectionEnd
