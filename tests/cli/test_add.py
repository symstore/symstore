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

    def test_add_with_comment(self):
        self.run_add_command(["--product-name", "dummyprod",
                              "--comment", "a comment"],
                             ["dummyprog.pdb"])

        self.assertSymstoreDir("comment_store.zip")

    @unittest.skipIf(cab.compress is None, util.NO_COMP_SKIP)
    def test_add_compressed_pdb(self):
        self.run_add_command(["--compress", "--product-name", "dummyprod"],
                             ["dummyprog.pdb"])

        self.assertSymstoreDir("new_store_compressed.zip")

    @unittest.skipIf(cab.compress is None, util.NO_COMP_SKIP)
    def test_add_max_compress(self):
        self.run_add_command(["--compress", "--max-compress", "5000"],
                             ["dummylib.dll", "dummylib.pdb", "dummyprog.exe"])

        self.assertSymstoreDir("max_compress.zip")


class TestDotNetFiles(util.CliTester):
    """
    Test publishing .NET binaries.

    Most notably the *.pdb here are in 'Portable PDB' format,
    i.e. a different format compared to (old) 'native PDB' format.
    """
    def test_add(self):
        self.run_add_command(["--product-name", "prod"],
                             ["cli_app_net.exe", "cli_app_net.dll", "cli_app_net.pdb",
                              "cli_lib_net.pdb", "gui_app_net.pdb"])

        self.assertSymstoreDir("netsyms.zip")


class TestAlternativeExtensions(util.CliTester):
    """
    Test the case when files have non-standard extensions.

    For example, some common file extensions can be:

      scr : Screensaver (PE/EXE file format)
      sys : Driver (PE/DLL file format)

    for more details: https://github.com/symstore/symstore/issues/20
    """

    RENAMED_FILES = [
        ("dummyprog.exe", "dummyprog.src"),
        ("dummylib.dll", "dummylib.sys"),
        ("dummyprog.pdb", "dummyprog.hej")
    ]

    def setUp(self):
        self.recordStartTime()

        # create new, initially empty, symbols store
        tmp_path = tempfile.mkdtemp()
        self.symstore_path = path.join(tmp_path, "renamed")

        # create some files with alternative extensions,
        # by copying existing test files to a temp directory
        # with new names
        self.renamed_files_dir = tempfile.mkdtemp()
        for src, dest in self.RENAMED_FILES:
            shutil.copyfile(util.symfile_path(src),
                            path.join(self.renamed_files_dir, dest))

    def tearDown(self):
        # make sure we remove created temp directories
        shutil.rmtree(path.dirname(self.symstore_path))
        shutil.rmtree(self.renamed_files_dir)

    def test_publish(self):
        files = [f for _, f in self.RENAMED_FILES]
        retcode, stderr = util.run_script(self.symstore_path, files,
                                          symfiles_dir=self.renamed_files_dir)
        self.assertEqual(retcode, 0)
        self.assertEqual(stderr, b"")

        self.assertSymstoreDir("renamed.zip")


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
