#!/usr/bin/env bash
set -euo pipefail
# Build macOS .app with PyInstaller
python3 -m pip install -r ../../requirements.txt
python3 -m pip install pyinstaller
pyinstaller --noconfirm --clean build/macos/oneshare.spec
echo "App en dist/OneShareInput.app"
