#!/usr/bin/env python

from distutils import core

core.setup(
    name="symstore",
    version="0.1",
    install_requires=[
        "pdbparse",
        "pefile",
    ],
    packages=["symstore"],
    scripts=["symstore/bin/symstore"],
)
