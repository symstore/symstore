import unittest
import tempfile
import shutil
from os import path

import symstore
from tests.cli import util


class TestOpenCompressedEntry(unittest.TestCase):
    """
    test trying to open an compressed transaction entry's data
    """
    def setUp(self):
        """
        set-up a new symstore with one compressed transaction
        """
        empty_dir = path.join(tempfile.mkdtemp(), "empty")
        self.symstore = symstore.Store(empty_dir)

        transaction = self.symstore.new_transaction("prod", "0.0.0")
        transaction.add_file(path.join(util.SYMFILES_DIR, "dummylib.pdb"),
                             compress=True)

        self.symstore.commit(transaction)

    def tearDown(self):
        # make sure we remove created temp directory
        shutil.rmtree(path.dirname(self.symstore._path))

    def test_open(self):
        """
        check that trying to open a compressed entry raises
        not impelemted exception
        """
        transactions = list(self.symstore.transactions.items())
        entry = transactions[0][1].entries[0]
        self.assertRaisesRegexp(NotImplementedError,
                                "reading compressed data not supported",
                                entry.open)
