import unittest
import tempfile
import shutil
from os import path

import symstore

DATA_DIR = path.join(path.dirname(path.abspath(__file__)), "data")


class MockHistStore:
    def __init__(self, history_file):
        self._history_file = history_file


class TestHistoryAdd(unittest.TestCase):
    """
    test History.add() method
    """
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _init_hist_file(self, histfile_name):
        """
        copy history file to temporary directory
        """
        src = path.join(DATA_DIR, histfile_name)
        dest = path.join(self.temp_dir, "history.txt")

        shutil.copyfile(src, dest)

        return dest

    def assertFileContents(self, file_path, content):
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), content)

    def test_new_file(self):
        """
        test adding new trasaction line to an empty (non-existing) file
        """
        store = MockHistStore(path.join(self.temp_dir, "history.txt"))
        history = symstore.History(store)

        history.add("new_line")

        self.assertFileContents(store._history_file,
                                "new_line")

    def test_no_newline(self):
        """
        test adding new trasaction line to a history file
        without newline character at the end
        """
        store = MockHistStore(self._init_hist_file("no_newline.txt"))
        history = symstore.History(store)

        history.add("new_line")

        self.assertFileContents(store._history_file,
                                "original_line\nnew_line")

    def test_trailing_newline(self):
        """
        test adding new trasaction line to a history file
        with trailing newline character
        """
        store = MockHistStore(self._init_hist_file("trailing_newline.txt"))
        history = symstore.History(store)

        history.add("new_line")

        self.assertFileContents(store._history_file,
                                "original_line\nnew_line")
