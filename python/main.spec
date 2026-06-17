# -*- mode: python ; coding: utf-8 -*-

block_cipher=None

a = Analysis(
    ['main.py', 
    'backend/__init__.py', 'backend/database_manager.py', 'backend/models.py',
    'frontend/__init__.py', 'frontend/dialogs.py', 'frontend/main_window.py', 'frontend/styles.py', 'frontend/widgets.py',
    'utils/__init__.py', 'utils/logger.py',],
    pathex=['C:/Users/zmcmillan/projects/TroubleshootingNotes'],
    binaries=[],
    datas=[('P:/EMS_TR_PATH/Shared_notes/shard_notes.db', 'db/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data,
                    cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EMS Shared Notes',
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
