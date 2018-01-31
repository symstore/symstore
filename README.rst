========
symstore
========

A python module and command lite utility for publishing windows debugging symbols to symbols store.
The symbols published in this format can be consumed by the common development tools for windows, such as Visual Studio and WinDbg.
See `Using SymStore <https://msdn.microsoft.com/en-us/library/windows/desktop/ms681417%28v=vs.85%29.aspx>`_ for more information on windows symbols store.

Currently it is possible to publish PDB and PE (exe and dll) files to a local file system.

Installing
==========

Install with pip utility by running:

.. code:: sh

    $ pip install symstore

This will install the command line utility ``symstore`` as well as python module ``symstore``.

It is also possible to install symstore package from source code.
For example, clone symstore's git repository with:

.. code:: sh

    $ git clone <repo-url> symstore

and install it with pip:

.. code:: sh

    $ pip install symstore/


Using
=====

command line
------------

Use the ``symstore`` command to publish the symbols. Run ``symstore --help`` for details.

Python module
-------------

To publish symbols programmatically use the ``symstore`` module.
See ``symstore/command_line.py`` for an example on how to use the API.

Compression
-----------

The symstore package supports compressing the data files when publishing them.
This can lead to significant reduction of data that needs to be transferred while accessing symbols.

The compression mode is activated with ``--compress`` or ``-z`` flag to ``symstore`` command line utility.

Symstore uses the native ``gcab`` library via introspection to compress data.
The required packages must be available on the system for the compression mode to work.

On ubuntu, install following packages:

  * gir1.2-libgcab-1.0
  * python-gi

In case symstore is not able to locate python-gi and gir packages while compression mode is requested, following error message will be displayed:

.. code:: sh

    gcab module not available, compression not supported

Change Log
==========

0.2.4 (31 January 2018)
-----------------------

* improved error handling on missing GCab python binding

0.2.3 (24 June 2017)
--------------------

* support publishing PDBs with longer root stream (even larger files)
* officially support python 3.6

0.2.2 (16 January 2017)
-----------------------

* support republishing same file in a new transaction
* print nice error message on unexpected file extensions
* more details in the docs on how to setup gcab to enable compression

0.2.1 (29 September 2016)
-------------------------

* generate correct signature for PDBs with age larger then 10
* support publishing PDBs with multi-page root stream (larger files)
* fetch PDB age from DBI stream
* support publishing PDBs without DBI stream

0.2.0 (22 March 2016)
---------------------

* added compression support

0.1.1 (10 February 2016)
------------------------

* dropped dependency to pdbparse and construct modules
* added support for python 3

0.1.0 (14 January 2016)
-----------------------

* dropped dependency to pefile module
* print nice error message on currupt PE files
