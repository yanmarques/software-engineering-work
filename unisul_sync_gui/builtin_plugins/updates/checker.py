from . import setting
from ... import __version__ as app_version
from packaging.version import parse as parse_version
from scrapy.selector import Selector
from PyQt5 import QtCore
import requests

import os
import platform
import distro


GITHUB_REPO = 'https://github.com/yanmarques/software-engineering-work'
WINDOWS_ASSET = 'unisul-sync-gui_0.0.1-1.zip'
DEBIAN_ASSET = 'unisul-sync-gui_0.0.1-1_all.deb'
RPM_ASSET = 'unisul-sync-gui-0.0.1-1.noarch.rpm'

LINUX_DISTS = {
    DEBIAN_ASSET: [
        'debian',
        'ubuntu',
        'linuxmint',
    ],
    RPM_ASSET: [
        'rhel',
        'centos',
        'fedora',
        'opensuse',
        'gentoo',
    ]
}


def url(path):
    return f'{GITHUB_REPO}/{path}'


def deduce_asset():
    if platform.system() == 'Windows':
        return WINDOWS_ASSET

    if platform.system() != 'Linux':
        raise UnavailableOperatingSystem()
    
    distribution = distro.id()
    for asset, dists in LINUX_DISTS.items():
        if distribution in dists:
            return asset
    
    raise UnavailableLinuxDistribution()


class UnavailableLinuxDistribution(Exception):
    def __init__(self, message=None):
        if message is None:
            message = f'Unable to manage the linux distribution: {distro.id()}'
        super().__init__(message)


class UnavailableOperatingSystem(Exception):
    def __init__(self, message=None):
        if message is None:
            message = f'Unable to manage the underlying operating system: {platform.system()}'
        super().__init__(message)


class UpdateChecker:
    def __init__(self):
        self.latest_version = None

    def check(self):
        path = '/refs-tags/master?source_action=disambiguate&source_controller=files&tag_name=master&q='
        response = requests.get(url(path))
        return self.check_response(response)
    
    def check_response(self, response):
        content = response.text
        versions = Selector(text=content).xpath('//div/a/span/text()')

        if not versions:
            return None

        upstream_version = self.find_latest_version(versions)

        if parse_version(app_version) < parse_version(upstream_version):
            self.latest_version = upstream_version
            return True
        return False

    def build_downloader(self, filepath):
        url = self.build_download_url()
        return AssetDownloader(url, filepath)

    def build_download_url(self):
        assert self.latest_version, 'There is no latest version to download.'
        # asset_name = deduce_asset()
        asset_name = WINDOWS_ASSET
        path = f'releases/download/{self.latest_version}/{asset_name}'
        return url(path)

    def find_latest_version(self, version_selectors):
        # remove bad chars
        processed_versions = [version.get().strip()
                              for version in version_selectors]

        use_unstable = setting.UseUnstableUpdatesSetting.get()

        # set the first version as latest, just by now
        latest_version_str = processed_versions[0]
        latest_version = parse_version(latest_version_str)

        for candidate in processed_versions[1:]:
            version = parse_version(candidate)

            # skip unstable releases when not using it
            if not use_unstable and (version.is_devrelease or \
                                     version.is_prerelease):
                continue

            # change our latest version
            if version > latest_version:
                latest_version_str = candidate
                latest_version = version
        
        return latest_version_str
        

class AssetDownloader(QtCore.QThread):
    got_response = QtCore.pyqtSignal(int)
    chunk_wrote = QtCore.pyqtSignal(int)
    done = QtCore.pyqtSignal()

    def __init__(self, url, filepath):
        super().__init__()
        self.url = url
        self.filepath = filepath
        self.chunk_size = 8192

    def run(self):
        with requests.get(self.url, stream=True) as res:
            res.raise_for_status()
            size = res.headers.get('content-length')
            if size is not None:
                size = int(size)
            self.got_response.emit(size)

            with open(self.filepath, mode='wb') as writer:
                self._iter_content(res, writer)
        self.done.emit()

    def _iter_content(self, response, writer):
        for chunk in response.iter_content(chunk_size=self.chunk_size):
            chunk_rcv = writer.write(chunk)
            self.chunk_wrote.emit(chunk_rcv)