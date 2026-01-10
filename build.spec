# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('gui/icon', 'icon')],  # 将 gui/icon 文件夹复制到打包包的 root/icon
    hiddenimports=['dotenv'],
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
    name='ModelScope_Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=True, # macOS: 允许 argv 传递
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui/icon/AppIcon.icns' if 'darwin' in __import__('sys').platform else None # 如果有应用图标，可以在这里指定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ModelScope_Manager',
)

app = BUNDLE(
    coll,
    name='ModelScope_Manager.app',
    icon=None,
    bundle_identifier='com.yourname.modelscope-manager',
)
