from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('scrapy_cookies')

hiddenimports = (
    collect_submodules('scrapy_cookies')
)