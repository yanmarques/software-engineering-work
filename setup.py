#!/usr/bin/env python

from setuptools import setup, find_packages

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
      install_requires=[
          'PyQt5',
          'scrapy',
          'scrapy_cookies',
          'requests',
          'crochet',
          'rarfile'
      ],
      python_requires='>=3',
      data_files=deduce_data_files()
     )