from PyInstaller.utils.hooks import collect_data_files, collect_submodules

hiddenimports = (
    collect_submodules('unisul_sync_gui') +
    collect_submodules('unisul_sync_gui.book_bot')
)