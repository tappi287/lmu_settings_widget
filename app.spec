# -*- mode: python ; coding: utf-8 -*-
from types import ModuleType

try:
    import pygame

    pygame_avail = 1
except ImportError:
    pygame_avail = 0

from PyInstaller.utils.hooks import get_package_paths

block_cipher = None
excluded_modules = ["cryptography"]

# ----- define app name
APP_NAME = "LMU-Settings-Widget"

# ----- locate eel.js
eel_js = get_package_paths("eel")[-1] + "\\eel.js"

# ----- App Icon
icon_file = "./vue/src/assets/app_icon.ico"


a = Analysis(
    ["scripts\\app.py"],
    pathex=[],
    binaries=[],
    datas=[
        # ("data/patched_eel_v0182.js", "eel/eel.js"),
        ("web", "web"),
        ("build/version.txt", "."),
        ("bin/PresentMonAPI2Loader.dll", "bin"),
        ("license.txt", "."),
        ("data", "data"),
    ],
    hiddenimports=["bottle_websocket", "ssl", "_ssl"],
    hookspath=["hooks"],
    runtime_hooks=[],
    excludes=excluded_modules,
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
    name=APP_NAME,
    icon=icon_file,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    upx_exclude=["_uuid.pyd", "vcruntime140.dll", "python.dll", "python3.dll", "python311.dll"],
    name=APP_NAME,
)
