from ... import signals, __version__ as app_version
from packaging.version import parse as parse_version
from scrapy.selector import Selector
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

        upstream_version = versions[0].get().strip()

        if parse_version(upstream_version) > parse_version(app_version):
            self.latest_version = upstream_version
            return True
        return False

    def build_downloader(self, dst_path):
        assert self.latest_version, 'There is no latest version to download.'
        asset_name = deduce_asset()
        path = f'releases/download/{self.latest_version}/{asset_name}'
        return AssetDownloader(url(path), asset_name, dst_path)
        

class AssetDownloader:
    got_response = signals.pysignal()
    chunk_wrote = signals.pysignal()
    done = signals.pysignal()

    def __init__(self, url, asset_name, filepath):
        self.url = url
        self.asset_name = asset_name
        self.filepath = filepath
        self.chunk_size = 8192

    def download(self):
        with requests.get(self.url, stream=True) as res:
            res.raise_for_status()
            size = res.headers.get('content-length')
            if size is not None:
                size = int(size)
            self.got_response.emit(size=size)

            with open(self.filepath, mode='wb') as writer:
                for chunk in res.iter_content(chunk_size=self.chunk_size):
                    writer.write(chunk)
                    self.chunk_wrote.emit()
        self.done.emit()