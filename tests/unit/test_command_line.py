import mock
import unittest

from symstore import command_line


class TestMain(unittest.TestCase):
    """
    test main()
    """
    Z_ARGV = ["prog", "-z", "store_path", "file"]

    @mock.patch("symstore.cab.compression_supported", False)
    @mock.patch("sys.stderr")
    def test_compression_not_supported(self, stderr):
        with mock.patch("sys.argv", self.Z_ARGV):
            self.assertRaises(SystemExit, command_line.main)

        stderr.write.assert_called_once_with(
            "gcab module not available, compression not supported\n")
