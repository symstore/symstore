import io
import struct

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


class PEFile:
    """
    Simple PE file parser, that loads two fields used by symstore:

    * TimeDateStamp from file header
    * SizeOfImage from optional header

    The values are accessed by reading the object's member variables by
    the same name, e.g.

        PEFile("some.exe").TimeDateStamp
    """
    def __init__(self, filepath):
        with io.open(filepath, "rb") as f:
            f.seek(PE_SIGNATURE_POINTER)

            # load PE signature offset
            pe_sig_offset, = struct.unpack("<i", f.read(4))

            # check that file contains valid PE signature
            f.seek(pe_sig_offset)
            if f.read(4) != PE_SIGNATURE:
                raise ValueError("PE signature not found")

            # load TimeDateStamp field
            f.seek(pe_sig_offset+TIME_DATE_STAMP_OFFSET)
            self.TimeDateStamp, = struct.unpack("<i", f.read(4))

            # load SizeOfImage field
            f.seek(pe_sig_offset +
                   OPTIONAL_HEADER_OFFSET +
                   SIZE_OF_IMAGE_OFFSET)
            self.SizeOfImage, = struct.unpack("<i", f.read(4))
