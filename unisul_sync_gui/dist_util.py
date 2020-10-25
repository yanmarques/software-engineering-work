
import subprocess
import platform
import sys
import os


def list_files(path: str):
    with os.scandir(path) as scan:
        for entry in scan:
            if entry.is_file():
                yield entry.path
            else:
                yield from list_files(entry.path)


def list_icons():
    icons = []
    for icon in list_files('icons'):
        directory = os.path.dirname(icon)
        icons.append((os.path.join('share', directory), [icon]))
    return icons


def deduce_data_files():
    if platform.system() != 'Windows':
        return [('share/applications/', ['unisul-sync-gui.desktop']),
                ] + list_icons()

      
def deduce_install_requires():
    defaults = weak_requirements()

    excludes = [
        '--install-layout=deb',     # used by "install" in debian/rules
        'custom_deb',
    ]

    if not any(True for value in excludes if value in sys.argv):
        defaults.extend(hard_requirements())
    return defaults


def hard_requirements():
    return [
        'PyQt5', 
        'requests', 
        'scrapy', 
        'rarfile',
        'packaging',
    ]


def weak_requirements():
    return [
        'scrapy_cookies',
        'crochet'
    ]


def uninstall_weak_requirements():
    return pip_weak_requirements('uninstall', '-y')


def install_weak_requirements():
    return pip_weak_requirements('install')    


def pip_weak_requirements(*command):
    cmd = ['pip3'] + list(command) + weak_requirements()

    try:
        subprocess.run(cmd, 
                       check=True,
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as proc:
        error = proc.stderr.decode().strip()
        if error:
            print(error)
        return False