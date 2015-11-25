#!/usr/bin/env python
import setuptools

setuptools.setup(
    name="symstore",
    version="0.1",
    install_requires=[
        "pdbparse",
        "pefile",
    ],
    packages=["symstore"],
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
