import mock
import unittest

from symstore import command_line, CabCompressionError


class TestMain(unittest.TestCase):
    """
    test main()
    """
    ERROR_MSG = "cab dummy"
    Z_ARGV = ["prog", "-z", "store_path", "file.pdb"]

    @mock.patch("symstore.cab.compress", None)
    @mock.patch("sys.stderr")
    def test_compression_not_supported(self, stderr):
        with mock.patch("sys.argv", self.Z_ARGV):
            self.assertRaises(SystemExit, command_line.main)

        stderr.write.assert_called_once_with(
            "gcab module not available, compression not supported\n")

    @mock.patch("symstore.cab.compress", True)
    @mock.patch("symstore.Store")
    @mock.patch("sys.stderr")
    def test_cab_error(self, stderr, store_mock):
        store_obj = store_mock.return_value
        store_obj.new_transaction.side_effect = \
            CabCompressionError(self.ERROR_MSG)

        with mock.patch("sys.argv", self.Z_ARGV):
            self.assertRaises(SystemExit, command_line.main)

        stderr.write.assert_called_once_with(
            "Error creating CAB\ncab dummy\n")
