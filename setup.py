#!/usr/bin/env python

from setuptools import setup, find_packages

import sys

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
          'console_scripts': ['unisul-sync-gui=unisul_sync_gui.cli:entrypoint']
      },
      install_requires=[
          'PyQt5',
          'scrapy',
          'scrapy_cookies',
          'requests'
      ],
      python_requires='>=3'
     )