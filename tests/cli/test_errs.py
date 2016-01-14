import unittest
from tests.cli import util


class TestInvalidPEFile(unittest.TestCase):
    def assertInvalidPEMsg(self, retcode, msg, filename):
        self.assertEqual(retcode, 1)
        self.assertRegexpMatches(msg,
                                 ".*%s: invalid PE file\n" % filename,
                                 "unexpected error message")

    def test_empty_exe(self):
        """
        will hit 'reading beyoned end of file error"
        """
        retcode, stderr = util.run_script("dummy", ["empty.exe"])
        self.assertInvalidPEMsg(retcode, stderr, "empty.exe")

    def test_invalid_exe(self):
        retcode, stderr = util.run_script("dummy", ["invalid.exe"])
        self.assertInvalidPEMsg(retcode, stderr, "invalid.exe")
