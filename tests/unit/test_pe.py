from os import path
from unittest.mock import Mock
from tests import testcase
from tests.cli import util
from symstore import pe
from symstore.symstore import _pe_hash


# expected PE fields values
TIME_DATE_STAMP = 0xE914506E
SIZE_OF_IMAGE = 0xA000


class TestPE(testcase.TestCase):
    def test_fields(self):
        """
        test that we can correctly read TimeDateStamp and SizeOfImage fields
        from a PE file

        in particular, check that large TimeDateStamp are correctly read as
        unsigned integers, and don't become negative values
        """
        # parse the PE file
        pefile = pe.PEFile(path.join(util.SYMFILES_DIR, "u32_test.dll"))

        # check that we got expected values
        self.assertEqual(pefile.TimeDateStamp, TIME_DATE_STAMP)
        self.assertEqual(pefile.SizeOfImage, SIZE_OF_IMAGE)


def _make_pe_mock(time_date_stamp, size_of_image):
    pe = Mock()
    pe.TimeDateStamp = time_date_stamp
    pe.SizeOfImage = size_of_image

    return pe


class TestPEHash(testcase.TestCase):
    def test_hash(self):
        pe_hash = _pe_hash(_make_pe_mock(1444402430, 32768))
        self.assertEqual("5617D4FE8000", pe_hash)

    def test_hash_lowcase(self):
        """
        get hash of an PE file,
        where the 'size of image' contains a letter in hex,
        thus we can check that the part of the hash is in lower case
        """
        pe_hash = _pe_hash(_make_pe_mock(1520452531, 512000))
        self.assertEqual("5AA043B37d000", pe_hash)

    def test_low_values_padding(self):
        """
        Test that low time stamp and size value are correctly
        prefixed with 0.

        The time stamp part should always be 8 chars long,
        the size 4 chars long.
        """
        pe_hash = _pe_hash(_make_pe_mock(77794544, 2048))
        self.assertEqual("04A30CF00800", pe_hash)
