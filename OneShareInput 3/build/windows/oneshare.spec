# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('app/icon.ico', 'app')],
    hiddenimports=['PySide6','pynput','pyautogui','pyperclip','screeninfo'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='OneShareInput',
    icon='app/icon.ico',
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    argv_emulation=False
)
