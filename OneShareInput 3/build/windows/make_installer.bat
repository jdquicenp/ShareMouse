@echo off
REM Create Windows installer with NSIS (requires makensis in PATH)
if not exist "..\..\dist\OneShareInput\OneShareInput.exe" (
  echo EXE not found. Run build_exe.bat first.
  exit /b 1
)
makensis build\windows\installer.nsi
echo Installer ready: OneShareInput-Setup-0.1.0.exe
