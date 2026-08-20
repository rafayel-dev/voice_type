# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pyaudio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['scipy', 'numpy', 'matplotlib', 'sklearn', 'torch', 'onnxruntime', 'pandas', 'PySide6', 'PyQt6', 'PyQt5'],
    noarchive=False,
    optimize=0,
)
# Strip unused speech_recognition data (pocketsphinx models, non-Windows flac binaries)
a.datas = [
    d for d in a.datas
    if 'pocketsphinx-data' not in d[0]
    and not any(x in d[0] for x in ('flac-linux', 'flac-mac'))
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Voice Typer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
