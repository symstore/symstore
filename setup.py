#!/usr/bin/env python
import setuptools
from os import path

VERSION = open(path.join("symstore", "VERSION")).read().strip()

setuptools.setup(
    name="symstore",
    version=VERSION,
    description="publish PDB and PE files to symbols store",
    long_description=open("README.rst", "r").read(),
    url="https://github.com/elmirjagudin/symstore",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="development symstore pdb",
    packages=["symstore"],
    package_data={"symstore": ["VERSION"]},
    entry_points={
        "console_scripts": ["symstore=symstore.command_line:main"],
    },
    extras_require={
        "develop":
            [
                "coverage",
                "flake8",
                "mock"
            ]
    }
)
