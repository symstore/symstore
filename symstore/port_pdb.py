"""
Simple parser that loads the 'PDB ID' from a portable PDB file.

Use `parse_pdb_id()` function to read the ID.

The general structure of portable PDB file format is defined in section
'II.24 Metadata physical layout' of the ECMA-335 standard document.
See doc/ECMA-335_6th_edition_june_2012.pdf.

For '#Pdb' stream definition see:
https://github.com/dotnet/runtime/blob/v7.0.5/docs/design/specs/PortablePdb-Metadata.md#standalone-debugging-metadata
"""
import os
import struct

SIGNATURE = b"BSJB"
VERSION_LENGTH_OFFSET = 12


# raised if the file does not start with portable PDB magic bytes
class InvalidSignature(Exception):
    pass


# raised when no '#Pdb' stream is found
class NoPDBStreamFound(Exception):
    pass


# raised if we fail to parse stream header
class InvalidStreamHeader(Exception):
    pass


def _parse_stream_header(file):
    """
    read stream's offset and name from stream header.
    """
    # read 'Offset'
    (offset,) = struct.unpack("<I", file.read(4))

    # skip 'Size'
    file.seek(4, os.SEEK_CUR)

    # read stream's name
    name = b""
    for _ in range(8):
        name += file.read(4)
        if b"\x00" in name:
            return offset, name

    raise InvalidStreamHeader()


def _get_pdb_id(file, offset) -> str:
    file.seek(offset)

    d1, d2, d3, d4 = struct.unpack("<IHH8s", file.read(4 + 2 * 2 + 8))

    id_str = f"{d1:08x}{d2:04x}{d3:04x}{d4.hex()}"
    return id_str.upper()


def _find_pdb_stream_offset(file, num_streams):
    """
    parse stream headers until we find '#Pdb' stream
    """
    for _ in range(num_streams):
        offset, name = _parse_stream_header(file)
        if name.startswith(b"#Pdb"):
            return offset

    raise NoPDBStreamFound()


def _parse(file) -> str:
    """
    Parse portable PDB file header until we find offset to '#Pdb' stream.

    Read and return 'PDB ID' from '#Pdb' stream.
    """
    if file.read(4) != SIGNATURE:
        raise InvalidSignature("missing portable PDB signature")

    # read version length
    file.seek(VERSION_LENGTH_OFFSET)
    (version_len,) = struct.unpack("<I", file.read(4))

    # skip 'Version' and 'Flags'
    file.seek(version_len + 2, os.SEEK_CUR)

    # read number of streams available
    (num_streams,) = struct.unpack("<H", file.read(2))

    # find '#Pdb' stream offset
    pdb_stream_offset = _find_pdb_stream_offset(file, num_streams)

    # parse 'PDB ID' from '#Pdb' stream
    return _get_pdb_id(file, pdb_stream_offset)


def parse_pdb_id(fname: str) -> str:
    """
    Read 'PDB ID' field from portable PDB file 'fname'.
    """
    with open(fname, "rb") as f:
        return _parse(f)
