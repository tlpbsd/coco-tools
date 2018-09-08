#!/usr/bin/env python

from setuptools import setup, find_packages


LONG_DESCRIPTION = """
jamieleecho-coco-tools contains tools that are useful for Color Computer users.
They currently include a tool for converting OS-9 VEF images to PNG.
"""


setup(
    name='jamieleecho-coco-tools',
    version='0.1.0',

    description='TRS-80 Color Computer Tools',
    long_description=LONG_DESCRIPTION,

    # The project's main homepage.
    url='https://github.com/jamieleecho/coco-tools',

    # Author details
    author='Jamie Cho',
    author_email='jamieleecho+coco_tools@gmail.com',

    # Choose your license
    license='GPLv2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    install_requires=[
        'Pillow',
        'pypng',
    ],

    # What does your project relate to?
    keywords='coco image conversion trs-80 tandy',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=('tests',)),

    entry_points={
        'console_scripts': [
            'cm3toppm=coco.cm3toppm:main',
            'hrstoppm=coco.hrstoppm:main',
            'mgetoppm=coco.mgetoppm:main',
            'veftopng=coco.veftopng:main',
        ],
    },
)
