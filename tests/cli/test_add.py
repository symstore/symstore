import unittest
import tempfile
import shutil
from os import path

from symstore import cab
from tests.cli import util


class TestNewStore(util.CliTester):
    """
    Test publishing files to a new symstore.
    """
    def setUp(self):
        self.recordStartTime()

        # set test's symstore path to a non-existing directory,
        # so that we can test code path that creates new symstore directory
        tmp_path = tempfile.mkdtemp()
        self.symstore_path = path.join(tmp_path, "empty")

    def tearDown(self):
        # make sure we remove created temp directory
        shutil.rmtree(path.dirname(self.symstore_path))

    def test_add_pdb(self):
        self.run_add_command(["--product-name", "dummyprod"],
                             ["bigage.pdb", "dummyprog.pdb"])

        self.assertSymstoreDir("new_store.zip")

    @unittest.skipIf(cab.compress is None, util.NO_COMP_SKIP)
    def test_add_compressed_pdb(self):
        self.run_add_command(["--compress", "--product-name", "dummyprod"],
                             ["dummyprog.pdb"])

        self.assertSymstoreDir("new_store_compressed.zip")


class TestExistingStore(util.CliTester):
    initial_dir_zip = "new_store.zip"

    def test_add_pdb(self):
        self.run_add_command(["--product-name", "dummylib"],
                             ["dummylib.pdb"])
        self.assertSymstoreDir("existing_store.zip")

    def test_republish(self):
        self.run_add_command(["--product-name", "dummyprod"],
                             ["dummyprog.pdb"])

        self.assertSymstoreDir("republished.zip")

    def test_special_pdb(self):
        # test adding two pdbs with following properties:
        #
        #  mono.pdb - root stream spans multiple pages
        #  vc140.pdb - no DBI stream
        self.run_add_command(["--product-name", "specpdbs"],
                             ["mono.pdb", "vc140.pdb"])
        self.assertSymstoreDir("special_pdbs.zip")

    def test_longroot(self):
        # test adding a pdb file with long root stream,
        # a root stream which need more then one page
        # to store it's indexes
        self.run_add_command(["--product-name", "longroot"],
                             ["longroot.pdb"])
        self.assertSymstoreDir("longroot_store.zip")


class TestSkipPublished(util.CliTester):
    """
    test adding new transaction with '--skip-published' flag enabled
    """
    initial_dir_zip = "new_store.zip"

    def test_skip(self):
        """
        test adding two files, where:

            dummyprog.pdb - is already published
            dummylib.dll - have not been published yet
        """
        self.run_add_command(
            ["--skip-published", "--product-name", "dummylib"],
            ["dummylib.dll", "dummyprog.pdb"])

        self.assertSymstoreDir("skip_republish.zip")

    def test_skip_no_new_files(self):
        """
        test adding one file that already have been published
        """
        retcode, stderr = util.run_script(self.symstore_path,
                                          ["dummyprog.pdb"],
                                          ["--skip-published"])

        # we should get an error message, as there is nothing new to publish
        self.assertEqual(retcode, 1)
        self.assertEqual(stderr.decode(), "no new files to publish\n")


class TestRepublishCompressed(util.CliTester):
    initial_dir_zip = "new_store_compressed.zip"

    @unittest.skipIf(cab.compress is None, util.NO_COMP_SKIP)
    def test_republish(self):
        self.run_add_command(["--compress", "--product-name", "dummyprod"],
                             ["dummyprog.pdb"])

        self.assertSymstoreDir("republished_compressed.zip")


class TestPublishPE(util.CliTester):
    initial_dir_zip = "existing_store.zip"

    def test_add_pdb(self):
        self.run_add_command(["--product-name", "peprods",
                              "--product-version", "1.0.1"],
                             ["dummylib.dll", "dummyprog.exe"])
        self.assertSymstoreDir("pe_store.zip")
