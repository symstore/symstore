import unittest
from tests.cli import util

SYMSTORE_PATH = "dummy"


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
        retcode, stderr = util.run_script(SYMSTORE_PATH, ["empty.exe"])
        self.assertInvalidPEMsg(retcode, stderr, "PE", "empty.exe")

    def test_invalid_exe(self):
        retcode, stderr = util.run_script(SYMSTORE_PATH, ["invalid.exe"])
        self.assertInvalidPEMsg(retcode, stderr, "PE", "invalid.exe")

    def test_invalid_pdb(self):
        retcode, stderr = util.run_script(SYMSTORE_PATH, ["invalid.pdb"])
        self.assertInvalidPEMsg(retcode, stderr, "PDB", "invalid.pdb")


class TestUnknownExtension(unittest.TestCase):
    def assertErrorMsg(self, retcode, stderr, filename, msg):
        self.assertEqual(retcode, 1)
        self.assertRegexpMatches(stderr.decode(),
                                 ".*%s: %s, can't figure out file format\n" %
                                 (filename, msg),
                                 "unexpected error message")

    def test_no_extension(self):
        filename = "no_extension"
        retcode, stderr = util.run_script(SYMSTORE_PATH, [filename])
        self.assertErrorMsg(retcode, stderr, filename,
                            "no file extension")

    def test_unknown_extension(self):
        filename = "unknown.ext"
        retcode, stderr = util.run_script(SYMSTORE_PATH, [filename])
        self.assertErrorMsg(retcode, stderr, filename,
                            "unknown file extension 'ext'")
