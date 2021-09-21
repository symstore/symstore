from os import path
from tests.cli import util
from tests import testcase

SYMSTORE_PATH = "dummy"


class TestInvalidPEFile(testcase.TestCase):
    def assertUnknownFileTypeMsg(self, retcode, msg, filename):
        self.assertEqual(retcode, 1)
        self.assertRegex(msg.decode(),
                         ".*%s: can't figure out file type" % filename,
                         "unexpected error message")

    def test_empty_exe(self):
        """
        will not find valid PE file signature
        """
        retcode, stderr = util.run_script(SYMSTORE_PATH, ["empty.exe"])
        self.assertUnknownFileTypeMsg(retcode, stderr, "empty.exe")

    def test_invalid_pdb(self):
        """
        will not find valid 'PDB file' signature
        """
        retcode, stderr = util.run_script(SYMSTORE_PATH, ["invalid.pdb"])
        self.assertUnknownFileTypeMsg(retcode, stderr, "invalid.pdb")

    def test_truncated_exe(self):
        """
        test adding a truncated PE file,

        a PE file that contains valid 'PE file' signaure part,
        but lacks the rest of the contents
        """
        retcode, stderr = util.run_script(SYMSTORE_PATH, ["truncated.exe"])

        self.assertEqual(retcode, 1)
        self.assertRegex(stderr.decode(),
                         ".*truncated.exe: invalid PE file:.*")


class TestTransactionNotFound(util.CliTester):
    initial_dir_zip = "existing_store.zip"

    def test_del_unknown_transaction(self):
        """
        test deleting non-existing transaction
        """
        retcode, stderr = util.run_script(SYMSTORE_PATH, [],
                                          ["--delete", "0000000042"])
        self.assertEqual(retcode, 1)
        self.assertRegex(stderr.decode(),
                         "no transaction with id '0000000042' found")


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
