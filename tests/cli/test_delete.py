from tests.cli import util


class TestDelete(util.CliTester):
    initial_dir_zip = "syms.zip"

    def test_delete(self):
        """
        test deleting a transaction from symstore
        """

        #
        # delete transactions and after each operation
        # check that resulting symstore looks as expected
        #

        self.run_add_command(["--delete", "0000000001"], [])
        self.assertSymstoreDir("syms-del1.zip")

        self.run_add_command(["--delete", "0000000003"], [])
        self.assertSymstoreDir("syms-del3.zip")

        self.run_add_command(["--delete", "0000000002"], [])
        self.assertSymstoreDir("syms-del2.zip")
