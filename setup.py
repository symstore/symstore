#!/usr/bin/env python
import setuptools
from os import path

VERSION = open(path.join("symstore", "VERSION")).read().strip()

setuptools.setup(
    name="symstore",
    version=VERSION,
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
