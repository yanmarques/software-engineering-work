#!/usr/bin/env python

from unisul_sync_gui.dist_util import (
    deduce_data_files,
    deduce_install_requires
)
from setuptools import setup, find_packages

import shutil
import sys
import os

HAS_STDEB = True
try:
    from stdeb.command import (
        bdist_deb, 
        sdist_dsc,
        debianize,
    )
    from stdeb import util
except ImportError:
    HAS_STDEB = False


def deduce_cmdclass():
    cmdclass = {}

    if HAS_STDEB:
        cmdclass.update(custom_deb=CustomDeb,
                        sdist_dsc=sdist_dsc.sdist_dsc)
    return cmdclass


if HAS_STDEB:
    class CustomDeb(bdist_deb.bdist_deb):
        def run(self):
            old_fn = util.process_command

            def wrapper(cmd, cwd=None):
                if cmd[0] == 'dpkg-buildpackage':
                    # make our customizations
                    self.announce('Customizing "debian" source directory...')

                    target_dir = os.path.join(cwd, 'debian')

                    # clean it up
                    shutil.rmtree(target_dir)

                    # put our debian
                    self.copy_tree('debian', target_dir)

                # actually run command
                old_fn(cmd, cwd=cwd)

            # hacky solution to customize build
            sys.modules['stdeb'].util.process_command = wrapper

            super().run() 


setup(name='unisul-sync-gui',
      version='0.0.1',
      license='BSD (3 clause)',
      description='Synchronyze books from EVA system easily',
      author='Yan Marques de Cerqueira',
      author_email='marques_yan@outlook.com',
      url='https://github.com/yanmarques/software-engineering-work/',
      download_url='https://github.com/yanmarques/software-engineering-work/releases/download/v0.0.1/unisul-sync-gui-0.0.1.tar.gz',
      classifiers=[
          'Intended Audience :: End Users/Desktop',
          'Topic :: Education',
      ],
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': ['unisul-sync-gui=cli:entrypoint']
      },
      install_requires=deduce_install_requires(),
      python_requires='>=3',
      data_files=deduce_data_files(),
      cmdclass=deduce_cmdclass()
     )
