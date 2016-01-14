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
See ``symstore/bin/symstore`` for an example on how to use the API.

Change Log
==========

0.1.0 (14 January 2016)
-----------------------

* dropped dependency to pefile module
* print nice error message on currupt PE files
