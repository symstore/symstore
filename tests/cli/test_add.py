from os import path
import tempfile
import shutil
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
                             ["dummyprog.pdb"])
        self.assertSymstoreDir("new_store.zip")


class TestExistingStore(util.CliTester):
    initial_dir_zip = "new_store.zip"

    def test_add_pdb(self):
        self.run_add_command(["--product-name", "dummylib"],
                             ["dummylib.pdb"])
        self.assertSymstoreDir("existing_store.zip")


class TestPublishPE(util.CliTester):
    initial_dir_zip = "existing_store.zip"

    def test_add_pdb(self):
        self.run_add_command(["--product-name", "peprods",
                              "--product-version", "1.0.1"],
                             ["dummyprog.exe", "dummylib.dll"])
        self.assertSymstoreDir("pe_store.zip")
