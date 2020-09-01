#!/usr/bin/env python

"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
import os
import sys
from setuptools import setup, find_packages
from setuptools.extension import Extension

# ------------------------------ Env check utils -------------------------------

# Initialize variables
repo_url = 'https://github.com/TACC-Cloud/python-reactors'
pkg_dir = 'src/reactors'

# Create version file
VERSION = "0.7.0"
with open(os.path.join(pkg_dir,'version.py'), 'w') as VF:
    cnt = """# THIS FILE IS GENERATED FROM SETUP.PY\nversion = '%s'"""
    VF.write(cnt%(VERSION))

# Get README contents
README_fp = "README.md"
if os.path.isfile(README_fp):
    with open(README_fp, 'r') as f:
        README_contents = f.read()
else:
    README_contents = ""

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
setup(
    name='reactors',  # package name
    version=VERSION,  # Required
    description='Software development kit for Tapis actors',
    long_description=README_contents,
    long_description_content_type='text/markdown',
    url=repo_url,
    author='Matthew W Vaughn, Ethan Ho, Shweta Gopaulakrishnan',
    classifiers=[  # https://pypi.org/classifiers/
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha', # update this as necessary
        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        # 'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
	# Supported python versions
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='sdk tapis actors reactors',
    package_dir={'':'src'},
    packages=find_packages("src", exclude=[]),  # Required
    package_data={},
    include_package_data=True,
    python_requires='>=3.6, <4',
    install_requires=[
        'agavepy',
    ],
    extras_require={
        'dev': ['pytest'],
        'test': ['pytest']
    },
    entry_points={},
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    project_urls={  # Optional
        'Bug Reports': os.path.join(repo_url, 'issues'),
    },
    # Extensions and included libs
    # ext_modules=extensions,
    include_dirs=[],
)

