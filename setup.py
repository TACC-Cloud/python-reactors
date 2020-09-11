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

repo_url = 'https://github.com/TACC-Cloud/python-reactors'
pkg_dir = 'src/reactors'

# Create version file
version = "0.7.0"
with open(os.path.join(pkg_dir,'version.py'), 'w') as f:
    contents = "# THIS FILE IS GENERATED FROM SETUP.PY\nversion = '{0}'".format(version)
    f.write(contents)

def get_readme(fp='./README.md'):
    """Get README contents
    """
    if os.path.isfile(fp):
        with open(fp, 'r') as f:
            return f.read()
    else:
        return str("")

def get_requirements(fp='./requirements.txt'):
    """Parse requirements from requirements.txt. Returns list for
    `install_requires`.
    """
    comment_prefixes = ("#")
    requires = list()

    # Read requirements.txt to list of lines
    with open(fp) as f:
        req_raw = f.read().splitlines()

    for req in req_raw:
        is_comment = any([req.startswith(prefix) for prefix in comment_prefixes])
        if not is_comment:
            requires.append(req)
    return requires


setup(
    name='reactors',
    version=version,
    description='Software development kit for Tapis actors',
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    url=repo_url,
    author='Matthew W Vaughn, Ethan Ho, Shweta Gopaulakrishnan',
    author_email='eho@tacc.utexas.edu',
    classifiers=[
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        # 'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='sdk tapis actors reactors',
    package_dir={'':'src'},
    packages=find_packages("src", exclude=[]),
    install_requires=get_requirements(),
    data_files=[('', ['requirements.txt'])],
    package_data={},
    include_package_data=True,
    python_requires='>=3.6, <4',
<<<<<<< HEAD
=======
    install_requires=[],
>>>>>>> fix_context
    extras_require={
        'dev': ['pytest'],
        'test': ['pytest']
    },
    entry_points={},
    project_urls={
        'Bug Reports': os.path.join(repo_url, 'issues'),
    },
    include_dirs=[],
)

