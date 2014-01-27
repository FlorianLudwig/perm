# -*- coding: utf-8 -*-
import os
import sys

import rsetup.setup
from setuptools import setup, find_packages

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
VERSION_SUFFIX = ''


if '--dev' in sys.argv:
    VERSION_SUFFIX = rsetup.setup.git_version_suffix()
    sys.argv.remove('--dev')



setup(
    name="perm",
    version="0.0.1" + VERSION_SUFFIX,
    author="Grey Rook Entertainment",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    package_data={'serviceapp': rsetup.setup.find_package_data(os.path.join(BASE_PATH, 'perm'))},
    install_requires=['rueckenwind>=0.0.0.git0'],
    cmdclass={'sdist': rsetup.setup.sdist_with_version_suffic(VERSION_SUFFIX)}
)
