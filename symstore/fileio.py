from __future__ import absolute_import

import errno
from symstore import errs


def read_all(fname, mode=None):
    """
    read all contents of a file
    """
    args = [fname]
    if mode is not None:
        args.append(mode)

    with open(*args) as f:
        return f.read()


def open_rb(filepath):
    """
    open file for reading, in binary mode

    :raises symstore.FileNotFound: if specified file does not exist
    """
    try:
        return open(filepath, "rb")
    except IOError as e:
        # to be backward compatible with python 2,
        # catch IOError exception and check the errnor,
        # to detect when specified file does not exits
        if e.errno == errno.ENOENT:
            raise errs.FileNotFound(e.filename)
        # unexpected error
        raise e
