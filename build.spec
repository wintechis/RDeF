# -*- mode: python ; coding: utf-8 -*-
# run "python -m PyInstaller build.spec"
from kivy_deps import sdl2, glew


block_cipher = None

base = '.'
add_files = [
    (base + '')
]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=None,
    datas=None,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['*.dist-info'],
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
    name='RDeF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='resources/rdef_48x48.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

ex = [  '.git',
        '.gitignore',
        '.github',
        'docs',
        'env',
        'icon',
        'mods',
        'example.jpg',
        '*.log',
        'LICENSE',
        'README.md',
        '__pycache__',
        '*.dist-info',
        '.pre-commit-config.yaml'
    ]


coll = COLLECT(
    exe,
    Tree('.', excludes=ex,),
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='data',
)
