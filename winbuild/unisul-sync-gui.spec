# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['.\\..\\unisul_sync_gui\\cli.py'],
             pathex=[],
             binaries=[],
             datas=[('.\\..\\unisul_sync_gui\\book_bot\\spiders\\*.py',
                     'unisul_sync_gui\\book_bot\\spiders')],
             hiddenimports=[],
             hookspath=['.\\winbuild\\hooks'],
             runtime_hooks=[],
             excludes=['hiredis', 'pymongo', 'tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='unisul-sync',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='eva.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='unisul-sync-gui')
