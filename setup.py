#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="biblioruler",
    version="0.1.0",
    description="API access to bibliographic managers",
    author="Benjamin Piwowarski",
    author_email="benjamin@bpiwowar.net",
    url="https://github.com/bpiwowar/biblioruler",
    packages=find_packages(),
    install_requires=["beautifulsoup4", "sqlalchemy"],
    setup_requires=["setuptools >=30.3", "setuptools_scm"],
)
