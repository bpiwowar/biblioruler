#!/usr/bin/env python

from distutils.core import setup

setup(name='biblioruler',
      version='0.1',
      description='API access to bibliographic managers',
      author='Benjamin Piwowarski',
      author_email='benjamin@bpiwowar.net',
      url='https://github.com/bpiwowar/biblioruler',
      install_requires = [
            "beautifulsoup4"
      ]
)
