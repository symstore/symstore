#!/usr/bin/env python

from __future__ import absolute_import

import sys
import argparse
import symstore
import re
import os


class CompressionNotSupported(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="publish windows debugging files")

    parser.add_argument("-s", "--store_path",
                        dest="store_path",
                        metavar="STORE_PATH",
                        type=str,
                        help="root directory of the symbol store")

    parser.add_argument("-t", "--target_files",
                        dest="target_files",
                        metavar="FILE(S)\FOLDER",
                        type=str, nargs="+",
                        help="PDB or PE file(s) to publish"
                        " or directory with files.")

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


def parse_directory(target_path, *patterns):
    for dir_name, _, files in os.walk(target_path):
        for f in files:
            for pattern in patterns:
                if re.match(pattern, f):
                    yield os.path.join(dir_name, f)


def main():

    args = parse_args()

    sym_store = symstore.Store(args.store_path)

    try:
        # error-out if no compression
        check_compression_support(args.compress)

        # create new add transaction, add all specified files
        transaction = sym_store.new_transaction(args.product_name,
                                                args.product_version)

        for target_item in args.target_files:
            if os.path.isdir(target_item):
                for item_target_file in parse_directory(target_item,
                                                        ".*pdb$|.*exe$"):
                    transaction.add_file(item_target_file, args.compress)
            elif os.path.isfile(target_item):
                transaction.add_file(target_item, args.compress)
            else:
                transaction.add_file(target_item, args.compress)

        # commit the transaction to the store
        sym_store.commit(transaction)
    except symstore.UnknownFileExtension as e:
        unknown_ext_err(file, e.file_extension)
    except symstore.FileFormatError as e:
        err_exit("%s: invalid %s file: %s" % (file, e.format_name, e))
    except CompressionNotSupported:
        err_exit("gcab module not available, compression not supported")

if __name__ == '__main__':
    main()
