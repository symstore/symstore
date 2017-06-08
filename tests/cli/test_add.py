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

    @unittest.skipIf(not cab.compression_supported, util.NO_COMP_SKIP)
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


class TestRepublishCompressed(util.CliTester):
    initial_dir_zip = "new_store_compressed.zip"

    @unittest.skipIf(not cab.compression_supported, util.NO_COMP_SKIP)
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
