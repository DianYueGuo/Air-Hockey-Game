# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(__file__).resolve().parents[2]

block_cipher = None


assets = project_root / "assets"


analysis = Analysis(
    [str(project_root / "src" / "air_hockey" / "main.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=[(str(assets), "assets")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(analysis.pure, analysis.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.zipfiles,
    analysis.datas,
    [],
    name="AirHockey",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=str(assets / "icons" / "app.ico"),
)
