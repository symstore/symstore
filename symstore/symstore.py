from __future__ import absolute_import

import os
import re
import time
import shutil
from os import path
from symstore import pe
from symstore import pdb
from symstore import cab
from symstore import errs
from symstore import fileio
from datetime import datetime


TRANSACTION_PREFIX_RE = re.compile(
    r"(\d+),"
    r"(add|del),"
    r"(.*)"
)

TRANSACTION_ADD_RE = re.compile(
    r"(file|ptr),"
    r"((?:\d\d/\d\d/\d\d\d\d),(?:\d\d:\d\d:\d\d)),"
    "\"([^\"]*)\","
    "\"([^\"]*)\","
    "\"([^\"]*)\","
    r".*")

TRANSACTION_DEL_RE = re.compile(
    r"(\d+)"
)

ADMIN_DIR = "000Admin"
LAST_ID_FILE = path.join(ADMIN_DIR, "lastid.txt")
HISTORY_FILE = path.join(ADMIN_DIR, "history.txt")
SERVER_FILE = path.join(ADMIN_DIR, "server.txt")
PINGME_FILE = "pingme.txt"

PDB_IMAGE, PE_IMAGE = range(2)

EXT_TYPES = dict(pdb=PDB_IMAGE,
                 exe=PE_IMAGE,
                 dll=PE_IMAGE)


def _pdb_hash(filename):
    pdbfile = pdb.PDBFile(filename)

    # figure out age string to be used in the hash string
    if pdbfile.age is None:
        # some pdb files does not have age,
        # accoring to symstore.exe we should just
        # skip adding the age to the hash string
        age_str = ""
    else:
        age_str = "%x" % pdbfile.age

    return "%s%s" % (pdbfile.guid, age_str)


def _pe_hash(file):
    pefile = pe.PEFile(file)

    return "%X%X" % (pefile.TimeDateStamp, pefile.SizeOfImage)


def _image_type(file):
    file_ext = path.splitext(file)[1][1:].lower()

    if file_ext not in EXT_TYPES:
        raise errs.UnknownFileExtension(file_ext)

    return EXT_TYPES[file_ext]


def _file_hash(file):

    image_type = _image_type(file)

    if image_type == PDB_IMAGE:
        return _pdb_hash(file)

    assert image_type == PE_IMAGE
    return _pe_hash(file)


def _is_empty_dir(dir_path):
    return len(os.listdir(dir_path)) == 0


class TransactionEntry:
    def __init__(self, symstore, file_name, file_hash, source_file,
                 compressed=False):
        self._symstore = symstore
        self.file_name = file_name
        self.file_hash = file_hash
        self.source_file = source_file
        self.compressed = compressed

    @classmethod
    def load(cls, symstore, file_name, file_hash, source_file):
        """
        Load transaction from disk.

        Examine files in symstore directory and create an transaction
        entry object that represents it.
        """

        # check if data file is compressed
        compressed_path = path.join(symstore._path, file_name,
                                    file_hash, file_name[:-1]+"_")
        # if both compressed and uncompressed versions of the file exists,
        # give preference to the compressed one
        compressed = path.isfile(compressed_path)

        return cls(symstore, file_name, file_hash, source_file, compressed)

    def _dest_dir(self):
        return path.join(self._symstore._path, self.file_name, self.file_hash)

    def read(self):
        if self.compressed:
            raise NotImplementedError("reading compressed data not supported")

        fpath = path.join(self._dest_dir(), self.file_name)
        return fileio.read_all(fpath, "rb")

    def publish(self):
        """
        publish this entry's source file inside symstore
        """
        dest_dir = self._dest_dir()

        if not path.isdir(dest_dir):
            os.makedirs(dest_dir)

        if self.compressed:
            cab.compress(self.source_file,
                         path.join(dest_dir, self.file_name[:-1]+"_"))
        else:
            shutil.copy(self.source_file, dest_dir)
            # TODO handle I/O errors

    def __str__(self):
        return r""""%s\%s","%s""""" % \
               (self.file_name,
                self.file_hash,
                path.abspath(self.source_file))


class Transaction:
    transaction_entry_class = TransactionEntry

    def __init__(self, symstore, id=None, type="add", ref="file",
                 timestamp=None, product=None, version=None, comment=None,
                 deleted_id=None):

        self._symstore = symstore
        self._entries = None
        self.id = id
        self.type = type
        self.ref = ref
        self.timestamp = timestamp
        self.product = product
        self.version = version
        self.comment = comment
        self.deleted_id = deleted_id

    def _commited(self):
        return self.id is not None

    def _entries_file_path(self):
        return path.join(self._symstore._admin_dir, self.id)

    def _entries_file(self, mode="r"):
        return open(self._entries_file_path(), mode=mode)

    def _load_entries(self):
        if not self._commited():
            return []

        entries = []
        with self._entries_file() as efile:
            for line in efile.readlines():
                entry, source_file = [
                    s.strip("\"") for s in line.strip().split(",")]

                file_name, file_hash = entry.split("\\")

                transaction_entry = self.transaction_entry_class.load(
                    self._symstore, file_name, file_hash, source_file)

                entries.append(transaction_entry)

        # TODO catch IOERrror
        # TODO catch parse errors

        return entries

    def add_file(self, file, compress=False):
        """
        :raises symstore.FileNotFound: if specified file not found
        :raises pe.PEFormatError: on errors parsing PE (.exe/.dll) files
        :raises UnknownFileExtension: if file extension is not .pdb/.exe/.dll
        """
        entry = TransactionEntry(self._symstore,
                                 path.basename(file),
                                 _file_hash(file),
                                 file,
                                 compress)
        # TODO handle I/O errors from _file_hash()

        self.entries.append(entry)

    @property
    def entries(self):
        if self._entries is None:
            self._entries = self._load_entries()

        return self._entries

    def commit(self, id, now):
        assert not self._commited()

        self.timestamp = now
        self.id = id

        # publish all entries files to the store
        for entry in self.entries:
            entry.publish()

        # write new transaction file
        with self._entries_file("a") as efile:
            for entry in self.entries:
                efile.write("%s\n" % entry)
        # TODO handle I/O errors while opening/writing efile

    def mark_deleted(self):
        src = self._entries_file_path()
        dst = "%s.deleted" % src
        os.rename(src, dst)

    def __str__(self):
        date_stamp = self.timestamp.strftime("%m/%d/%Y")
        time_stamp = self.timestamp.strftime("%H:%M:%S")

        assert self._commited()
        return """%s,%s,%s,%s,%s,"%s","%s","",""" % \
               (self.id, self.type, self.ref, date_stamp, time_stamp,
                self.product, self.version)


def parse_transaction_line(line):
    # TODO handle parse errors in this function
    (id, type, tail) = TRANSACTION_PREFIX_RE.match(line).groups()

    if type == "add":
        # this is an 'add' transaction
        (ref, timestamp, product, version, comment) = \
            TRANSACTION_ADD_RE.match(tail).groups()

        timestamp = datetime.strptime(timestamp, "%m/%d/%Y,%H:%M:%S")
        return dict(id=id, type=type, ref=ref, timestamp=timestamp,
                    product=product, version=version, comment=comment)

    # this should be a delete transaction
    assert type == "del"
    (deleted_id,) = TRANSACTION_DEL_RE.match(tail).groups()

    return dict(id=id, type=type, deleted_id=deleted_id)


class FilesMap:
    def __init__(self):
        self._entries = {}

    def add_entry(self, entry, transaction):
        map_key = (entry.file_name, entry.file_hash)

        if map_key not in self._entries:
            self._entries[map_key] = []

        self._entries[map_key].append(transaction.id)

    def droped_entries(self, transaction):
        """
        figure out which files can be deleted
        """
        deleted_entries = []

        for entry, trans_ids in self._entries.items():
            if transaction.id not in trans_ids:
                continue

            if len(trans_ids) == 1:
                deleted_entries.append(entry)

        return deleted_entries


class Transactions:
    transaction_class = Transaction

    def __init__(self, symstore):
        self._symstore = symstore
        self._transactions = None

    def _server_file(self, mode="r"):
        return open(self._symstore._server_file, mode=mode)

    def _server_file_exists(self):
        return path.isfile(self._symstore._server_file)

    def _parse_server_file(self):
        if not self._server_file_exists():
            return {}

        transactions = {}

        with self._server_file() as sfile:
            for line in sfile.readlines():
                transaction = self.transaction_class(
                    self._symstore, **parse_transaction_line(line))

                transactions[transaction.id] = transaction

        return transactions

    def _get_transactions(self):
        if self._transactions is None:
            self._transactions = self._parse_server_file()
        return self._transactions

    def find(self, transaction_id):
        return self._get_transactions().get(transaction_id)

    def get_files_map(self):
        fmap = FilesMap()

        for transaction in self._get_transactions().values():
            for entry in transaction.entries:
                fmap.add_entry(entry, transaction)

        return fmap

    def items(self):
        return self._get_transactions().items()

    def add(self, transaction):
        with self._server_file("a") as sfile:
            sfile.write("%s\n" % transaction)
        # TODO handle I/O errors

    def rewrite_server_file(self, transactions):
        """
        overwrite the server.txt with specified transactions

            transactions - transactions to list in the server file
        """
        # make sure transactions list is sorted by transaction IDs
        transactions.sort(key=lambda v: v.id)

        with self._server_file("w") as sfile:
            for transaction in transactions:
                sfile.write("%s\n" % transaction)

    def delete(self, transaction):
        # figure out what files can be removed
        files_map = self.get_files_map()
        dropped = files_map.droped_entries(transaction)

        # delete any dropped files
        for file_name, file_hash in dropped:
            dir_path = path.join(self._symstore._path, file_name, file_hash)
            shutil.rmtree(dir_path)

            # if parent directory becomes empty, remove it as well
            parent_dir = path.dirname(dir_path)
            if _is_empty_dir(parent_dir):
                shutil.rmtree(parent_dir)

        # create a list of transaction without the deleted transaction
        new_transactions = [
            v for v in self._transactions.values()
            if v.id != transaction.id]

        # 'delete' transaction listing from server file
        self.rewrite_server_file(new_transactions)


class History:
    transaction_class = Transaction

    def __init__(self, symstore):
        self._symstore = symstore
        self._transactions = None

    def _history_file(self, mode="r"):
        return open(self._symstore._history_file, mode=mode)

    def _history_file_exists(self):
        return path.isfile(self._symstore._history_file)

    def _parse_history_file(self):
        if not self._history_file_exists():
            return []

        transactions = []

        with self._history_file() as hfile:
            for line in hfile.readlines():
                transaction = self.transaction_class(
                    self._symstore, **parse_transaction_line(line))

                transactions.append(transaction)

        return transactions

    def _get_transactions(self):
        if self._transactions is None:
            self._transactions = self._parse_history_file()
        return self._transactions

    def __len__(self):
        return len(self._get_transactions())

    def __getitem__(self, item):
        return self._get_transactions()[item]

    def _write_line(self, new_line):
        def prefix_with_newline(f):
            """
            figure out if we need to prefix the new transaction line
            with new line character
            """
            f.seek(0, os.SEEK_END)
            if f.tell() == 0:  # use tell() for python 2 compatibility
                # end of file is byte 0, this is an empty file,
                # no need for prefixing with with new line
                return False

            f.seek(-1, os.SEEK_END)
            ch = f.read(1)

            # use seek() for python 2 on windows compatibility otherwise
            # later file writes will fail
            f.seek(0, os.SEEK_END)

            return ch != b'\n'

        with self._history_file("ab+") as hfile:
            if prefix_with_newline(hfile):
                # add line break if appending to existing non-empty file
                hfile.write(b"\n")

            hfile.write(new_line.encode("utf-8"))

        # TODO handle I/O errors

    def add(self, transaction):
        self._write_line("%s" % transaction)

    def delete(self, transaction_id, next_transaction_id):
        self._write_line("%s,del,%s" % (next_transaction_id, transaction_id))


class Store:
    def __init__(self, store_path):
        self._path = store_path
        self.transactions = Transactions(self)
        self.history = History(self)

    @property
    def modify_timestamp(self):
        """
        Get the time when this symstore was last modified.

        The modify timestamp is returned as datetime.datetime object.
        """
        return datetime.fromtimestamp(os.stat(self._pingme_file).st_mtime)

    @property
    def _admin_dir(self):
        return path.join(self._path, ADMIN_DIR)

    @property
    def _last_id_file(self):
        return path.join(self._path, LAST_ID_FILE)

    @property
    def _history_file(self):
        return path.join(self._path, HISTORY_FILE)

    @property
    def _server_file(self):
        return path.join(self._path, SERVER_FILE)

    @property
    def _pingme_file(self):
        return path.join(self._path, PINGME_FILE)

    def _create_dirs(self):
        if not path.isdir(self._path):
            os.mkdir(self._path)
            # TODO handle mkdir errors

        admin_dir = self._admin_dir
        if not path.isdir(admin_dir):
            os.mkdir(admin_dir)
            # TODO handle mkdir errors

    def _next_transaction_id(self):
        last_id_file = self._last_id_file

        last_id = 0
        if path.isfile(last_id_file):
            # TODO handle open and read errors
            # TODO handle parse errors
            last_id = int(fileio.read_all(last_id_file))

        return "%.010d" % (last_id + 1)

    def _write_transaction_id(self, trans_id):
        with open(self._last_id_file, "w") as id_file:
            id_file.write(trans_id)

    def _touch_pingme(self, timestamp):
        pingme_path = self._pingme_file

        if not path.isfile(pingme_path):
            open(pingme_path, "a").close()

        os.utime(pingme_path, (timestamp, timestamp))

    def new_transaction(self, product, version, type="add"):
        return Transaction(self, type=type, product=product, version=version)

    def delete_transaction(self, transaction_id):
        # look up the transaction to delete
        transaction = self.transactions.find(transaction_id)
        if transaction is None:
            raise errs.TransactionNotFound()

        self.transactions.delete(transaction)
        transaction.mark_deleted()

        next_transaction_id = self._next_transaction_id()
        self.history.delete(transaction.id, next_transaction_id)

        self._write_transaction_id(next_transaction_id)
        self._touch_pingme(round(time.time()))

    def commit(self, transaction):
        self._create_dirs()

        now = round(time.time())

        transaction.commit(self._next_transaction_id(),
                           datetime.fromtimestamp(now))

        self.transactions.add(transaction)
        self.history.add(transaction)

        self._write_transaction_id(transaction.id)
        self._touch_pingme(now)
