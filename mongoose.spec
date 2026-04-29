# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Mongoose
# Works on both Windows and Linux.
# Usage: pyinstaller mongoose.spec --clean

import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect ALL PyQt6 files (binaries, data, hidden imports)
qt_datas, qt_binaries, qt_hiddenimports = collect_all('PyQt6')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=qt_binaries,
    datas=[
        ('static/icons/*.svg', 'static/icons'),
    ] + qt_datas,
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtSvg',
        'PyQt6.sip',
        'numpy',
        'typing_extensions',
    ] + qt_hiddenimports,
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
    a.datas,
    [],
    name='Mongoose',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # Set to True so you can see errors; change to False for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
