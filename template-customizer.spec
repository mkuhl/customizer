# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Template Customizer
Builds a standalone native executable for Linux
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, 'src')

a = Analysis(
    ['src/template_customizer/__main__.py'],
    pathex=['src'],
    binaries=[],
    datas=[],  # No data files needed - all code is bundled
    hiddenimports=[
        'click',
        'click.core',
        'click.decorators',
        'click.exceptions',
        'click.formatting',
        'click.parser',
        'click.termui',
        'click.types',
        'click.utils',
        'rich',
        'rich.console',
        'rich.panel',
        'rich.progress',
        'rich.table',
        'rich.text',
        'rich.syntax',
        'rich.traceback',
        'jinja2',
        'jinja2.ext',
        'yaml',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
        'sqlite3',
        'test',
        'tests',
        'unittest',
        'xml',
        'xmlrpc',
        'email',
        'distutils',
        'setuptools',
        'pip',
        'pkg_resources',
    ],
    noarchive=False,
    optimize=1,  # Optimize bytecode (level 1 preserves docstrings)
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='customizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols for smaller size
    upx=False,   # UPX disabled - minimal benefit, adds complexity
    runtime_tmpdir=None,
    console=True,  # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # No icon for Linux
)