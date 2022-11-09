# Developing the symstore Package

Information on setting up development environment and running checks.

## Setting Up Development Environment

The recommended set-up is to create a virtualenv sandbox and install the symstore package in the sandbox with pip.

Note that you need to use _pip version 21.3_ or later to be able to install the package in development mode.

Set-up and activate the sandbox with:

    $ mkdir symstore
    $ cd symstore
    $ virtualenv sandbox
    $ . sandbox/bin/activate

Clone the symstore repository:

    $ git clone <repo-url> src

Install the symstore package in developer mode:

    $ cd src
    $ pip install -e .[dev]

This will make in in-place installation of the symstore package.
It will also install all the necessary tools for development.


## Running Tests and Checks

To run all tests and checks goto the root directory of the repository and type:

    $ make

This will run all tests and perform flake8 static check on the code.

### Make targets

The Makefile provides following targets:

    $ make flake8

Runs flake8 tool on all the source code.
Performs static checks and checks PEP8 style conformance.

    $ make check

Runs all the integration tests.

    $ make cov

Runs all the tests and generates a coverage report.
Stores the report in ``htmlcov`` directory.

    $ make all

The default target.
Will run flake8 checks and integrations tests.

## Making a Release to PyPi

* create ~/.pypirc

    [distutils]
    index-servers =
      pypi
      pypitest

    [pypi]
    repository=https://upload.pypi.org/legacy/

    [pypitest]
    repository=https://test.pypi.org/legacy/

* pip install flit

* flit publish --repository=pypitest

* check https://testpypi.python.org/pypi/symstore

* flit publish
