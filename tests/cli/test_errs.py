from os import path
from tests.cli import util
from tests import testcase

SYMSTORE_PATH = "dummy"


class TestInvalidPEFile(testcase.TestCase):
    def assertInvalidPEMsg(self, retcode, msg, type, filename):
        self.assertEqual(retcode, 1)
        self.assertRegex(msg.decode(),
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


class TestUnknownExtension(testcase.TestCase):
    def assertErrorMsg(self, retcode, stderr, filename, msg):
        self.assertEqual(retcode, 1)
        self.assertRegex(stderr.decode(),
                         ".*%s: %s, can't figure out file format%s" %
                         (filename, msg, util.line_end()),
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


class TestFileNotFound(testcase.TestCase):
    PDB_FILE = "noexist.pdb"
    PE_FILE = "noexist.exe"

    def test_pdb_not_found(self):
        # full path to our non-existing file
        pdb_path = path.join(util.SYMFILES_DIR, self.PDB_FILE)
        # make sure file don't exist
        self.assertFalse(path.exists(pdb_path))

        # run the script, and check that we get proper error message
        retcode, stderr = util.run_script(SYMSTORE_PATH, [self.PDB_FILE])
        self.assertEqual(retcode, 1)
        self.assertRegex(stderr.decode(), "No such file: %s" % pdb_path)

    def test_pe_not_found(self):
        # full path to our non-existing file
        exe_path = path.join(util.SYMFILES_DIR, self.PE_FILE)
        # make sure file don't exist
        self.assertFalse(path.exists(exe_path))

        # run the script, and check that we get proper error message
        retcode, stderr = util.run_script(SYMSTORE_PATH, [self.PE_FILE])
        self.assertEqual(retcode, 1)
        self.assertRegex(stderr.decode(), "No such file: %s" % exe_path)
