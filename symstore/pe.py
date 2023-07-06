import os
import struct
from symstore import errs
from symstore import fileio

PE_SIGNATURE = b"PE\0\0"
PE_SIGNATURE_POINTER = 0x3C

PE_SIG_SIZE = 4
MACHINE_SIZE = 2
NUMBER_OF_SECTION_SIZE = 2
TIME_DATE_STAMP_SIZE = 4
POINTER_TO_SYMBOL_TABLE_SIZE = 4
NUMBER_OF_SYMBOLS_SIZE = 4
SIZE_OF_OPTIONAL_HEADER_SIZE = 2
CHARACTERISTICS_SIZE = 2

# TimeDateStamp field's offset relative to PE signature
TIME_DATE_STAMP_OFFSET = \
    PE_SIG_SIZE + \
    MACHINE_SIZE + \
    NUMBER_OF_SECTION_SIZE

# Optional header offset relative to PE signature
OPTIONAL_HEADER_OFFSET = \
    PE_SIG_SIZE + \
    MACHINE_SIZE + \
    NUMBER_OF_SECTION_SIZE + \
    TIME_DATE_STAMP_SIZE + \
    POINTER_TO_SYMBOL_TABLE_SIZE + \
    NUMBER_OF_SYMBOLS_SIZE + \
    SIZE_OF_OPTIONAL_HEADER_SIZE + \
    CHARACTERISTICS_SIZE

# SizeOfImage field's offset relative to optional header start
SIZE_OF_IMAGE_OFFSET = 56


class PESignatureNotFoundError(Exception):
    pass


class PEFormatError(errs.FileFormatError):
    format_name = "PE"


def _read_u32(file, size, offset):
    """
    Read 32-bit little-endian unsigned integer from an opened file.

    :param file: opended file handle
    :param size: file szie
    :param offset: the offset of the integer
    """
    if offset + 4 > size:
        raise PEFormatError("data offset %s beyond end of file %s" %
                            (offset, size))

    file.seek(offset)

    return struct.unpack("<I", file.read(4))[0]


class PEFile:
    """
    Simple PE file parser, that loads two fields used by symstore:

    * TimeDateStamp from file header
    * SizeOfImage from optional header

    The values are accessed by reading the object's member variables by
    the same name, e.g.

        PEFile("some.exe").TimeDateStamp

    :raises symstore.FileNotFoundError: if specified file does not exist
    """
    def __init__(self, filepath):
        with fileio.open_rb(filepath) as f:
            fsize = os.fstat(f.fileno()).st_size

            # load PE signature offset
            try:
                pe_sig_offset = _read_u32(f, fsize, PE_SIGNATURE_POINTER)
            except PEFormatError:
                raise PESignatureNotFoundError()

            # check that file contains valid PE signature
            f.seek(pe_sig_offset)
            if f.read(4) != PE_SIGNATURE:
                raise PESignatureNotFoundError()

            # load TimeDateStamp field
            self.TimeDateStamp = \
                _read_u32(f, fsize, pe_sig_offset+TIME_DATE_STAMP_OFFSET)

            # load SizeOfImage field
            self.SizeOfImage = _read_u32(f, fsize,
                                         pe_sig_offset +
                                         OPTIONAL_HEADER_OFFSET +
                                         SIZE_OF_IMAGE_OFFSET)
