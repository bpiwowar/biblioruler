#!/usr/bin/env python

from setuptools import setup

setup(
    name="biblioruler",
    description="API access to bibliographic managers",
    author="Benjamin Piwowarski",
    author_email="benjamin@bpiwowar.net",
    url="https://github.com/bpiwowar/biblioruler",
    install_requires=["beautifulsoup4", "sqlalchemy"],
    setup_requires=["setuptools >=30.3", "setuptools_scm"],
    use_scm_version=True,
)
