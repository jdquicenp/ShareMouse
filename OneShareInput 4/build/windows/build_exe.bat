@echo off
setlocal
REM Build Windows executable with PyInstaller
pip install -r ..\..\requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --clean build\windows\oneshare.spec
echo.
echo Build finished. EXE in dist\OneShareInput\OneShareInput.exe
