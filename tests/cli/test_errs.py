import unittest
from tests.cli import util


class TestInvalidPEFile(unittest.TestCase):
    def assertInvalidPEMsg(self, retcode, msg, type, filename):
        self.assertEqual(retcode, 1)
        self.assertRegexpMatches(msg.decode(),
                                 ".*%s: invalid %s file:.*\n" %
                                 (filename, type), "unexpected error message")

    def test_empty_exe(self):
        """
        will hit 'reading beyoned end of file error"
        """
        retcode, stderr = util.run_script("dummy", ["empty.exe"])
        self.assertInvalidPEMsg(retcode, stderr, "PE", "empty.exe")

    def test_invalid_exe(self):
        retcode, stderr = util.run_script("dummy", ["invalid.exe"])
        self.assertInvalidPEMsg(retcode, stderr, "PE", "invalid.exe")

    def test_invalid_pdb(self):
        retcode, stderr = util.run_script("dummy", ["invalid.pdb"])
        self.assertInvalidPEMsg(retcode, stderr, "PDB", "invalid.pdb")
