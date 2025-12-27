# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for OPlus ROM Converter
Build with: pyinstaller OPlusRomConverter.spec
"""

import os
from pathlib import Path

block_cipher = None

# Get the directory containing this spec file
spec_dir = Path(SPECPATH)

# Data files to bundle
datas = [
    # Image assets for Zadig guide
    (str(spec_dir / 'assets'), 'assets'),
    
    # Zadig executable
    (str(spec_dir / 'zadig-2.9.exe'), '.'),
    
    # Kedacom Driver folder
    (str(spec_dir / 'DriverKedacomUSB'), 'DriverKedacomUSB'),
    
    # Tools (simg2img, lpmake)
    (str(spec_dir.parent / 'Tools' / 'simg2img.exe'), 'tools'),
    (str(spec_dir.parent / 'Tools' / 'lpmake.exe'), 'tools'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QFlashForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to reduce AV false positives
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(spec_dir / 'assets' / 'icon.ico'),  # App Icon
)
