#!/usr/bin/env python

from __future__ import absolute_import

import sys
import argparse
import symstore


class CompressionNotSupported(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="publish windows debugging files")

    parser.add_argument("store_path", metavar="STORE_PATH",
                        type=str,
                        help="root directory of the symbol store")
    parser.add_argument("files", metavar="FILE", type=str, nargs="+",
                        help="PDB or PE file(s) to publish")

    parser.add_argument("-z", "--compress",
                        action="store_true",
                        help="publish compressed files")

    parser.add_argument("-p", "--product-name", default="",
                        help="name of the product")

    parser.add_argument("-r", "--product-version", default="",
                        help="version of the product")

    parser.add_argument("--version",
                        action="version",
                        version="symstore %s" % symstore.VERSION,
                        help="show program's version number and exit")

    return parser.parse_args()


def err_exit(error_msg):
    sys.stderr.write("%s\n" % error_msg)
    sys.exit(1)


def unknown_ext_err(file, file_extension):
    if len(file_extension) > 0:
        msg = "unknown file extension '%s'" % file_extension
    else:
        msg = "no file extension"

    err_exit("%s: %s, can't figure out file format" % (file, msg))


def check_compression_support(compress_flag):
    if not compress_flag:
        # compression not request, no need to check
        return

    from symstore import cab
    if not cab.compression_supported:
        raise CompressionNotSupported()


def main():

    args = parse_args()

    sym_store = symstore.Store(args.store_path)

    try:
        # error-out if no compression
        check_compression_support(args.compress)

        # create new add transaction, add all specified files
        transaction = sym_store.new_transaction(args.product_name,
                                                args.product_version)
        for file in args.files:
            transaction.add_file(file, args.compress)

        # commit the transaction to the store
        sym_store.commit(transaction)
    except symstore.UnknownFileExtension as e:
        unknown_ext_err(file, e.file_extension)
    except symstore.FileFormatError as e:
        err_exit("%s: invalid %s file: %s" % (file, e.format_name, e))
    except CompressionNotSupported:
        err_exit("gcab module not available, compression not supported")
