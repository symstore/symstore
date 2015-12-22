import io
import unittest
import tempfile
import shutil
import zipfile
import subprocess
from os import path
from datetime import datetime

import symstore

from tests import conf

SYMSTORE_COMMAND = path.join("symstore", "bin", "symstore")

SYMFILES_DIR = path.join(path.dirname(__file__), "symfiles")

ADMIN_DIR = "000Admin"
LAST_ID_FILE = "%s/%s" % (ADMIN_DIR, "lastid.txt")
HISTORY_FILE = "%s/%s" % (ADMIN_DIR, "history.txt")
SERVER_FILE = "%s/%s" % (ADMIN_DIR, "server.txt")


class ZipTransactionEntry:
    def __init__(self, symstore, data_path, source_file):
        self._symstore = symstore
        self.file_name, self.file_hash = data_path.split("\\")
        self.source_file = source_file

    def open(self):
        name = "%s/%s/%s" % (self.file_name, self.file_hash, self.file_name)
        return self._symstore._zfile.open(name)


class ZipTransaction(symstore.Transaction):
    transaction_entry_class = ZipTransactionEntry

    def _entries_file(self):
        name = "%s/%s" % (ADMIN_DIR, self.id)
        return io.TextIOWrapper(self._symstore._zfile.open(name))


class ZipTransactions(symstore.Transactions):
    transaction_class = ZipTransaction

    def _server_file(self):
        return io.TextIOWrapper(self._symstore._zfile.open(SERVER_FILE))

    def _server_file_exists(self):
        return True


class ZipHistory(symstore.History):
    transaction_class = ZipTransaction

    def _history_file(self):
        return io.TextIOWrapper(self._symstore._zfile.open(HISTORY_FILE))

    def _history_file_exists(self):
        return True


class ZipSymstore:
    def __init__(self, zfile_path):
        self._zfile = zipfile.ZipFile(zfile_path)
        self.transactions = ZipTransactions(self)
        self.history = ZipHistory(self)

    def _next_transaction_id(self):
        last_id = int(self._zfile.open(LAST_ID_FILE).read())
        return "%.010d" % (last_id + 1)


def _open_zip(zfile_name):
    return zipfile.ZipFile(path.join(SYMFILES_DIR, zfile_name))


def _file_part(path):
    sep_pos = path.rfind("/")
    if sep_pos == -1:
        sep_pos = path.rfind("\\")

    if sep_pos == -1:
        return path

    return path[sep_pos+1:]


class CliTester(unittest.TestCase):
    initial_dir_zip = None

    def recordStartTime(self):
        # record test's start time, used to verify created symstore's
        # modify timestamp
        self.start_timestamp = datetime.now()

    def setUp(self):
        self.recordStartTime()

        self.symstore_path = tempfile.mkdtemp()
        zfile = _open_zip(self.initial_dir_zip)

        zfile.extractall(self.symstore_path)

    def tearDown(self):
        shutil.rmtree(self.symstore_path)

    def run_add_command(self, options, files):

        files = [path.join(SYMFILES_DIR, f) for f in files]
        command = [SYMSTORE_COMMAND, self.symstore_path] + options + files
        if conf.WITH_COVERAGE:
            command = ["coverage", "run", "-p"] + command

        subprocess.check_call(command)

    def _assert_transaction_num(self, expected, got):
        self.assertEqual(expected, got,
                         "Unexpected number of transactions, "
                         "expected %s got %s." % (expected, got))

    def _assert_transaction_entry(self, transaction_id, expected, got):
            self.assertEqual(expected.file_name, got.file_name,
                             "Unexpected file name entry for transaction %s: "
                             "expected '%s', got '%s'" %
                             (transaction_id,
                              expected.file_name,
                              got.file_name))

            self.assertEqual(expected.file_hash, got.file_hash,
                             "Unexpected file hash entry for transaction %s: "
                             "expected '%s', got '%s'" %
                             (transaction_id,
                              expected.file_hash,
                              got.file_hash))

            exp_src_file = _file_part(expected.source_file)
            got_src_file = _file_part(got.source_file)

            self.assertEqual(exp_src_file, got_src_file,
                             "Unexpected source file for transaction: %s: "
                             "expected '%s'. got '%s'" %
                             (transaction_id, exp_src_file, got_src_file))

            self.assertEqual(expected.open().read(),
                             got.open().read(),
                             "Unexpected contents for %s/%s" %
                             (expected.file_name, expected.file_hash))

    def _assert_transaction_metadata(self, expected, got, modify_timestamp):
        for attrname in ["id", "type", "ref", "product", "version", "comment"]:
            exp_attr = getattr(expected, attrname)
            got_attr = getattr(got, attrname)
            self.assertEqual(exp_attr, got_attr,
                             "Missmatching transaction attribute %s, "
                             "expected '%s', got '%s'" %
                             (attrname, exp_attr, got_attr))

        self.assertLessEqual(expected.timestamp, got.timestamp,
                             "too early transaction time stamp")

        self.assertLessEqual(got.timestamp, modify_timestamp,
                             "too late transaction time stamp")

    def _assert_transaction(self, expected, got, modify_timestamp):
        self._assert_transaction_metadata(expected, got, modify_timestamp)

        expected_entries = expected.entries
        got_entries = got.entries

        self.assertEqual(len(expected_entries), len(got_entries),
                         "Unexpected number of entries in transaction %s: "
                         "expected %s entries , got %s entries" %
                         (expected.id,
                          len(expected_entries),
                          len(got_entries)))
        for exp_entry, got_entry in zip(expected_entries, got_entries):
            self._assert_transaction_entry(expected.id, exp_entry, got_entry)

    def _assert_modify_timestamp(self, modify_timestamp):
        """
        Assert that the symstore's modify timestamp have been updated recently.

        Use the timestamp recorded at the start of the test, and make sure
        that modify timestamp is from same or later time point.
        """
        self.assertGreaterEqual(modify_timestamp,
                                self.start_timestamp,
                                "Modify timestamp from the past")

    def _assert_history(self, expected, got, modify_timestamp):
        expected_len = len(expected)
        got_len = len(got)
        self.assertEqual(expected_len, got_len,
                         "Unexpected number of history entries, "
                         "expected %s, got %s" % (expected_len, got_len))

        for exp_entry, got_entry in zip(expected, got):
            self._assert_transaction_metadata(exp_entry,
                                              got_entry,
                                              modify_timestamp)

    def _assert_transactions(self, expected, got, modify_timestamp):
        expected_items = expected.items()
        got_items = got.items()

        expected_len = len(expected_items)
        got_len = len(got_items)

        self.assertEqual(expected_len, got_len,
                         "Unexpected number of transactions, "
                         "expected %s, got %s" % (expected_len, got_len))

        for (exp_id, exp_tr), (got_id, got_tr) in zip(expected_items,
                                                      got_items):
            self.assertEqual(exp_id, got_id,
                             "Unexpected transaction id, "
                             "expected '%s', got '%s'" % (exp_id, got_id))
            self._assert_transaction(exp_tr, got_tr, modify_timestamp)

    def _assert_next_transaction_id(self, expected_store, generated_store):
        expected_id = expected_store._next_transaction_id()
        got_id = generated_store._next_transaction_id()

        self.assertEqual(expected_id, got_id,
                         "Unexpected next transaction ID, "
                         "expected '%s', got '%s'" % (expected_id, got_id))

    def assertSymstoreDir(self, expected_dir_zip):
        expected_store = ZipSymstore(path.join(SYMFILES_DIR,
                                               expected_dir_zip))
        generated_store = symstore.Store(self.symstore_path)

        self._assert_transactions(expected_store.transactions,
                                  generated_store.transactions,
                                  generated_store.modify_timestamp)

        self._assert_history(expected_store.history,
                             generated_store.history,
                             generated_store.modify_timestamp)

        self._assert_modify_timestamp(generated_store.modify_timestamp)

        self._assert_next_transaction_id(expected_store, generated_store)
