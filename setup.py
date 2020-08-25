#!/usr/bin/env python
import setuptools
import symstore
from symstore import fileio


setuptools.setup(
    name="symstore",
    version=symstore.VERSION,
    description="publish PDB and PE files to symbols store",
    long_description=fileio.read_all("README.rst"),
    url="https://github.com/elmirjagudin/symstore",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    license="MIT",
    keywords="development symstore pdb",
    packages=["symstore"],
    package_data={"symstore": ["VERSION"]},
    data_files=[
        ("", ["LICENSE"])
    ],
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
