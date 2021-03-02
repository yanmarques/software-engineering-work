
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


def find_icons_dirname():
    # windows pyinstaller? get frozen path
    if is_bundled():
        return cwd()

    module_dir = os.path.dirname(cwd())
    top_level_dir = os.path.dirname(module_dir)
    static_icons_dir = os.path.join(top_level_dir, 'icons')

    # dev mode? get icons from source code
    if os.path.exists(static_icons_dir) and \
       os.path.isdir(static_icons_dir):
        return top_level_dir

    # otherwise linux default icons path
    return '/usr/share/'


def is_bundled():
    '''
    Return whether the app is bundled.

    @see https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    '''

    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def cwd():
    if is_bundled():
        # @see https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
        target_dir = sys._MEIPASS
    else:
        target_dir = __file__

    return os.path.abspath(os.path.realpath(target_dir))


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
        'distro',
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


def pip_weak_requirements(*command, on_error=None):
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
            # set print as default callback
            if on_error is None:
                on_error = print

            # handle error with callback
            on_error(error)

        return False