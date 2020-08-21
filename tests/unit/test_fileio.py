import os
import tempfile
import shutil
from os import path
from tests import testcase
from symstore import fileio
from symstore import FileNotFound


class TestOpenRb(testcase.TestCase):
    """
    test fileio.open_rb() function
    """
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_file_not_found(self):
        """
        test the case when file we want to open does not exist
        """
        file_path = path.join(self.temp_dir, "foo")

        with self.assertRaises(FileNotFound) as cm:
            fileio.open_rb(file_path)

        # check that exception have correct filename assigned
        self.assertEqual(cm.exception.filename, file_path)

    def test_other_error(self):
        """
        test the case when get an error 'unexpected' error,
        and error which we don't explicitly handle
        """
        dir_path = path.join(self.temp_dir, "bar")
        os.mkdir(dir_path)

        self.assertRaisesRegex(IOError, ".*Is a directory",
                               fileio.open_rb, dir_path)
