#!/usr/bin/env python
import setuptools
from os import path

VERSION = open(path.join("symstore", "VERSION")).read().strip()

setuptools.setup(
    name="symstore",
    version=VERSION,
    description="publish PDB and PE files to symbols store",
    url="https://github.com/elmirjagudin/symstore",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
    ],
    keywords="development symstore pdb",
    install_requires=[
        "pdbparse",
        "pefile",
        "construct"
    ],
    packages=["symstore"],
    package_data={"symstore": ["VERSION"]},
    scripts=["symstore/bin/symstore"],
    extras_require={
        "develop":
            [
                "coverage",
                "flake8",
                "mock"
            ]
    }
)
