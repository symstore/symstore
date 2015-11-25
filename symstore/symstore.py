import os
import re
import shutil
import pdbparse
import pefile
from os import path
from datetime import datetime

TRANSACTION_LINE_RE = re.compile(
    r"(\d+),"
    r"(add|del),"
    r"(file|ptr),"
    r"((?:\d\d/\d\d/\d\d\d\d),(?:\d\d:\d\d:\d\d)),"
    "\"([^\"]*)\","
    "\"([^\"]*)\","
    "\"([^\"]*)\","
    r".*")

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
    pdb = pdbparse.parse(filename, fast_load=True)

    pdb.STREAM_PDB.load()
    guid = pdb.STREAM_PDB.GUID
    guid_str = "%.8X%.4X%.4X%s" % (guid.Data1, guid.Data2, guid.Data3,
                                   guid.Data4.encode("hex").upper())

    return "%s%s" % (guid_str, pdb.STREAM_PDB.Age)


def _pe_hash(file):
    pe = pefile.PE(file, fast_load=True)

    return "%X%X" % (pe.FILE_HEADER.TimeDateStamp,
                     pe.OPTIONAL_HEADER.SizeOfImage)


def _image_type(file):
    file_ext = path.splitext(file)[1][1:].lower()
    # TODO handle cases of unknown file extensions
    return EXT_TYPES[file_ext]


def _file_hash(file):

    image_type = _image_type(file)

    if image_type == PDB_IMAGE:
        return _pdb_hash(file)

    assert image_type == PE_IMAGE
    return _pe_hash(file)


def _new_or_empty(filename):
    if not path.isfile(filename):
        return True

    return os.stat(filename).st_size == 0


def _append_line(filename, line):
    with open(filename, "a") as f:
        f.write("%s" % line)


class TransactionEntry:
    def __init__(self, symstore, data_path, source_file):
        self._symstore = symstore
        self.file_name, self.file_hash = data_path.split("\\")
        self.source_file = source_file

    def open(self):
        fpath = path.join(self._symstore._path, self.file_name,
                          self.file_hash, self.file_name)

        return open(fpath, "r")


class Transaction:
    transaction_entry_class = TransactionEntry

    def __init__(self, symstore, id, type, ref,  timestamp, product,
                 version, comment):

        self._symstore = symstore
        self.id = id
        self.type = type
        self.ref = ref
        self.timestamp = timestamp
        self.product = product
        self.version = version
        self.comment = comment

    def _entries_file(self):
        return open(path.join(self._symstore._admin_dir, self.id))

    @property
    def entries(self):
        entries = []
        with self._entries_file() as efile:
            for line in efile.readlines():
                entry, source_file = [
                    s.strip("\"") for s in line.strip().split(",")]

                transaction_entry = self.transaction_entry_class(
                    self._symstore, entry, source_file)

                entries.append(transaction_entry)

        # TODO catch IOERrror
        # TODO catch parse errors

        return entries


def parse_transaction_line(line):
    (id, type, ref, timestamp, product, version, comment) = \
        TRANSACTION_LINE_RE.match(line).groups()

    ts = datetime.strptime(timestamp, "%m/%d/%Y,%H:%M:%S")
    return id, type, ref,  ts, product, version, comment


class Transactions:
    transaction_class = Transaction

    def __init__(self, symstore):
        self._symstore = symstore
        self._transactions = None

    def _server_file(self):
        return open(self._symstore._server_file)

    def _server_file_exists(self):
        return path.isfile(self._symstore._server_file)

    def _parse_server_file(self):
        if not self._server_file_exists():
            return {}

        transactions = {}

        with self._server_file() as sfile:
            for line in sfile.readlines():
                transaction = self.transaction_class(
                    self._symstore, *parse_transaction_line(line))

                transactions[transaction.id] = transaction

        return transactions

    def _get_transactions(self):
        if self._transactions is None:
            self._transactions = self._parse_server_file()
        return self._transactions

    def items(self):
        return self._get_transactions().items()


class History:
    transaction_class = Transaction

    def __init__(self, symstore):
        self._symstore = symstore
        self._transactions = None

    def _history_file(self):
        return open(self._symstore._history_file)

    def _history_file_exists(self):
        return path.isfile(self._symstore._history_file)

    def _parse_history_file(self):
        if not self._history_file_exists():
            return []

        transactions = []

        with self._history_file() as hfile:
            for line in hfile.readlines():
                transaction = self.transaction_class(
                    self._symstore, *parse_transaction_line(line))

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
            last_id = int(open(last_id_file, "r").read())

        return "%.010d" % (last_id + 1)

    def _store_file(self, file):
        file_dir = path.join(path.basename(file), _file_hash(file))
        dest_dir = path.join(self._path, file_dir)

        os.makedirs(dest_dir)
        shutil.copy(file, dest_dir)

        return file_dir

    def _write_transaction_file(self, transaction_id, added_entries):
        transaction_filename = path.join(self._admin_dir, transaction_id)
        with open(transaction_filename, "w") as transfile:
            for pdb_dir, file in added_entries:
                pdb_dir = pdb_dir.replace("/", "\\")
                file = path.abspath(file)
                transfile.write("\"%s\",\"%s\"\n" % (pdb_dir, file))
        # TODO handle file write errors

    def _record_transaction(self, start_time, transaction_id,
                            product, version):
        """
        Record new transaction in history.txt and server.txt files.
        """
        date_stamp = start_time.strftime("%m/%d/%Y")
        time_stamp = start_time.strftime("%H:%M:%S")

        log_line = """%s,add,file,%s,%s,"%s","%s","",""" % \
                   (transaction_id, date_stamp, time_stamp, product, version)

        _append_line(self._server_file, log_line + "\n")

        line_break = "" if _new_or_empty(self._history_file) else "\n"
        _append_line(self._history_file, line_break + log_line)

    def _write_transaction_id(self, trans_id):
        with open(self._last_id_file, "w") as id_file:
            id_file.write(trans_id)

    def _touch_pingme(self):
        pingme_path = self._pingme_file

        if not path.isfile(pingme_path):
            open(pingme_path, "a")
            return

        os.utime(pingme_path, None)

    def add(self, files, product, version):
        trans_start_time = datetime.now()
        self._create_dirs()
        trans_id = self._next_transaction_id()

        added_dirs = []

        for file in files:
            added_dirs.append(self._store_file(file))

        self._write_transaction_file(trans_id, zip(added_dirs, files))
        self._record_transaction(trans_start_time, trans_id, product, version)
        self._write_transaction_id(trans_id)
        self._touch_pingme()
