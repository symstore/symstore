# Developing the symstore Package

Information on setting up development environment and running checks.

## Setting Up Development Environment

The recommended set-up is to create a virtualenv sandbox and install the
symstore package in the sandbox with pip.

Set-up and activate the sandbox with:

    $ mkdir symstore
    $ cd symstore
    $ virtualenv sandbox
    $ . sandbox/bin/activate

Clone the symstore repository:

    $ git clone <repo-url> src

Install the symstore package in developer mode:

    $ cd src
    $ pip install -e .[develop]

This will make in in-place installation of the symstore package. It will also
install all the necessary tools for development.


## Running Tests and Checks

To run all tests and checks goto the root directory of the repository and type:

    $ make

This will run all tests and perform flake8 static check on the code.
