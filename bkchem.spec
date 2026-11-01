# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for BKChem - build from the project root with:

    pyinstaller bkchem.spec

The result is dist/BKChem/BKChem.exe (a one-folder build).

Notes on the choices below:
* console=True on purpose for the first builds: BKChem reports
  startup errors as tracebacks, and with a windowed build you would
  see exactly the "exe starts, no window, no message" symptom.
  Once the one-folder build runs fine, set console=False for the
  final build (and only then consider onefile - one-folder is much
  easier to debug and starts faster).
* Pmw must be collected completely (collect_all): Pmw loads its
  widget library lazily from the .py files inside the Pmw package
  directory at runtime, so the usual static import analysis is not
  enough and a naive build fails silently inside Pmw.
* The datas list mirrors how bkchem/os_support.py looks resources
  up at runtime, relative to the bkchem package directory:
  bkchem/pixmaps, bkchem/templates and bkchem/images inside the
  package, plus ../images, ../plugins and ../locale next to it.
* win32clipboard / win32con are imported lazily inside
  paper.selected_to_real_clipboard_as_SVG() and
  selected_to_real_clipboard_as_image(), so static analysis does
  not see them - they are listed as hidden imports (pywin32 must
  be installed in the build environment).
"""

from PyInstaller.utils.hooks import collect_all

pmw_datas, pmw_binaries, pmw_hiddenimports = collect_all('Pmw')

datas = [
    ('bkchem/pixmaps', 'bkchem/pixmaps'),
    ('bkchem/templates', 'bkchem/templates'),
    ('bkchem/images', 'bkchem/images'),
    ('images', 'images'),
    ('plugins', 'plugins'),
    ('locale', 'locale'),
] + pmw_datas

hiddenimports = [
    'win32clipboard',
    'win32con',
] + pmw_hiddenimports


a = Analysis(
    ['run_bkchem.py'],
    pathex=[],
    binaries=pmw_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BKChem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='BKChem',
)
