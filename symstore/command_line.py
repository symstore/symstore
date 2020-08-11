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

    parser.add_argument("-d", "--delete",
                        metavar="TRANSACTION_ID",
                        help="delete transaction")

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

    parser.add_argument("store_path", metavar="STORE_PATH",
                        type=str,
                        help="root directory of the symbol store")

    parser.add_argument("files", metavar="FILE", type=str, nargs="*",
                        help="PDB or PE file(s) to publish")

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


def delete_action(sym_store, transaction_id):
    try:
        sym_store.delete_transaction(transaction_id)
    except symstore.TransactionNotFound:
        err_exit("no transaction with id '%s' found" % transaction_id)


def add_action(sym_store, files, product_name, product_version, compress):
    try:
        # error-out if no compression
        check_compression_support(compress)

        # create new add transaction, add all specified files
        transaction = sym_store.new_transaction(product_name, product_version)
        for file in files:
            transaction.add_file(file, compress)

        # commit the transaction to the store
        sym_store.commit(transaction)
    except symstore.UnknownFileExtension as e:
        unknown_ext_err(file, e.file_extension)
    except symstore.FileFormatError as e:
        err_exit("%s: invalid %s file: %s" % (file, e.format_name, e))
    except CompressionNotSupported:
        err_exit("gcab module not available, compression not supported")
    except symstore.FileNotFound as e:
        err_exit("No such file: %s" % e.filename)


def main():
    args = parse_args()
    sym_store = symstore.Store(args.store_path)

    if args.delete is not None:
        delete_action(sym_store, args.delete)
        return

    # otherwise this is an 'add' action
    add_action(sym_store, args.files, args.product_name,
               args.product_version, args.compress)
