import math
import os
import struct
from symstore import fileio

SIGNATURE = b"Microsoft C/C++ MSF 7.00\r\n\x1ADS\0\0\0"
PORTABLE_SIGNATURE = b"BSJB"


class PDBInvalidSignature(Exception):
    pass


class PDBMissingStream(Exception):
    pass


def pages(size, page_size):
    """
    calculate number of pages that are required to store the specified
    number of bytes

    :param size: number of bytes
    :param page_size: page size
    """
    return int(math.ceil(float(size)/page_size))


class Root:
    """
    A bare bones abstraction of the root stream of an PDB files. Provides
    methods to read raw chunks of the root stream, as well as accessing
    data about streams containing streams.
    """
    def __init__(self, fp, page_size, size):
        self.fp = fp
        self.page_size = page_size
        self.size = size
        self._pages_idx = None

    def _load_pages(self):
        """
        get page numbers used by the root stream
        """
        num_pages = pages(self.size, self.page_size)

        # root stream indexes starts 5 int pointers after the signature
        self.fp.seek(len(SIGNATURE) + 4*5)
        num_root_index_pages = pages(num_pages * 4, self.page_size)

        root_index_pages = struct.unpack(
            "<%sI" % num_root_index_pages,
            self.fp.read(4*num_root_index_pages))

        # read in the root page list
        root_page_data = b""
        for root_index in root_index_pages:
            self.fp.seek(root_index * self.page_size)
            root_page_data += self.fp.read(self.page_size)

        page_list_fmt = "<" + ("%dI" % num_pages)
        return struct.unpack(page_list_fmt, root_page_data[:num_pages*4])

    def _pages(self):
        if self._pages_idx is None:
            self._pages_idx = self._load_pages()

        return self._pages_idx

    def _seek(self, page, byte):
        """
        move the root stream to a new position

        :param page: move to this page
        :param byte: move to the offset in the specified page
        """
        offset = self._pages()[page] * self.page_size + byte
        self.fp.seek(offset)

    def read(self, start, length):
        """
        read root stream bytes

        :param start: the global offset where to read
        :param length: number of bytes to read

        :return: root bytes as an bytes array
        """

        start_page = start // self.page_size
        start_byte = start % self.page_size

        self._seek(start_page, start_byte)

        partial_size = min(length, self.page_size - start_byte)
        result = self.fp.read(partial_size)
        length -= partial_size
        while 0 < length:
            start_page += 1
            self._seek(start_page, 0)
            partial_size = min(self.page_size, length)
            result += self.fp.read(partial_size)
            length -= partial_size
        return result

    def num_streams(self):
        """
        get number of streams listed in this root stream
        :return:
        """
        return struct.unpack("<I", self.read(0, 4))[0]

    def stream_size(self, stream_index):
        """
        get stream's size in bytes
        """
        if stream_index >= self.num_streams():
            raise IndexError("stream index to large")

        return struct.unpack("<I", self.read(stream_index * 4 + 4, 4))[0]

    def stream_pages(self, stream_index):
        """
        get stream's page numbers
        """
        num_streams = self.num_streams()

        pages_offset = 4 + 4 * num_streams

        for sidx in range(stream_index):
            stream_size = self.stream_size(sidx)
            stream_num_pages = pages(stream_size, self.page_size)
            pages_offset += stream_num_pages * 4

        num_pages = pages(self.stream_size(stream_index),
                          self.page_size)

        return struct.unpack("<%dI" % num_pages,
                             self.read(pages_offset, 4*num_pages))


class GUID:
    """
    Represents Globally Unique Identifier (GUID). The value is accessable
    via 4 data fields with sizes below:

        data1 - 32bit integer
        data2 - 16bit integer
        data3 - 16bit integer
        data4 - 64bit as byte array

    This object can also be converted to a hexidecimal string representation.
    """
    def __init__(self, data1, data2, data3, data4):
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.data4 = data4

    def __str__(self):
        data4_str = self.data4.hex().upper()

        return "%.8X%.4X%.4X%s" % \
               (self.data1, self.data2, self.data3, data4_str)


class PDBFile:
    """
    Simple PDB (program database) file parser the loads files GUID and Age
    fields.

    The GUID and Age values are accessible as following object members:

        guid - PDB file's GUID as an instance of GUID class
        age  - PDB file's Age, as an integer

    :raises symstore.FileNotFoundError: if specified file does not exist
    """
    def __init__(self, filepath):
        with fileio.open_rb(filepath) as f:

            # Check signature
            sig = f.read(len(SIGNATURE))
            if sig == SIGNATURE:
                self._read_pdb(f)
            else:
                f.seek(0)
                sig = f.read(len(PORTABLE_SIGNATURE))
                if sig == PORTABLE_SIGNATURE:
                    self._read_portable_pdb(f)
                else:
                    raise PDBInvalidSignature()

    def _read_pdb(self, f):
            # load page size and root stream definition
            page_size, _, _, root_dir_size, _ = \
                struct.unpack("<IIIII", f.read(4*5))

            # Create Root stream parser
            root = Root(f, page_size, root_dir_size)

            # load the PDB stream page
            pdb_stream_pages = root.stream_pages(1)

            # load GUID from PDB stream
            f.seek(pdb_stream_pages[0]*page_size)
            _, _, _, guid_d1, guid_d2, guid_d3, guid_d4 = \
                struct.unpack("<IIIIHH8s", f.read(4*4 + 2 * 2 + 8))

            # load age from the DBI information
            # (PDB information age changes when using PDBSTR)
            dbi_stream_pages = root.stream_pages(3)
            if 0 < len(dbi_stream_pages):
                f.seek(dbi_stream_pages[0]*page_size)
                _, _, age = struct.unpack("<III", f.read(3*4))
                # Regular PDB age parameters use lowercase hex for the signature, unlike portable PDBs
                age_str = "%x" % age
            else:
                # vc140.pdb however, does not have this stream,
                # so it does not have an age that can be used
                # in the hash string
                age = None
                # according to symstore.exe we should just
                # skip adding the age to the hash string
                age_str = ""

            # store GUID and age for user friendly retrieval
            self.guid = GUID(guid_d1, guid_d2, guid_d3, guid_d4)
            self.age = age
            self.age_str = age_str

    def _read_portable_pdb(self, pdb_file):
        # Documented in https://www.ecma-international.org/wp-content/uploads/ECMA-335_2nd_edition_december_2002.pdf
        # See partition II, chapter 23 for details
        # Seek past the MinorVersion and MajorVersion, which are hardcoded to 1 and ignored
        pdb_file.seek(8, os.SEEK_CUR)
        version_length, = struct.unpack("<I", pdb_file.read(4))
        # Stream data starts after version and then the 2-byte Flags field (which is ignored)
        pdb_file.seek(version_length + 2, os.SEEK_CUR)
        num_streams, = struct.unpack("<H", pdb_file.read(2))

        for stream_index in range(num_streams):
            # Offset is relative to the start of the file header (so absolute for  pdb_file, where the header is at
            # the start)
            offset, _size = struct.unpack("<II", pdb_file.read(8))
            stream_name = b""
            while True:
                # Names are aligned to closest 4 bytes, so read 4 byte blocks until we find a terminating NUL
                block = pdb_file.read(4)
                terminator_index = block.find(b"\x00")
                if terminator_index == -1:
                    stream_name += block
                else:
                    stream_name += block[:terminator_index]
                    break

            stream_name = stream_name.decode("utf-8")
            if stream_name == "#Pdb":
                # "#Pdb" stream is documented here:
                # https://github.com/dotnet/runtime/blob/v7.0.5/docs/design/specs/PortablePdb-Metadata.md#standalone-debugging-metadata
                pdb_file.seek(offset, os.SEEK_SET)
                guid_d1, guid_d2, guid_d3, guid_d4 = struct.unpack("<IHH8s", pdb_file.read(4 + 2 * 2 + 8))
                self.guid = GUID(guid_d1, guid_d2, guid_d3, guid_d4)
                # Timestamp is hardcoded to FFFFFFFF in Portable PDBs, so ignore the one encoded in the header, per:
                # https://github.com/dotnet/symstore/blob/9c9ef5d6c845826e433f70a29f4d80bf7108e451/docs/specs/SSQP_Key_Conventions.md#portable-pdb-signature
                self.age = 0xFFFFFFFF
                # Portable PDB age parameters use uppercase hex for the signature, unlike regular PDBs
                self.age_str = "%X" % self.age
                return

        raise PDBMissingStream()
