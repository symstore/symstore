#!/usr/bin/env python

from __future__ import absolute_import

import sys
import argparse
import symstore
from pathlib import Path


class CompressionNotSupported(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="publish windows debugging files")

    parser.add_argument("-d", "--delete",
                        metavar="TRANSACTION_ID",
                        help="Delete transaction.")

    parser.add_argument("-z", "--compress",
                        action="store_true",
                        help="Publish compressed files.")

    parser.add_argument("-m", "--max-compress",
                        type=int, default=None,
                        help="Specifies maximum size of files to compress. "
                             "File above the limit are published uncompressed.")

    parser.add_argument("-p", "--product-name", default="",
                        help="Name of the product.")

    parser.add_argument("-r", "--product-version", default="",
                        help="Version of the product.")

    parser.add_argument("-c", "--comment", default="",
                        help="Comment for the transaction.")

    parser.add_argument("-s", "--skip-published",
                        action="store_true",
                        default=False,
                        help="Exclude all previously published files from "
                             "transaction.  Uses file's hash to check if it's "
                             "already exists in the store.")

    parser.add_argument("--version",
                        action="version",
                        version="symstore %s" % symstore.__version__,
                        help="Show program's version number and exit.")

    parser.add_argument("store_path", metavar="STORE_PATH",
                        type=str,
                        help="Root directory of the symbol store.")

    parser.add_argument("files", metavar="FILE", type=str, nargs="*",
                        help="PDB or PE file(s) to publish.")

    return parser.parse_args()


def err_exit(error_msg):
    sys.stderr.write("%s\n" % error_msg)
    sys.exit(1)


def check_compression_support(compress_flag):
    if not compress_flag:
        # compression not request, no need to check
        return

    from symstore import cab
    if cab.compress is None:
        raise CompressionNotSupported()


def delete_action(sym_store, transaction_id):
    try:
        sym_store.delete_transaction(transaction_id)
    except symstore.TransactionNotFound:
        err_exit("no transaction with id '%s' found" % transaction_id)


def add_action(sym_store, files,
               product_name, product_version, comment,
               compress, max_compress, skip_published):

    def _compress_file(file):
        """
        makes a decision if the file should be published compressed
        """

        if not compress:
            # compression is disabled for this transaction
            return False

        if max_compress is None:
            # compression is enabled,
            # but there is no file size specified
            return True

        # only compress if the file is inside
        # the compression file size limit
        file_size = Path(file).stat().st_size
        return file_size <= max_compress

    try:
        # error-out if no compression
        check_compression_support(compress)

        # create new add transaction, add all specified files
        transaction = sym_store.new_transaction(product_name, product_version,
                                                comment)
        for file in files:
            entry = transaction.new_entry(file, _compress_file(file))

            if skip_published and entry.exists():
                # 'skip published' mode is on and this file
                # have already been published, skip it skipper
                continue

            transaction.add_entry(entry)

        if len(transaction.entries) == 0:
            err_exit("no new files to publish")

        # commit the transaction to the store
        sym_store.commit(transaction)
    except symstore.UnknownFileType:
        err_exit("%s: can't figure out file type" % file)
    except symstore.FileFormatError as e:
        err_exit("%s: invalid %s file: %s" % (file, e.format_name, e))
    except CompressionNotSupported:
        err_exit("gcab module not available, compression not supported")
    except symstore.FileNotFound as e:
        err_exit("No such file: %s" % e.filename)
    except symstore.CabCompressionError as e:
        err_exit("Error creating CAB\n%s" % e)


def main():
    args = parse_args()

    sym_store = symstore.Store(args.store_path)

    if args.delete is not None:
        delete_action(sym_store, args.delete)
        return

    # otherwise this is an 'add' action
    add_action(sym_store, args.files, args.product_name,
               args.product_version, args.comment,
               args.compress, args.max_compress,
               args.skip_published)
