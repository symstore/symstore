===============================
Developing the symstore Package
===============================

Information on setting up development environment and running checks.

Setting Up Development Environment
==================================

The recommended set-up is to create a virtualenv sandbox and install the symstore package in the sandbox with pip.

Set-up and activate the sandbox with:

.. code:: sh

    $ mkdir symstore
    $ cd symstore
    $ virtualenv sandbox
    $ . sandbox/bin/activate

Clone the symstore repository:

.. code:: sh

    $ git clone <repo-url> src

Install the symstore package in developer mode:

.. code:: sh

    $ cd src
    $ pip install -e .[develop]

This will make in in-place installation of the symstore package.
It will also install all the necessary tools for development.


Running Tests and Checks
========================

To run all tests and checks goto the root directory of the repository and type:

.. code:: sh

    $ make

This will run all tests and perform flake8 static check on the code.

Make targets
------------

The Makefile provides following targets:

.. code:: sh

    $ make flake8

Runs flake8 tool on all the source code.
Performs static checks and checks PEP8 style conformance.

.. code:: sh

    $ make check

Runs all the integration tests.

.. code:: sh

    $ make cov

Runs all the tests and generates a coverage report.
Stores the report in ``htmlcov`` directory.

.. code:: sh

    $ make all

The default target.
Will run flake8 checks and integrations tests.
