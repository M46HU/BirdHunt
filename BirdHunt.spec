# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.png', '.'), ('Analysis', 'Analysis'), ('GUI', 'GUI')],
    hiddenimports=['PIL._tkinter_finder', 'babel.numbers', 'tkintermapview', 'rasterio', 'rasterio.sample', 'fiona', 'shapely'],
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
    [],
    exclude_binaries=True,
    name='BirdHunt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Enable console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BirdHunt',
)
import sys

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='BirdHunt.app',
        icon=None,
        bundle_identifier=None,
    )
