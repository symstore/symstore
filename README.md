[![Build Status](https://app.travis-ci.com/symstore/symstore.svg?branch=master)](https://app.travis-ci.com/github/symstore/symstore)
[![Downloads](https://pepy.tech/badge/symstore)](https://pepy.tech/project/symstore)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/symstore/badges/downloads.svg)](https://anaconda.org/conda-forge/symstore)

# symstore

A python module and command line utility for publishing windows debugging symbols to symbols store.
The symbols published in this format can be consumed by the common development tools for windows, such as Visual Studio and WinDbg.
See [Using SymStore](https://docs.microsoft.com/en-us/windows/win32/debug/using-symstore) for more information on windows symbols store.

Currently it is possible to publish PDB and PE (exe and dll) files to a local file system.

## Installing

Symstore is available on pypi and conda package repositories.
It can be installed with ``pip`` or ``conda`` utilities, see below.

### Pip

Install symstore with pip utility by running:

    $ pip install symstore

This will install the command line utility ``symstore`` as well as python module ``symstore``.

It is also possible to install symstore package from source code.
For example, clone symstore's git repository with:

    $ git clone <repo-url> symstore

and install it with pip:

    $ pip install symstore/

### Conda

The symstore package is available on ``conda-forge`` channel.
To install it, activate your conda environment and run:

    $ conda install --channel conda-forge symstore

## Using

### command line

Use the ``symstore`` command to publish the symbols. Run ``symstore --help`` for details.

### Python module

To publish symbols programmatically use the ``symstore`` module.
See ``symstore/command_line.py`` for an example on how to use the API.

### Compression

The symstore package supports compressing the data files when publishing them.
This can lead to significant reduction of data that needs to be transferred while accessing symbols.

The compression mode is activated with ``--compress`` or ``-z`` flag to ``symstore`` command line utility.

On non-Windows systems, symstore uses the native ``gcab`` library via python bindings to compress data.
The required packages must be available on the system for the compression mode to work.

On Ubuntu 22.04, install following packages:

 * gir1.2-gcab-1.0
 * python3-gi

On Ubuntu 20.04 or 18.04, install following packages:

  * gir1.2-gcab-1.0
  * python-gi

On Ubuntu 16.04, install following packages:

  * gir1.2-libgcab-1.0
  * python-gi

On FreeBSD 12.2, install following binary packages:

 * gcab
 * py37-gobject3

If symstore is unable to load required packages while compression mode is requested, following error message will be displayed:

    gcab module not available, compression not supported

On Windows systems, symstore uses the standard `makecab.exe` utility.
The `makecab.exe` utility normally is included by default in Windows installations, thus symstore compression will work out-of-box.


## Change Log

### 0.3.4 (6 December 2022)

* adds support for transaction comments (`--comment` cli argument)
* parallelized transaction publication code (pull request #26)
* `--max-compress` cli argument to disable compression on big files (pull request #27)
* fixed issue with wrong symstore paths of some PE-files (issue #25)
* dropped support for python 2.7, 3.4, 3.5
* officially support python 3.11

### 0.3.3 (30 September 2021)

* add `--skip-published` cli flag (pull request #19)
* support publishing PE files with non-standard file extension (issue #20)

### 0.3.2 (28 June 2021)

* support compression on windows (pull request #18)

### 0.3.1 (14 March 2021)

* fixes EXE/DLL parsing bug which generated wrong hashes (pull request #16)
* add information on enabling compression on FreeBSD 12.2 and Ubuntu 20.04
* officially support python 3.9

### 0.3.0 (1 October 2020)

* support for deleting transactions
* better error message when specified PDB/EXE/DLL is not found
* officially support python 3.8

### 0.2.7 (25 September 2019)

* explicitly put this code under MIT license

### 0.2.6 (29 August 2019)

* don't leak open file handles during operation (issue #10)

### 0.2.5 (16 December 2018)

* officially support python 3.7
* fixed write errors to history.txt on windows/python2.7

### 0.2.4 (31 January 2018)

* improved error handling on missing GCab python binding

### 0.2.3 (24 June 2017)

* support publishing PDBs with longer root stream (even larger files)
* officially support python 3.6

### 0.2.2 (16 January 2017)

* support republishing same file in a new transaction
* print nice error message on unexpected file extensions
* more details in the docs on how to setup gcab to enable compression

### 0.2.1 (29 September 2016)

* generate correct signature for PDBs with age larger then 10
* support publishing PDBs with multi-page root stream (larger files)
* fetch PDB age from DBI stream
* support publishing PDBs without DBI stream

### 0.2.0 (22 March 2016)

* added compression support

### 0.1.1 (10 February 2016)

* dropped dependency to pdbparse and construct modules
* added support for python 3

### 0.1.0 (14 January 2016)

* dropped dependency to pefile module
* print nice error message on currupt PE files
