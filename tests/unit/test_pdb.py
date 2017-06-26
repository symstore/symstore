import mock
import unittest
from symstore import pdb

NUM_STREAMS = 5


class TestRoot(unittest.TestCase):
    """
    test some methods in pdb.Root class
    """
    @mock.patch("symstore.pdb.Root.num_streams")
    def test_stream_size_index_err(self, num_streams):
        """
        test the case when stream_size() is invoked with to
        non-existant stream index
        """
        # mock that there is NUM_STREAMS available in the PDB file
        num_streams.return_value = NUM_STREAMS

        root = pdb.Root(None, None, None)
        self.assertRaisesRegexp(IndexError, "stream index to large",
                                root.stream_size, NUM_STREAMS+2)
