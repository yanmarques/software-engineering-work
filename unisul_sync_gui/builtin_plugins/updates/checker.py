from . import setting
from ... import __version__ as app_version
from packaging.version import parse as parse_version
from scrapy.selector import Selector
from PyQt5 import QtCore
import requests
import distro

import os
import platform


GITHUB_REPO = 'https://github.com/yanmarques/software-engineering-work'
WINDOWS_ASSET = 'unisul-sync-gui_{}-1.zip'
DEBIAN_ASSET = 'unisul-sync-gui_{}-1_all.deb'
RPM_ASSET = 'unisul-sync-gui-{}-1.noarch.rpm'

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


def find_latest_version(version_selectors):
    use_unstable = setting.UseUnstableUpdatesSetting.get()

    def keep_version(release):
        '''
        Return whether to keep the specified version.

        It should always keep when using unstable releases,
        otherwise only when stable.
        '''

        if use_unstable:
            return True
        version = parse_version(release)
        return not (version.is_devrelease or version.is_prerelease)

    processed_versions = []

    # filter only versions to keep
    # also remove bad strings
    for version in version_selectors:
        _version = version.get().strip()
        if keep_version(_version):
            processed_versions.append(_version)
    
    # do we still have any versions?
    if not processed_versions:
        return

    # assign to the first version, just by now
    latest_version_index = 0
    latest_version = parse_version(processed_versions[0])

    for index, candidate in enumerate(processed_versions[1:]):
        version = parse_version(candidate)

        # maybe change our latest version
        if version > latest_version:
            latest_version_index = index
            latest_version = version
    
    return processed_versions[latest_version_index]


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


class AnyLatestVersionAvailable(Exception):
    def __init__(self, all_versions, message=None):
        if message is None:
            message = f'Unable to find a valid version from specified versions'
        super().__init__(message)
        self.all_versions = all_versions


class VersionsParseFailure(Exception):
    def __init__(self, response, message=None):
        if message is None:
            message = f'Could not find any version from upstream server'
        super().__init__(message)
        self.response = response


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
            raise VersionsParseFailure(response)

        upstream_version = find_latest_version(versions)
        
        if not upstream_version:
            raise AnyLatestVersionAvailable(versions)

        if parse_version(app_version) < parse_version(upstream_version):
            self.latest_version = upstream_version
            return True
        return False

    def build_downloader(self, filepath):
        url = self.build_download_url()
        return AssetDownloader(url, filepath)

    def build_download_url(self):
        assert self.latest_version, 'There is no latest version to download.'

        # remove leading "v" strings of "version"
        asset_version = self.latest_version.lstrip('v')
        asset_name = deduce_asset().format(asset_version)

        path = f'releases/download/{self.latest_version}/{asset_name}'
        return url(path)
        

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