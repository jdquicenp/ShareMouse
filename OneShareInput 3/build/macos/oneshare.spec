# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/icon.icns','app')],
    hiddenimports=['PySide6','pynput','pyautogui','pyperclip','screeninfo'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
app = BUNDLE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='OneShareInput.app',
    icon='app/icon.icns',
    bundle_identifier='com.oneshare.input',
    info_plist={'NSAppleEventsUsageDescription':'Necesario para controlar teclado y mouse',
                'NSMicrophoneUsageDescription':'No se usa microfono',
                'NSCameraUsageDescription':'No se usa camara'}
)
