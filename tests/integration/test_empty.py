from os import path
import shutil
import unittest
import tempfile
import symstore


class TestEmpty(unittest.TestCase):
    """
    Test reading history and transactions from an empty
    symstore.
    """
    def setUp(self):
        empty_dir = path.join(tempfile.mkdtemp(), "empty")
        self.symstore = symstore.Store(empty_dir)

    def tearDown(self):
        shutil.rmtree(path.dirname(self.symstore._path))

    def test_history(self):
        self.assertEqual(len(self.symstore.history), 0)

    def test_transactions(self):
        self.assertEqual(list(self.symstore.transactions.items()), [])

    def test_transactions_caching(self):
        """
        Test the transaction parsing caching code path.

        Getting transaction items twice in a row should give same
        results, and second request should be fetched from the cache.
        """
        first = self.symstore.transactions.items()
        second = self.symstore.transactions.items()
        self.assertEqual(first, second)
