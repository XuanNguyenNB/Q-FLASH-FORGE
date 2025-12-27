# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for OPlus ROM Converter
Build with: pyinstaller build.spec
"""

import os
from pathlib import Path

block_cipher = None

# Get paths
spec_dir = Path(SPECPATH)
tools_dir = spec_dir.parent / 'Tools'

# Data files to bundle
datas = [
    # Bundle tools
    (str(tools_dir / 'simg2img.exe'), 'tools'),
    (str(tools_dir / 'lpmake.exe'), 'tools'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name='OPlusRomConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
