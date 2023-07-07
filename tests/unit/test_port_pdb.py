from typing import List
import os
import struct
import tempfile
from tests import testcase
from symstore import port_pdb


def _make_pdb(filename: str, stream_names: List[bytes]):
    with open(filename, "wb") as f:
        # Signature
        f.write(port_pdb.SIGNATURE)

        # MajorVersion, MinorVersion, Reserved
        f.write(b"\x01\x00\x01\x00\x00\x00\x00\x00")

        # Version length, Version string
        f.write(b"\x0c\x00\x00\x00PDB v1.0\x00\x00\x00\x00")

        # Flags
        f.write(b"\x00\x00")

        # Number of Streams
        f.write(struct.pack("<H", len(stream_names)))

        for stream_name in stream_names:
            # (dummy) stream offset and size
            f.write(b"\x10\x00\x00\x00\x20\x00\x00\x00")
            # stream name
            f.write(stream_name)


class TestCurruptPDB(testcase.TestCase):
    def setUp(self):
        fd, self.temp_file = tempfile.mkstemp()
        os.close(fd)

    def tearDown(self):
        os.remove(self.temp_file)

    def test_missing_pdb_stream(self):
        """
        test the case where '#Pdb' stream is not found
        """
        _make_pdb(self.temp_file, [b"#Strings\x00\x00\x00\x00", b"#~\x00\x00"])
        with self.assertRaises(port_pdb.NoPDBStreamFound):
            port_pdb.parse_pdb_id(self.temp_file)

    def test_invalid_stream_header(self):
        """
        test the case where we have currupt stream header
        """
        # create PDB file, where one stream header is missing null termination in it's name
        _make_pdb(self.temp_file, [b"#Strings\x00\x00\x00\x00", b"#~"])
        with self.assertRaises(port_pdb.InvalidStreamHeader):
            port_pdb.parse_pdb_id(self.temp_file)
